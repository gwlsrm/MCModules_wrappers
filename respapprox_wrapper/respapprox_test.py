"""
    test respapprox.dll -- response matrix calculation
"""
import logging
import os
import shutil
import sys
from itertools import product

from respapprox import calc_response_matrix
from compare_matrices import compare_matrices


def form_infile_name(has_peaks: bool) -> str:
    if has_peaks:
        return f"in_files{os.sep}respapprox_input_with_peaks.json"
    else:
        return f"in_files{os.sep}respapprox_input_wo_peaks.json"


def form_etalon_name(has_peaks: bool) -> str:
    if has_peaks:
        return f"etalon{os.sep}kd1a2.mtx"
    else:
        return f"etalon{os.sep}wpd1a4.mtx"


def form_result_name(has_peaks: bool, is_mutithread: bool) -> str:
    mt_str = "_mt" if is_mutithread else ""
    if has_peaks:
        return f"results{os.sep}kd1a2{mt_str}.mtx"
    else:
        return f"results{os.sep}wpd1a4{mt_str}.mtx"


def main():
    # logger
    logging.basicConfig(
        level=logging.WARN,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    # create out_files directory and copy analyzer.ain
    if not os.path.exists('results'):
        os.mkdir('results')

    for is_multithread, has_peaks in product([False, True], [True, False]):
        input_fname = form_infile_name(has_peaks)
        etalon_fname = form_etalon_name(has_peaks)
        logging.info(f"calc with: {input_fname} has_peaks={has_peaks}, is_multithread={is_multithread}")
        shutil.copy(input_fname, "respapprox_input.json")
        res = calc_response_matrix(is_multithread)
        if not res:
            logging.error(f"calculation error for {input_fname}")
            continue
        res = compare_matrices("test.mtx", etalon_fname, channels_num=1000, rel_epsilon=1e-7)
        if not res:
            logging.error(f'calculation results for {input_fname} are different')
        else:
            logging.info(f'calculation results for {input_fname} is OK')
        shutil.copy('test.mtx', form_result_name(has_peaks, is_multithread))


if __name__ == "__main__":
    main()
