"""
    compare 2 csv files
"""
import csv
import logging
import math
import typing as tp


REL_TOL = 1e-5


def _compare_vals(val1, val2, rel_tol=REL_TOL) -> bool:
    if isinstance(val1, float):
        return math.isclose(val1, val2, rel_tol=rel_tol)
    elif isinstance(val1, str):
        nums1 = [float(v) for v in val1.split(';')]
        nums2 = [float(v) for v in val2.split(';')]
        for n1, n2 in zip(nums1, nums2):
            if not _compare_vals(n1, n2, rel_tol):
                return False
        return True
    else:
        print("unknown type: ", type(val1), val1)
        return val1 == val2


def _calc_diff(val1, val2) -> tp.Optional[float]:
    if isinstance(val1, float):
        return 2.0 * (val1 - val2) / (val1 + val2)
    else:
        return None


def compare_csv(filename1: str, filename2: str, rel_tol: float = REL_TOL) -> bool:
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
                if not _compare_vals(val1, val2, rel_tol):
                    diff = _calc_diff(val1, val2)
                    diff_str = f'{diff*100:.2f}%' if diff is not None else '?'
                    logging.error(
                        f'{filename1} != {filename2} in row {i} and col {j} {col_names[j]}: ' +
                        f'{val1} != {val2}, diff={diff_str}')
                    res = False
                    break
    return res
