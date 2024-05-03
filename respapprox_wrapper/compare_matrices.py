import io
import logging
import math
import struct
import sys


def read_float(f: io.BufferedReader) -> float:
    s = f.read(8)
    d = struct.unpack('d', s)[0]
    return d


def compare_matrices(filename1: str, filename2: str, channels_num: int, rel_epsilon: float = 1e-9) -> bool:
    """
    compares 2 response matrices, you need to pass channels_num for matrices.
    """
    with open(filename1, 'rb') as f, open(filename2, 'rb') as g:
        for i in range(channels_num):
            for j in range(channels_num):
                lhs = read_float(f)
                rhs = read_float(g)
                diff = 2 * (lhs - rhs) / (lhs + rhs + rel_epsilon) * 100
                if not math.isclose(lhs, rhs, rel_tol=rel_epsilon):
                    logging.error(f"{i}:{j} value is different: {lhs} != {rhs}, diff={diff}%")
                    return False
    return True


def convert_mtx_to_txt(input_filename: str, output_filename: str, channels_num: int) -> None:
    with open(input_filename, 'rb') as f, open(output_filename, 'w') as g:
        for _ in range(channels_num):
            for j in range(channels_num):
                v = read_float(f)
                g.write(str(v))
                if j+1 != channels_num:
                    g.write('\t')
            g.write('\n')


def main():
    if len(sys.argv) <= 3:
        print("compare <matrix_fname1> <matrix_fname2> <channel_num>")
        sys.exit()
    compare_matrices(sys.argv[1], sys.argv[2], int(sys.argv[3]))


if __name__ == "__main__":
    main()
