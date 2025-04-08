import io
import struct
import sys

import matplotlib.pyplot as plt
import numpy as np


def read_float(f: io.BufferedReader) -> float:
    s = f.read(8)
    d = struct.unpack('d', s)[0]
    return d


def plot_matrix_line(mtx_filename: str, line_num: int, channels_num: int, pic_filename: str) -> None:
    with open(mtx_filename, 'rb') as f:
        f.read(line_num * channels_num * 8)
        line = np.array([read_float(f) for _ in range(channels_num)])
    plt.figure()
    plt.plot(np.arange(channels_num), line)
    plt.savefig(pic_filename)


def main():
    if len(sys.argv) <= 3:
        print("plot <matrix_fname1> line <line_num> with <channels_num> and same it to <output_fname.png>")
        sys.exit()
    plot_matrix_line(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])


if __name__ == "__main__":
    main()
