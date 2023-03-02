"""
    test tccfcalc.dll calculation
"""
import logging
import os
import shutil
import sys
from itertools import product
from tqdm import tqdm

from effcalc import calculate_eff, calculate_eff_json
from nuclide import Nuclide
from outfile_reader import compare_out_files


det_list = ['hpge', 'scintil']
geom_list = ['point', 'cylinder', 'marinelli', 'cone']
nuclide_list = ['co-60', 'eu-152']


def form_infile_name(det, geom, nuclide):
    if nuclide:
        return f'in_files{os.sep}tccfcalc_{det}_{geom}_nuclide.in'
    else:
        return f'in_files{os.sep}tccfcalc_{det}_{geom}.in'


def form_infile_json_name(det, geom, nuclide):
    if nuclide:
        return f'in_files{os.sep}tccfcalc_input_{det}_{geom}_{nuclide}.json'
    else:
        return f'in_files{os.sep}tccfcalc_input_{det}_{geom}.json'


def form_outfile_name(det, geom, nuclide):
    if nuclide:
        return f'out_files{os.sep}tccfcalc_{det}_{geom}_{nuclide}.out'
    else:
        return f'out_files{os.sep}tccfcalc_{det}_{geom}.out'


def form_resfile_name(det, geom, nuclide):
    if nuclide:
        return f'results{os.sep}tccfcalc_{det}_{geom}_{nuclide}.out'
    else:
        return f'results{os.sep}tccfcalc_{det}_{geom}.out'


def form_res_spectrum_name(det, geom, nuclide):
    return f'results{os.sep}spectrum_{det}_{geom}_{nuclide}.spe'


def form_res_coincspectrum_name(det, geom, nuclide):
    return f'results{os.sep}spectrum_coinc_{det}_{geom}_{nuclide}.spe'


SEED = 42
N = 1000
ACTIVITY = 10000


if __name__ == '__main__':
    # logger
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    # create results directory and copy analyzer.ain
    if not os.path.exists('results'):
        os.mkdir('results')
    if not os.path.exists('analyzer.ain'):
        shutil.copy('in_files/analyzer_ppd_8k_3MeV.ain', 'analyzer.ain')
    anal_path = os.path.abspath('analyzer.ain')

    # efficiency
    nuclide = ''
    for det, geom in tqdm(product(det_list, geom_list)):
        tccfcalc_name = form_infile_name(det, geom, nuclide)
        outfname = form_outfile_name(det, geom, nuclide)
        logging.info('calc with: ' + tccfcalc_name)
        shutil.copy(tccfcalc_name, 'tccfcalc.in')
        calculate_eff(Nuclide.get_default(), N, None, SEED, ACTIVITY)
        res = compare_out_files('tccfcalc.out', outfname, rel_eps=1e-3)
        if not res:
            logging.error(f'tccfcal.out != {outfname}')
        else:
            logging.info(f'tccfcal.out == {outfname}')
        shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))

    # coincidence
    geom = 'point'
    for det, nuclide in tqdm(product(det_list, nuclide_list)):
        tccfcalc_name = form_infile_name(det, geom, nuclide)
        outfname = form_outfile_name(det, geom, nuclide)
        logging.info('calc with: ' + tccfcalc_name)
        shutil.copy(tccfcalc_name, 'tccfcalc.in')
        calculate_eff(Nuclide.parse_from(nuclide), N, anal_path, SEED, ACTIVITY)
        res = compare_out_files('tccfcalc.out', outfname, rel_eps=1e-3)
        if not res:
            logging.error(f'tccfcal.out != {outfname}')
        else:
            logging.info(f'tccfcal.out == {outfname}')
        shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))
        shutil.copy('test_spectr.spe', form_res_spectrum_name(det, geom, nuclide))
        shutil.copy('test_spectr_coi.spe', form_res_coincspectrum_name(det, geom, nuclide))

    # json calculation cycle
    nuclide = ''
    for det, geom in tqdm(product(det_list, geom_list)):
        tccfcalc_name = form_infile_json_name(det, geom, nuclide)
        outfname = form_outfile_name(det, geom, nuclide)
        logging.info('calc with: ' + tccfcalc_name)
        shutil.copy(tccfcalc_name, 'tccfcalc_input.json')
        calculate_eff_json(N, None, SEED, ACTIVITY)
        res = compare_out_files('tccfcalc.out', outfname, rel_eps=1e-3)
        if not res:
            logging.error(f'tccfcal.out != {outfname}')
        else:
            logging.info(f'tccfcal.out == {outfname}')
        shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))
