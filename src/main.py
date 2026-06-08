from argparse import ArgumentParser

import numpy as np
import skvideo
import skvideo.io

def main():
    parser = ArgumentParser(
        prog="ant-svd",
        description="Remove static background from a video"
    )

    parser.add_argument("filename")
    args = parser.parse_args()

    video_gen = skvideo.io.vreader(args.filename)


if __name__ == "__main__":
    main()
