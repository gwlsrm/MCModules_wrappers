from dataclasses import dataclass
import logging
import math
import sys
import typing as tp


_K = 3


def _try_str_to_float(string: str) -> tp.Optional[float]:
    try:
        return float(string)
    except ValueError:
        return None


def _compare_line_eff_with_k(eff1: float, deff1: float, eff2: float, deff2: float, k: float):
    deff1 *= eff1
    deff2 *= eff2
    return (eff1 - eff2)**2 <= k**2 * (deff1**2 + deff2**2)


def _k_diff(eff1: float, deff1: float, eff2: float, deff2: float):
    deff1 *= eff1
    deff2 *= eff2
    diff = (eff1 - eff2)**2
    den = (deff1**2 + deff2**2)
    return math.sqrt(diff / den) if den > 0 else 1e9


@dataclass
class EffLine:
    energy: float
    eff: float
    deff: float

    @staticmethod
    def parse_eff_line(line: str):
        words = line.strip().split('\t')
        if len(words) < 8:
            return None
        energy = _try_str_to_float(words[1])
        eff = _try_str_to_float(words[6])
        deff = _try_str_to_float(words[7])
        if energy is None or eff is None or deff is None:
            return None
        deff /= 100
        return EffLine(energy, eff, deff)


class OutFileReader:
    """
        Parses tccfcalc.out file
    """
    def __init__(self, filename: str) -> None:
        with open(filename) as f:
            # search header
            has_header = False
            while True:
                line = f.readline()
                if not line:
                    break
                if line.startswith("----"):
                    has_header = True
                    break
            if not has_header:
                raise ValueError(f"Out file {filename} doesn't have table")

            # read table header
            line = f.readline()
            if line:
                line = f.readline()

            # read eff lines
            self.lines: tp.List[EffLine] = []
            while True:
                line = f.readline()
                if not line or line.startswith("----"):
                    break
                eff_line = EffLine.parse_eff_line(line)
                if eff_line is not None:
                    self.lines.append(eff_line)

    def __str__(self) -> str:
        return '\n'.join([str(line) for line in self.lines])


def compare_out_files_efficiencies(lhs: OutFileReader, rhs: OutFileReader) -> bool:
    if len(lhs.lines) != len(rhs.lines):
        logging.error(f'Different lines count: {len(lhs.lines)} != {len(rhs.lines)}')
        return False

    for i, (lline, rline) in enumerate(zip(lhs.lines, rhs.lines)):
        if lline.energy != rline.energy:
            logging.error(f"lines {i} have different energies: {lline.energy} != {rline.energy}")
            return False
        if not _compare_line_eff_with_k(lline.eff, lline.deff, rline.eff, rline.deff, _K):
            k_diff = _k_diff(lline.eff, lline.deff, rline.eff, rline.deff)
            logging.error(f"lines {i} have different efficiencies: {lline.eff} != {rline.eff}, diff k = {k_diff}")
            return False
    return True


def compare_out_files_efficiencies_with_eps(lhs: OutFileReader, rhs: OutFileReader, rel_eps: float) -> bool:
    if len(lhs.lines) != len(rhs.lines):
        logging.error(f'Different lines count: {len(lhs.lines)} != {len(rhs.lines)}')
        return False

    for i, (lline, rline) in enumerate(zip(lhs.lines, rhs.lines)):
        if lline.energy != rline.energy:
            logging.error(f"lines {i} have different energies: {lline.energy} != {rline.energy}")
            return False
        if not math.isclose(lline.eff, rline.eff, rel_tol=rel_eps, abs_tol=1e-16):
            k_diff = _k_diff(lline.eff, rel_eps*lline.eff, rline.eff, rel_eps*rline.eff)
            logging.error(f"lines {i} have different efficiencies: {lline.eff} != {rline.eff}, diff k = {k_diff}")
            return False
    return True


def compare_out_files(filename1: str, filename2: str, rel_eps: tp.Optional[float] = None) -> bool:
    try:
        file_reader1 = OutFileReader(filename1)
        file_reader2 = OutFileReader(filename2)
        if rel_eps is None:
            return compare_out_files_efficiencies(file_reader1, file_reader2)
        else:
            return compare_out_files_efficiencies_with_eps(file_reader1, file_reader2, rel_eps)
    except FileNotFoundError as e:
        logging.error("File for compare is not found: %s", e)
        return False


def main():
    if len(sys.argv) < 3:
        print("outfile_reader compares 2 out-files")
        print("outfile_reader <file_lhs.out> <file_rhs> [<rel_eps>]")
        sys.exit()
    rel_eps = float(sys.argv[3]) if len(sys.argv) > 3 else None
    print(compare_out_files(sys.argv[1], sys.argv[2], rel_eps))


if __name__ == "__main__":
    main()
