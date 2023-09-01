"""
    generates energy grid for efficiency calculation (Fake 290.enx file)
"""
import argparse
import numpy as np

HEADER = "290XX   *Fake ENSDF2 B- DECAY\n"
OUT_FNAME = "290.ENX"


def format_info_string(points_num: int) -> str:
    """
290 27 I    11        10         0        10         1
       N 1.0         1.0       1.0       1.0
    """
    s1 = "290 27 I    {: <10}{: <11}0        {: <11}1\n".format(points_num+1, points_num, points_num)
    s2 = "       N 1.0         1.0       1.0       1.0\n"
    return s1 + s2


def format_level(index: int, energy: float) -> str:
    # "    3  L 145.923"
    return "{: >5}  L {:.3f}\n".format(index, energy)


def format_gamma(energy: float, intensity: float) -> str:
    # "    1  G 100.0       10.0                              0.0"
    return "    1  G {:<12.3f}{:<34.1f}0.0\n".format(energy, intensity)


def main():
    # parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument('min_energy', type=float, help='first grid energy, keV')
    parser.add_argument('max_energy', type=float, help='last grid energy, keV')
    parser.add_argument('points_number', type=int, help='number of grid points')
    parser.add_argument('-l', '--log', action="store_true", help='is logarithmic grid')
    args = parser.parse_args()
    e_min = args.min_energy
    e_max = args.max_energy
    points_num = args.points_number
    is_log = args.log

    # write to file
    with open(OUT_FNAME, 'w') as f:
        f.write(HEADER)
        f.write(
            format_info_string(points_num)
        )
        f.write('290CO  P 0.0\n')
        f.write('    1  L 0.0\n')

        energies = (np.geomspace(e_min, e_max, points_num)
            if is_log
            else np.linspace(e_min, e_max, points_num))
        intensity = 100.0 / points_num

        for i, e in enumerate(energies):
            f.write(
                format_level(i+2, e)
            )
            f.write("       B 0.0         10.0\n")
            f.write(
                format_gamma(e, intensity)
            )


if __name__ == "__main__":
    main()