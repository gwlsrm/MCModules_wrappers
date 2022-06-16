"""
    compare 2 csv files
"""
import csv
import logging
import math


REL_TOL = 1e-5


def _compare_vals(val1, val2) -> bool:
    if isinstance(val1, float):
        return math.isclose(val1, val2, rel_tol=REL_TOL)
    else:
        return val1 == val2

def compare_csv(filename1: str, filename2: str):
    res = True
    with open(filename1) as f1, open(filename2) as f2:
        reader1 = csv.reader(f1, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        reader2 = csv.reader(f2, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
        for i, (row1, row2) in enumerate(zip(reader1, reader2)):
            for val1, val2 in zip(row1, row2):
                if not _compare_vals(val1, val2):
                    logging.error(f'{filename1} != {filename2} in row {i}: {val1} != {val2}, diff={(val1 - val2)/val2}')
                    res = False
                    break
    return res
