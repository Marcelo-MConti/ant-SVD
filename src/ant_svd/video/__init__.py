import scipy
import skimage
import numpy as np


def preprocess_chunk(frames, /, height: int, width: int) -> np.ndarray:
    """
    Preprocesses a chunk of frames in YUV444P format (extracts the luma component of each frame)
    and resizes each frame to the dimensions specified in height and width parameters.

    Returns a matrix of the frames in the chunk.
    """
    chunk_size = len(frames)
    frame_mat = np.ndarray(shape=(height * width, chunk_size))

    for i in range(chunk_size):
        # frames[i].shape = (height, width, n_chan)
        #
        # YUV444P has three channels: Y (luma), U (blue difference), V (green difference)
        # We only use the luma channel (0) when applying SVD
        frame_luma = frames[i][:, :, 0]
        frame_luma_resized = skimage.transform.resize(
            frame_luma,
            (height, width)
        )

        frame_mat[:, i] = np.reshape(frame_luma_resized / 255, height * width)

    return frame_mat


def postprocess_mask(frame_mask: np.ndarray, thresh: float, /, orig_height: int, orig_width: int) -> np.ndarray:
    """
    Given a grayscale mask, converts it to a binary mask using the threshold given
    and scales it to the specified dimensions.

    Returns the rescaled binary mask.
    """
    m = np.max(frame_mask)
    bin_mask = np.round(frame_mask * (0.5 / thresh) / m)

    filled_mask = scipy.ndimage.binary_fill_holes(bin_mask)
    filled_mask_resized = skimage.transform.resize(filled_mask, (orig_height, orig_width))

    return filled_mask_resized
