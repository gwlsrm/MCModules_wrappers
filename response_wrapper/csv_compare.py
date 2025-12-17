"""
    compare 2 csv files
"""
import argparse
import csv
import logging
import math
import sys
import typing as tp

import numpy as np

from numpy.polynomial import Polynomial


REL_TOL = 1e-5
ABS_TOL = 1e-6
EPS = 1e-10
N_POINTS = 100

COL_TO_UNC_COL = {
    "fep": "dfep",
    "sep": "dsep",
    "dep": "ddep",
    "xept": "dxept",
    "p511": "dp511",
    "FEP": "dfep",
    "SEP": "dsep",
    "DEP": "ddep",
    "P511": "dp511",
    "XEPT": "dxept",
}
SKIP_COL_NAMES = {"xep", "xep", "dxep", "XEP", "dsep", "ddep", "dxept", "dp511"}
POLY_COL_PREFIXES = {"a", "b"}
K = 3


def _parse_coeffs(row: list, header: dict[str, int]) -> tuple[list[list[float]], list[list[float]]]:
    a = []
    b = []
    for i in range(6):
        a.append([row[header[f"a{i}{j}"]] for j in range(9)])
    for i in range(2):
        b.append([row[header[f"b{i}{j}"]] for j in range(9)])
    return a, b


def _compare_vals(val1, val2, rel_tol: float = REL_TOL, abs_tol: float = ABS_TOL) -> bool:
    if isinstance(val1, float):
        return math.isclose(val1, val2, rel_tol=rel_tol, abs_tol=abs_tol)
    elif isinstance(val1, str):
        nums1 = [float(v) for v in val1.split(';')]
        nums2 = [float(v) for v in val2.split(';')]
        for n1, n2 in zip(nums1, nums2):
            if not _compare_vals(n1, n2, rel_tol):
                return False
        return True
    else:
        print("unsupported type: ", type(val1), val1)
        return val1 == val2


def _calc_diff(val1, val2) -> tp.Optional[float]:
    if isinstance(val1, float):
        return 2.0 * (val1 - val2) / (val1 + val2)
    else:
        return None


def _print_max_diff(y1: np.ndarray, y2: np.ndarray):
    abs_diff = np.abs(y1 - y2)
    max_abs_diff_idx = np.argmax(abs_diff)
    max_abs_diff = abs_diff[max_abs_diff_idx]
    max_rel_diff = 2 * max_abs_diff / (y1[max_abs_diff_idx] + y2[max_abs_diff_idx] + EPS)
    logging.error(f"  poly_idx={max_abs_diff_idx}: abs_diff={max_abs_diff:.4}, rel_diff={max_rel_diff:.3}")


def _compare2coeffs(coeff_1: list[float], coeff_2: list[float], rel_tol: float = REL_TOL) -> bool:
    assert len(coeff_1) == len(coeff_2)
    p1 = Polynomial(coeff_1)
    p2 = Polynomial(coeff_2)
    x = np.linspace(0, 1, N_POINTS)
    y1 = p1(x).sum()
    y2 = p2(x).sum()
    # a_tolerance = np.sqrt(N_POINTS)
    a_tolerance = 5 * N_POINTS / 100
    res = np.isclose(y1, y2, rtol=rel_tol, atol=a_tolerance)
    if not res:
        diff = y2 - y1
        rel_diff = 2 * diff / (y2 + y1 + EPS)
        logging.error(f" polynome integrals are different: {y1} != {y2}, abs_diff={diff}, rel_diff={rel_diff}, rel_tol={rel_tol}, a_tol={a_tolerance}")
        # _print_max_diff(y1, y2)
    else:
        diff = y2 - y1
        rel_diff = 2 * diff / (y2 + y1 + EPS)
        logging.debug(f" polynomes integrals are equal: {y1} == {y2}, abs_diff={diff}, rel_diff={rel_diff}, rel_tol={rel_tol}, a_tol={a_tolerance}")

    return res


def _compare2points(point_1_coeffs: list[list[float]], point_2_coeffs: list[list[float]], rel_tol: float, continue_after_fail: bool = False) -> bool:
    assert len(point_1_coeffs) == len(point_2_coeffs)
    main_res = True
    for coeff_num, (coeff_1, coeff_2) in enumerate(zip(point_1_coeffs, point_2_coeffs)):
        logging.debug(f"  coeff #{coeff_num}")
        res = _compare2coeffs(coeff_1, coeff_2, rel_tol)
        if not res:
            main_res = False
            if not continue_after_fail:
                return False
    return main_res

def compare_csv(filename1: str, filename2: str, rel_tol: float = REL_TOL, abs_tol: float = ABS_TOL) -> bool:
    res = True
    with open(filename1) as f1, open(filename2) as f2:
        reader1 = csv.reader(f1, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        reader2 = csv.reader(f2, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for i, (row1, row2) in enumerate(zip(reader1, reader2)):
            if i == 0:  # header
                if row1 != row2:
                    logging.error(f'{filename1} != {filename2} diffs in headers')
                    res = False
                    break
                col_names = list(row1)
                continue
            for j, (val1, val2) in enumerate(zip(row1, row2)):
                if not _compare_vals(val1, val2, rel_tol, abs_tol):
                    diff = _calc_diff(val1, val2)
                    diff_str = f'{diff*100:.2f}%' if diff is not None else '?'
                    logging.error(
                        f'{filename1} != {filename2} in row {i} and col {j} {col_names[j]}: ' +
                        f'{val1} != {val2}, diff={diff_str}')
                    res = False
                    break
    return res


def compare_csv_with_uncertainty(filename1: str, filename2: str, rel_tol: float = REL_TOL, abs_tol: float = ABS_TOL) -> bool:
    res = True
    with open(filename1) as f1, open(filename2) as f2:
        reader1 = csv.reader(f1, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        reader2 = csv.reader(f2, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for i, (row1, row2) in enumerate(zip(reader1, reader2)):
            if i == 0:  # header
                if row1 != row2:
                    logging.error(f'{filename1} != {filename2} diffs in headers')
                    res = False
                    break
                col_name_list = list(row1)
                col_name_to_idx = {n: i for i, n in enumerate(row1)}
                continue
            for j, (val1, val2) in enumerate(zip(row1, row2)):
                col_name = col_name_list[j]
                if col_name in SKIP_COL_NAMES:
                    continue
                if col_name[0] in POLY_COL_PREFIXES:
                    # TODO: treat poly values
                    continue
                else:
                    if col_name in COL_TO_UNC_COL:
                        rel_unc_idx = col_name_to_idx[COL_TO_UNC_COL[col_name]]
                        rel_unc = K * math.hypot(row1[rel_unc_idx], row2[rel_unc_idx]) / 100.0
                        cur_res = _compare_vals(val1, val2, rel_tol=rel_unc, abs_tol=abs_tol)
                    else:
                        cur_res = _compare_vals(val1, val2, rel_tol, abs_tol)
                    if not cur_res:
                        diff = _calc_diff(val1, val2)
                        diff_str = f'{diff*100:.2f}%' if diff is not None else '?'
                        logging.error(
                            f'{filename1} != {filename2} in row {i} and col {j} {col_name}: ' +
                            f'{val1} != {val2}, diff={diff_str}')
                        res = False
                        break
            # compare polynomes
            a1, b1 = _parse_coeffs(row1, col_name_to_idx)
            a2, b2 = _parse_coeffs(row2, col_name_to_idx)
            res = _compare2points(a1, a2, rel_tol)
            if not res:
                logging.error(
                    f'{filename1} != {filename2} in row {i} in polynomes a')
                break
            res = _compare2points(b1, b2, rel_tol)
            if not res:
                logging.error(
                    f'{filename1} != {filename2} in row {i} in polynomes b')
                break

    return res


def main():
    parser = argparse.ArgumentParser(description="compare 2 csv-files with float values")
    parser.add_argument("filename1")
    parser.add_argument("filename2")
    parser.add_argument("--with_unc", action="store_true", help="use uncertainties in csv-files")
    parser.add_argument("--verbose", "-v", action="store_true", help="verbose output")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    if args.with_unc:
        res = compare_csv_with_uncertainty(args.filename1, args.filename2, rel_tol=0.05)
    else:
        res = compare_csv(args.filename1, args.filename2)
    print(res)


if __name__ == "__main__":
    main()
