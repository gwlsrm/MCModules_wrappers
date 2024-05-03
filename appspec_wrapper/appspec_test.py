import logging
import os
import sys
import typing as tp

from appspec_wrapper import AppspecDllWrapper
from read_output_bin import convert_from_bin_to_txt


FILE_LIST = ["appspec_{}_with_peaks", "appspec_{}_wo_peaks"]
TOL = 1e-7


def form_infile_name(filename):
    return f"input_jsons{os.sep}{filename}.json"


def form_etalon_name(filename):
    return f"etalon{os.sep}{filename}.txt"


def form_result_name(filename):
    return f"results{os.sep}{filename}.txt"


def read_result(filename: str) -> tp.List[float]:
    with open(filename) as f:
        return [float(line.strip()) for line in f]


def compare_res_with_etalon(result_filename, etalon_filename):
    results = read_result(result_filename)
    etalon = read_result(etalon_filename)
    if (len(results) != len(etalon)):
        logging.error("results {} and etalon have different length: {} != {}".format(result_filename,
                      len(results), len(etalon)))
        return
    for i, (r, e) in enumerate(zip(results, etalon)):
        if abs(r - e) > TOL:
            logging.info(f"channel {i}: {r} != {e}, diff={r-e}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        stream=sys.stderr,
    )

    appspec_calc = AppspecDllWrapper()

    for file_template in FILE_LIST:
        input_filename = form_infile_name(file_template.format("input"))
        etalon_filename = form_etalon_name(file_template.format("output"))
        result_filename = form_result_name(file_template.format("output"))
        logging.info(f"file: {input_filename}")

        res = appspec_calc.calc_apparatus_spectrum(input_filename)
        if res:
            logging.error("Apparatus spectrum calculation error {}".format(res))
            continue
        convert_from_bin_to_txt('appspec_output.bin', result_filename)
        compare_res_with_etalon(result_filename, etalon_filename)
    logging.info("done")


if __name__ == "__main__":
    main()
