import json
import logging
import math
import typing as tp

from json_compare import compare_dicts

_K = 3
ABS_DIFF_THRES = 1e-8


def _compare_values_with_abs_k(value1: float, dvalue1: float, value2: float, dvalue2: float, k: float):
    return (value1 - value2)**2 <= k**2 * (dvalue1**2 + dvalue2**2) or abs(value1 - value2) <= ABS_DIFF_THRES


def _compare_values_with_k(value1: float, dvalue1: float, value2: float, dvalue2: float, k: float):
    dvalue1 *= value1
    dvalue2 *= value2
    return _compare_values_with_abs_k(value1, dvalue1, value2, dvalue2, k)


def _k_diff(value1: float, dvalue1: float, value2: float, dvalue2: float):
    dvalue1 *= value1
    dvalue2 *= value2
    diff = (value1 - value2)**2
    den = (dvalue1**2 + dvalue2**2)
    return math.sqrt(diff / den) if den > 0 else 1e9


def compare_physspec_output_data_with_errors(data1: tp.Dict[str, tp.Any], data2: tp.Dict[str, tp.Any]) -> bool:
    calc_res1 = data1["CalculationResults"]
    calc_res2 = data2["CalculationResults"]
    # func
    if not _compare_values_with_k(calc_res1["func"], calc_res1["dfunc"], calc_res2["func"], calc_res2["dfunc"], _K):
        k_diff = _k_diff(calc_res1["func"], calc_res1["dfunc"], calc_res2["func"], calc_res2["dfunc"])
        logging.warn(
            f"calculation results differs in func: {calc_res1['func']} != {calc_res2['func']} with k_diff= {k_diff}")
        return False
    # fcol
    if not _compare_values_with_k(calc_res1["fcol"], calc_res1["dfcol"], calc_res2["fcol"], calc_res2["dfcol"], _K):
        k_diff = _k_diff(calc_res1["fcol"], calc_res1["dfcol"], calc_res2["fcol"], calc_res2["dfcol"])
        logging.warn(
            f"calculation results differs in fcol: {calc_res1['fcol']} != {calc_res2['fcol']} with k_diff= {k_diff}")
        return False
    # y0
    for i, (y1, y2) in enumerate(zip(calc_res1["y0"], calc_res2["y0"])):
        if not math.isclose(y1, y2):
            logging.warn(f"calculation results differs in y0 idx {i}: {y1} != {y2}")
            return False
    # x1
    for i, (x1, x2) in enumerate(zip(calc_res1["x1"], calc_res2["x1"])):
        if not math.isclose(x1, x2):
            logging.warn(f"calculation results differs in x1 idx {i}: {x1} != {x2}")
            return False
    # y1
    for i, (y1, dy1, y2, dy2) in enumerate(zip(calc_res1["y1"], calc_res1["dy1"], calc_res2["y1"], calc_res2["dy1"])):
        if not _compare_values_with_abs_k(y1, dy1, y2, dy2, _K):
            k_diff = _k_diff(y1, dy1, y2, dy2)
            logging.warn(f"calculation results differs in y1 idx {i}: {y1} != {y2} with k_diff= {k_diff}")
            return False
    # x2
    for i, (x1, x2) in enumerate(zip(calc_res1["x2"], calc_res2["x2"])):
        if not math.isclose(x1, x2):
            logging.warn(f"calculation results differs in x2 idx {i}: {x1} != {x2}")
            return False
    # y2
    for i, (y1, y2) in enumerate(zip(calc_res1["y2"], calc_res2["y2"])):
        dy1 = calc_res1["dfcol"]
        dy2 = calc_res2["dfcol"]
        if not _compare_values_with_k(y1, dy1, y2, dy2, _K):
            k_diff = _k_diff(y1, dy1, y2, dy2)
            logging.warn(f"calculation results differs in y2 idx {i}: {y1} != {y2} with k_diff= {k_diff}")
            return False
    return True


def compare_physspec_output_with_errors(filename1: str, filename2: str, with_error: bool = False) -> bool:
    with open(filename1) as f1, open(filename2) as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
        if with_error:
            return compare_physspec_output_data_with_errors(data1, data2)
        else:
            return compare_dicts(data1, data2)
