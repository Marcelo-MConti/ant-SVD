from types import FrameType
import argparse
import itertools

import gc

import os
import sys
import time
import signal
import shutil

from pathlib import Path

import numpy as np

import skvideo
import skvideo.io
import skvideo.utils

import skimage

from .svd import SVD_Decomposition
from .video import preprocess_chunk, postprocess_mask

from .utils import logging


def handle_timeout(_x: int, _f: FrameType | None):
    raise TimeoutError()


def main():
    parser = argparse.ArgumentParser(
        prog="ant-svd",
        description="Remove static background from a video",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-n", "--chunk-size",
        help="How many frames are processed per chunk",
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
        "-x", "--trace",
        help="Trace mode: do only the SVD decomposition of the first chunk and exit.",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "filename",
        help="Path to a video file to be processed",
        type=Path
    )

    args = parser.parse_args()

    CHUNK_SIZE_MIN = 15
    CHUNK_SIZE_MAX = 150

    if args.chunk_size < CHUNK_SIZE_MIN or args.chunk_size > CHUNK_SIZE_MAX:
        raise ValueError(f"Invalid value for chunk_size, must be between {CHUNK_SIZE_MIN} and {CHUNK_SIZE_MAX} frames")

    if args.transparent_color[:1] != "#":
        raise ValueError("Invalid value for transparent_color")

    r = int(args.transparent_color[1:3], base=16)
    g = int(args.transparent_color[3:5], base=16)
    b = int(args.transparent_color[5:7], base=16)

    trans_yuv = skimage.color.rgb2yuv(
        np.array([[[r, g, b]]], dtype=np.float64) / 255.0
    )[0, 0, :]

    filename: Path = args.filename

    metadata = skvideo.io.ffprobe(filename)
    frame_rate = metadata["video"]["@avg_frame_rate"]

    # Iterador dos frames do vídeo no formato YUV444P
    video_gen = skvideo.io.vreader(filename)

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
    rm_r("output/backgrounds")

    mkdir("output")
    mkdir("output/masks")
    mkdir("output/videos")
    mkdir("output/backgrounds")

    # Retorna um handle que pode ser usado para montar o vídeo de saída, frame a frame, no formato YUV444P
    video_out = skvideo.io.FFmpegWriter(
        f"output/videos/{os.path.basename(filename.stem)}.mp4",
        inputdict={
            "-r": frame_rate,
            "-hwaccel": "auto"
        },
        outputdict={
            "-vcodec": "libx264",
            "-crf": "10",
            "-preset": "slow"
        }
    )

    cur_chunk = 0

    if args.trace:
        signal.signal(signal.SIGUSR1, handle_timeout)

    for frames in itertools.batched(video_gen, args.chunk_size):
        (orig_height, orig_width, n_chan) = frames[0].shape

        frame_mat = preprocess_chunk(frames, height=args.height, width=args.width)

        if args.trace:
            del frames
            del video_gen

            gc.collect()

            try:
                print(":::", flush=True)
                time.sleep(100)
            except TimeoutError:
                pass

        print("---")
        t1 = time.clock_gettime(time.CLOCK_MONOTONIC)

        if args.use_builtin:
            u, s, vt = np.linalg.svd(frame_mat, full_matrices=False)
        else:
            u, s, vt = SVD_Decomposition(frame_mat)

        t2 = time.clock_gettime(time.CLOCK_MONOTONIC)
        print(f"T={t2 - t1}")
        print("+++")

        if args.trace:
            sys.exit(120)

        logging.log_singular_data(frame_mat, u, s, vt, out_dir="output")

        # Static elements matrix (similar to, but not quite a, background)
        sta_mat = np.zeros_like(frame_mat)

        for i in range(args.k):
            sta_mat += s[i] * np.outer(u[:, i], vt[i, :])

        # Dynamic elements matrix -> mask
        dyn_mat = np.abs(frame_mat - sta_mat)

        for i in range(len(frames)):
            # Process each frame mask
            mask = np.reshape(dyn_mat[:, i], (args.height, args.width))
            mask = postprocess_mask(mask, args.threshold, orig_height, orig_width)

            if args.write_masks:
                skimage.io.imsave(f"output/masks/{args.chunk_size * cur_chunk + i}.png", mask)

            masked_frame = np.zeros_like(frames[i])

            # Apply the mask to the frame to remove the background (elementwise multiplication)
            for j in range(n_chan):
                masked_frame[:, :, j] = frames[i][:, :, j] * mask

            # Invert the mask
            mask = 1 - mask

            # Replace the background color in the masked frame with args.transparent_color
            for j in range(n_chan):
                masked_frame[:, :, j] += (int(trans_yuv[j] * 255) * mask).astype(np.uint8)

            video_out.writeFrame(masked_frame)

            # NOTE: This has to come in last, because it trashes masked_frame and assumes the mask has already been inverted
            if args.write_background:
                for j in range(n_chan):
                    masked_frame[:, :, j] = frames[i][:, :, j] * mask

                skimage.io.imsave(f"output/backgrounds/{args.chunk_size * cur_chunk + i}.png", masked_frame)

        cur_chunk += 1

        if cur_chunk >= args.chunks:
            break

    video_out.close()


if __name__ == "__main__":
    main()
