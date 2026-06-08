from argparse import ArgumentParser

import itertools

import numpy as np

import skvideo
import skvideo.io
import skvideo.utils

import skimage

import scipy

from matplotlib import pyplot as plt

from svd.manual_svd import SVD_decomposition


def main():
    parser = ArgumentParser(
        prog="ant-svd",
        description="Remove static background from a video"
    )

    parser.add_argument(
        "-b", "--batch-size",
        help="How many frames are processed per batch",
        type=int,
        default=15
    )

    parser.add_argument(
        "-C", "--transparent-color",
        help="Color to replace transparent sections with (RGB hex format)",
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
        "filename",
        help="Path to a video file to be processed"
    )

    args = parser.parse_args()

    if args.batch_size < 15 or args.batch_size > 60:
        raise ValueError("Invalid value for batch_size, must be between 30 and 60 frames")

    # Iterador dos frames do vídeo no formato YUV444P
    video_gen = skvideo.io.vreader(args.filename)

    for frames in itertools.batched(video_gen, args.batch_size):
        # XXX: Recreating a matrix like this every time is expensive
        frame_mat = np.ndarray(shape=(args.height * args.width, args.batch_size))

        for i in range(args.batch_size):
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

        if args.use_builtin:
            u, s, vt = np.linalg.svd(frame_mat)
        else:
            u, s, vt = SVD_decomposition(frame_mat)

        print("+++")

        # Dynamic elements matrix -> mask
        dyn_mat = np.zeros_like(frame_mat)
        # Static elements matrix (similar to, but not quite a, background)
        sta_mat = np.zeros_like(frame_mat)

        for i in range(args.k):
            sta_mat += s[i] * np.outer(u[:, i], vt[i, :])

        dyn_mat = np.abs(frame_mat - sta_mat)

        for i in range(args.batch_size):
            # Process each frame mask
            frame_mask = np.reshape(dyn_mat[:, i], (args.height, args.width))

            m = np.max(frame_mask)
            print(f"m={m}")
            bin_mask = np.round(frame_mask / m + 0.3)

            filled_mask = scipy.ndimage.binary_fill_holes(bin_mask)

            plt.imshow(filled_mask, cmap="gray", vmax=1.)
        plt.show()


if __name__ == "__main__":
    main()
