from argparse import ArgumentParser

import itertools

import numpy as np

import skvideo
import skvideo.io
import skvideo.utils

import skimage

from matplotlib import pyplot as plt


def main():
    parser = ArgumentParser(
        prog="ant-svd",
        description="Remove static background from a video"
    )

    parser.add_argument(
        "-b", "--batch-size",
        help="How many frames are processed per batch",
        type=int,
        default=60
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
        "-w", "--width",
        help="Width to use when processing the video file",
        type=int,
        default=200
    )

    parser.add_argument(
        "-h", "--height",
        help="Height to use when processing the video file",
        type=int,
        default=100
    )

    parser.add_argument(
        "-k",
        help="Number of "
    )

    parser.add_argument(
        "filename",
        help="Path to a video file to be processed"
    )

    args = parser.parse_args()

    if args.batch_size < 30 or args.batch_size > 60:
        raise ValueError("Invalid value for batch_size, must be between 30 and 60 frames")

    # Iterador dos frames do vídeo no formato YUV444P
    video_gen = skvideo.io.vreader(args.filename)

    for frames in itertools.batched(video_gen, args.batch_size):
        (height, width, n_chan) = frames[0].shape

        frame_mat = np.ndarray(shape=(height * width, args.batch_size))

        for (index, frame) in frames.enumerate():
            frame_mat[:, index] = frame

        if args.use_builtin:
            u, s, vt = np.linalg.svd(frame_mat)

            ...
        else:
            ...
            # u, s, vt = svd()
            # mask_mat = trunc(sigma, u, v, k)

            skimage.segmentation.flood()

        for index in range(args.batch_size):
            ...


if __name__ == "__main__":
    main()
