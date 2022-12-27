"""
    test response.dll calculation
"""
import logging
import os
import shutil
import sys
from itertools import product
from tqdm import tqdm

from csv_compare import compare_csv
from energy_grid import EnergyGrid
from response import calc_response_with


det_list = ["hpge", "scintil"]
geom_list = ["point"]
E_MIN = 50
E_MAX = 3000
POINTS = 10
IS_LOG = True
SEED = 42
N = 1000


def form_infile_name(det, geom):
    return f"in_files{os.sep}response_input_{det}_{geom}.json"


def form_etalon_name(det, geom):
    return f"etalon{os.sep}response_output_{det}_{geom}.csv"


def form_result_name(det, geom):
    return f"results{os.sep}response_output_{det}_{geom}.csv"


if __name__ == "__main__":
    # logger
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    # create out_files directory and copy analyzer.ain
    if not os.path.exists('results'):
        os.mkdir('results')

    # grid
    grid = EnergyGrid(E_MIN, E_MAX, POINTS, IS_LOG)

    # calculation cycle
    for det, geom in tqdm(product(det_list, geom_list)):
        input_fname = form_infile_name(det, geom)
        etalon_fname = form_etalon_name(det, geom)
        logging.info("calc with: " + input_fname)
        shutil.copy(input_fname, "response_input.json")
        calc_response_with(grid, SEED, N)
        res = compare_csv('response_output.csv', etalon_fname)
        if not res:
            logging.error(f'calculation results for {input_fname} are different')
        else:
            logging.info(f'calculation results for {input_fname} is OK')
        shutil.copy('response_output.csv', form_result_name(det, geom))
