from argparse import ArgumentParser

import itertools

import numpy as np
import skvideo
import skvideo.io

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
        "filename",
        help="Path to a video file to be processed"
    )

    args = parser.parse_args()

    if args.batch_size < 30 or args.batch_size > 60:
        raise ValueError("Invalid value for batch_size, must be between 30 and 60 frames")

    video_gen = skvideo.io.vreader(args.filename)

    for frames in itertools.batched(video_gen, args.batch_size):
        (height, width, n_chan) = frames[0].shape

        print(frames[0][:, :, 0])

        frame_mat = np.ndarray(shape=(height * width, args.batch_size))

        for (index, frame) in frames.enumerate():
            frame_mat[:, index] = frame

        # sigma, u, v = svd()
        # mask_mat = trunc(sigma, u, v, k)

        for index in range(args.batch_size):
            ...


if __name__ == "__main__":
    main()
