import io
import struct
import sys


def read_float(f: io.BufferedReader) -> float:
    s = f.read(8)
    d = struct.unpack('d', s)[0]
    return d


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
        print("convert <matrix_fname1> to txt <output_fname> with <channels_num>")
        sys.exit()
    convert_mtx_to_txt(sys.argv[1], sys.argv[2], int(sys.argv[3]))


if __name__ == "__main__":
    main()
