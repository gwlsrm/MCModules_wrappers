"""
    test physspec.dll calculation
"""
import logging
import os
import shutil
import sys
from itertools import product

from physspec import calc_physspec
from json_compare import compare_json


det_list = ["hpge", "scintil"]
collimator_list = ["nocol", "col1", "col2"]
geom_list = ["point", "barrel", "nzk"]
SEED = 42
N = 100


def form_infile_name(det, col, geom):
    return f"in_files{os.sep}physspec_input_{det}_{col}_{geom}.json"


def form_etalon_name(det, col, geom):
    return f"etalon{os.sep}physspec_output_{det}_{col}_{geom}.json"


def form_result_name(det, col, geom):
    return f"results{os.sep}physspec_output_{det}_{col}_{geom}.json"


if __name__ == "__main__":
    # logger
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    # create out_files directory
    if not os.path.exists('results'):
        os.mkdir('results')

    # calculation cycle
    for det, col, geom in product(det_list, collimator_list, geom_list):
        input_fname = form_infile_name(det, col, geom)
        etalon_fname = form_etalon_name(det, col, geom)
        logging.info("calc with: " + input_fname)
        shutil.copy(input_fname, "physspec_input.json")
        calc_physspec(SEED, N)
        res = compare_json('physspec_output.json', etalon_fname)
        if not res:
            logging.error(f'calculation for {input_fname} failed')
        else:
            logging.info(f'calculation results for {input_fname} is OK')
        shutil.copy('physspec_output.json', form_result_name(det, col, geom))
