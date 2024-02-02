import numpy as np


def unpack_frame_arr(frames, idx_extract=6):
    list_vals = []
    for frame in frames:
        list_vals.append(frame.to_matrix()[idx_extract])

    return np.asarray(list_vals)
