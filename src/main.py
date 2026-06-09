import argparse
import itertools

import os
import time
import shutil

import numpy as np

import skvideo
import skvideo.io
import skvideo.utils

import skimage

import scipy

from svd.manual_svd import SVD_decomposition, Cumulative_variance, Compute_rank


def main():
    parser = argparse.ArgumentParser(
        prog="ant-svd",
        description="Remove static background from a video",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-b", "--batch-size",
        help="How many frames are processed per batch",
        type=int,
        default=15
    )

    parser.add_argument(
        "-c", "--transparent-color",
        help="Color to replace transparent sections with",
        type=str,
        default="#ff60d0"
    )

    parser.add_argument(
        "-u", "--use-builtin",
        help="Use built-in library functions rather than our SVD implementation",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "-W", "--width",
        help="Width to use when processing the video file",
        type=int,
        default=120
    )

    parser.add_argument(
        "-H", "--height",
        help="Height to use when processing the video file",
        type=int,
        default=80
    )

    parser.add_argument(
        "-k",
        help="Number of singular values to keep to get the background",
        type=int,
        default=2
    )

    parser.add_argument(
        "-t", "--threshold",
        help="Threshold to use when quantizing the mask",
        type=float,
        default=0.2
    )

    parser.add_argument(
        "-M", "--write-masks",
        help="Write the masks used to remove the background to separate image files",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "-B", "--write-background",
        help="Write background images to a file",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "-C", "--chunks",
        help="Number of chunks to process",
        type=int,
        default=5
    )

    parser.add_argument(
        "filename",
        help="Path to a video file to be processed"
    )

    args = parser.parse_args()

    BATCH_MIN = 15
    BATCH_MAX = 60

    if args.batch_size < BATCH_MIN or args.batch_size > BATCH_MAX:
        raise ValueError(f"Invalid value for batch_size, must be between {BATCH_MIN} and {BATCH_MAX} frames")

    if args.transparent_color[:1] != "#":
        raise ValueError("Invalid value for transparent_color")

    r = int(args.transparent_color[1:3], base=16)
    g = int(args.transparent_color[3:5], base=16)
    b = int(args.transparent_color[5:7], base=16)

    trans_yuv = skimage.color.rgb2yuv(
        np.array([[[r, g, b]]], dtype=np.float64) / 255.0
    )[0, 0, :]

    # Iterador dos frames do vídeo no formato YUV444P
    video_gen = skvideo.io.vreader(args.filename)

    def rm_r(path):
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass

    def mkdir(path):
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

    rm_r("output/masks")
    rm_r("output/videos")
    rm_r("output/backgrounds")

    mkdir("output")
    mkdir("output/masks")
    mkdir("output/videos")
    mkdir("output/backgrounds")

    # Retorna um handle que pode ser usado para montar o vídeo de saída, frame a frame, no formato YUV444P
    video_out = skvideo.io.FFmpegWriter(f"output/videos/{os.path.basename(args.filename)}")

    cur_chunk = 0

    for frames in itertools.batched(video_gen, args.batch_size):
        batch_size = len(frames)
        (orig_height, orig_width, n_chan) = frames[0].shape

        frame_mat = np.ndarray(shape=(args.height * args.width, batch_size))

        for i in range(batch_size):
            # frames[i].shape = (height, width, n_chan)
            #
            # YUV444P has three channels: Y (luma), U (blue difference), V (green difference)
            # We only use the luma channel (0) when applying SVD
            frame_luma = frames[i][:, :, 0]
            frame_luma_resized = skimage.transform.resize(
                frame_luma,
                (args.height, args.width)
            )

            frame_mat[:, i] = np.reshape(frame_luma_resized / 255, args.height * args.width)
            print(f"Processed frame {i}")

        print("---")

        t1 = time.clock_gettime(time.CLOCK_MONOTONIC)

        if args.use_builtin:
            u, s, vt = np.linalg.svd(frame_mat)
        else:
            u, s, vt = SVD_decomposition(frame_mat)

        t2 = time.clock_gettime(time.CLOCK_MONOTONIC)

        print(f"T={t2 - t1}")

        print("+++")

        # Dynamic elements matrix -> mask
        dyn_mat = np.zeros_like(frame_mat)
        # Static elements matrix (similar to, but not quite a, background)
        sta_mat = np.zeros_like(frame_mat)

        with (
            open("output/singular.csv", "w") as csv_singular,
            open("output/cum_var.csv", "w") as csv_cum_var,
            open("output/rec_err.csv", "w") as csv_rec_err
        ):
            rank = Compute_rank(s)

            print("k,sigma_k", file=csv_singular)
            print("k,V_k", file=csv_cum_var)
            print("k,E_k", file=csv_rec_err)

            l = np.zeros_like(frame_mat)

            for i in range(batch_size):
                l += s[i] * np.outer(u[:, i], vt[i, :])

                if i == args.k - 1:
                    sta_mat = l.copy()

                print(f"{i + 1},{s[i]}", file=csv_singular)
                print(f"{i + 1},{Cumulative_variance(s, i + 1, rank)}", file=csv_cum_var)
                print(f"{i + 1},{np.linalg.norm(frame_mat - l, "fro")}", file=csv_rec_err)

        dyn_mat = np.abs(frame_mat - sta_mat)

        for i in range(batch_size):
            # Process each frame mask
            frame_mask = np.reshape(dyn_mat[:, i], (args.height, args.width))

            m = np.max(frame_mask)
            print(f"m={m}")
            bin_mask = np.round(frame_mask * (0.5 / args.threshold) / m)

            filled_mask = scipy.ndimage.binary_fill_holes(bin_mask)
            filled_mask_resized = skimage.transform.resize(filled_mask, (orig_height, orig_width))

            if args.write_masks:
                skimage.io.imsave(f"output/masks/{args.batch_size * cur_chunk + i}.png", filled_mask_resized)

            masked_frame = np.zeros_like(frames[i])

            # Convolve/Apply the mask to the frame to remove the background
            for j in range(n_chan):
                masked_frame[:, :, j] = frames[i][:, :, j] * filled_mask_resized

            # Invert the mask
            filled_mask_resized = 1 - filled_mask_resized

            # Replace the background color in the masked frame with args.transparent_color
            for j in range(n_chan):
                masked_frame[:, :, j] += (int(trans_yuv[j] * 255) * filled_mask_resized).astype(np.uint8)

            video_out.writeFrame(masked_frame)

            # NOTE: This has to come in last, because it trashes masked_frame and assumes the mask has already been inverted
            if args.write_background:
                for j in range(n_chan):
                    masked_frame[:, :, j] = frames[i][:, :, j] * filled_mask_resized

                skimage.io.imsave(f"output/backgrounds/{args.batch_size * cur_chunk + i}.png", masked_frame)

        cur_chunk += 1

        if cur_chunk > args.chunks:
            break

    video_out.close()


if __name__ == "__main__":
    main()
