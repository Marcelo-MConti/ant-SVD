import numpy as np

from ..svd import Compute_rank, Cumulative_variance


def log_singular_data(
    frame_mat: np.ndarray,
    u: np.ndarray, s: np.ndarray, vt: np.ndarray,
    *,
    out_dir="output"
):
    with (
        open(f"{out_dir}/singular.csv", "w") as csv_singular,
        open(f"{out_dir}/cum_var.csv", "w") as csv_cum_var,
        open(f"{out_dir}/rec_err.csv", "w") as csv_rec_err
    ):
        rank = Compute_rank(s)

        print("k,sigma_k", file=csv_singular)
        print("k,V_k", file=csv_cum_var)
        print("k,E_k", file=csv_rec_err)

        l = np.zeros_like(frame_mat)
        chunk_size = frame_mat.shape[1]

        for i in range(chunk_size):
            l += s[i] * np.outer(u[:, i], vt[i, :])

            print(f"{i + 1},{s[i]}", file=csv_singular)
            print(f"{i + 1},{Cumulative_variance(s, i + 1, rank)}", file=csv_cum_var)
            print(f"{i + 1},{np.linalg.norm(frame_mat - l, "fro")}", file=csv_rec_err)
