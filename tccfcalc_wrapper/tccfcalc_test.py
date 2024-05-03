"""
    test tccfcalc.dll calculation
"""
import argparse
import logging
import os
import shutil
import sys
from itertools import product
from tqdm import tqdm

from effcalc import calculate_eff, calculate_eff_json
from nuclide import Nuclide
from outfile_reader import compare_out_files


SEED = 42
N = 1000
ACTIVITY = 10000

det_list = ['hpge', 'scintil']
geom_list = ['point', 'cylinder', 'marinelli', 'cone']
effmaker_geom_list = ['point', 'cylinder', 'cylindersmall', 'cone']
effmaker_additional_geom_list = ['sphere', 'cuboid']
nuclide_list = ['co-60', 'eu-152', 'k-40']


def _form_filename_suffix(det, geom, nuclide, is_multithread=False):
    tokens = [det, geom]
    if nuclide:
        tokens.append(nuclide)
    if is_multithread:
        tokens.append('mt')
    return '_'.join(tokens)


def form_infile_name(det, geom, nuclide, is_multithread=False):
    fname_suffix = _form_filename_suffix(det, geom, 'nuclide' if nuclide else '', is_multithread)
    return f'in_files{os.sep}tccfcalc_{fname_suffix}.in'


def form_infile_json_name(det, geom, nuclide):
    fname_suffix = _form_filename_suffix(det, geom, nuclide)
    return f'in_files{os.sep}tccfcalc_input_{fname_suffix}.json'


def form_outfile_name(det, geom, nuclide):
    fname_suffix = _form_filename_suffix(det, geom, nuclide)
    return f'out_files{os.sep}tccfcalc_{fname_suffix}.out'


def form_resfile_name(det, geom, nuclide, is_multithread=False):
    fname_suffix = _form_filename_suffix(det, geom, nuclide, is_multithread)
    return f'results{os.sep}tccfcalc_{fname_suffix}.out'


def form_res_spectrum_name(det, geom, nuclide):
    return f'results{os.sep}spectrum_{det}_{geom}_{nuclide}.spe'


def form_res_coincspectrum_name(det, geom, nuclide):
    return f'results{os.sep}spectrum_coinc_{det}_{geom}_{nuclide}.spe'


def main():
    parser = argparse.ArgumentParser(description='tests for tccfcalc.dll')
    parser.add_argument('--not-calc-eff', help='do not run efficiency calculation task',
                        action="store_true", default=False)
    parser.add_argument('--not-calc-coinc', help='do not run coincidence calculation task',
                        action="store_true", default=False)
    parser.add_argument('--not-calc-json', help='do not run json-tccfcalc efficiency calculation task',
                        action="store_true", default=False)
    parser.add_argument('--not-calc-effmaker', help='do not run effmaker source efficiency calculation task',
                        action="store_true", default=False)
    parser.add_argument('--not-calc-mt', help='do not run multithread tasks',
                        action="store_true", default=False)
    parser.add_argument('--calc-addition-effmaker', help='run additional effmaker source efficiency calculation task',
                        action="store_true", default=False)
    parser.add_argument('--cmp-with-errors', help='using uncertainties to compare results',
                        action="store_true", default=False)
    args = parser.parse_args()
    rel_eps = None if args.cmp_with_errors else 1e-3
    calc_eff_task = not args.not_calc_eff
    calc_coinc_task = not args.not_calc_coinc
    calc_json_task = not args.not_calc_json
    calc_effmaker_task = not args.not_calc_effmaker
    calc_mt_task = not args.not_calc_mt
    calc_addition_effmaker = args.calc_addition_effmaker
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

    # efficiency
    if calc_eff_task:
        nuclide = ''
        for det, geom in tqdm(product(det_list, geom_list)):
            tccfcalc_name = form_infile_name(det, geom, nuclide)
            outfname = form_outfile_name(det, geom, nuclide)
            logging.info('calc with: ' + tccfcalc_name)
            shutil.copy(tccfcalc_name, 'tccfcalc.in')
            calculate_eff(Nuclide.get_default(), N, False, SEED, ACTIVITY)
            res = compare_out_files('tccfcalc.out', outfname, rel_eps=rel_eps)
            if not res:
                logging.error(f'tccfcal.out != {outfname}')
            else:
                logging.info(f'tccfcal.out == {outfname}')
            shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))

    # coincidence
    if calc_coinc_task:
        geom = 'point'
        for det, nuclide in tqdm(product(det_list, nuclide_list)):
            tccfcalc_name = form_infile_name(det, geom, nuclide)
            outfname = form_outfile_name(det, geom, nuclide)
            logging.info('calc with: ' + tccfcalc_name)
            shutil.copy(tccfcalc_name, 'tccfcalc.in')
            calculate_eff(Nuclide.parse_from(nuclide), N, True, SEED, ACTIVITY)
            res = compare_out_files('tccfcalc.out', outfname, rel_eps=rel_eps)
            if not res:
                logging.error(f'tccfcal.out != {outfname}')
            else:
                logging.info(f'tccfcal.out == {outfname}')
            shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))
            shutil.copy('test_spectr.spe', form_res_spectrum_name(det, geom, nuclide))
            shutil.copy('test_spectr_coi.spe', form_res_coincspectrum_name(det, geom, nuclide))

    # multithread calculation
    if calc_mt_task:
        for det, geom, nuclide in tqdm([('hpge', 'cylinder', ''), ('scintil', 'point', 'co-60')]):
            tccfcalc_name = form_infile_name(det, geom, nuclide, is_multithread=True)
            outfname = form_outfile_name(det, geom, nuclide)
            logging.info('calc with: ' + tccfcalc_name)
            shutil.copy(tccfcalc_name, 'tccfcalc.in')
            nucl = Nuclide.parse_from(nuclide) if nuclide else Nuclide.get_default()
            calculate_eff(nucl, N, False, SEED, ACTIVITY)
            res = compare_out_files('tccfcalc.out', outfname, rel_eps=None)
            if not res:
                logging.error(f'tccfcal.out != {outfname}')
            else:
                logging.info(f'tccfcal.out == {outfname}')
            shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide, is_multithread=True))

    # tccfcalc json calculation cycle
    if calc_json_task:
        nuclide = ''
        for det, geom in tqdm(product(det_list, geom_list)):
            tccfcalc_name = form_infile_json_name(det, geom, nuclide)
            outfname = form_outfile_name(det, geom, nuclide)
            logging.info('calc with: ' + tccfcalc_name)
            shutil.copy(tccfcalc_name, 'tccfcalc_input.json')
            calculate_eff_json(N, False, SEED, ACTIVITY)
            res = compare_out_files('tccfcalc.out', outfname, rel_eps=rel_eps)
            if not res:
                logging.error(f'tccfcal.out != {outfname}')
            else:
                logging.info(f'tccfcal.out == {outfname}')
            shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))

    # effmaker source efficiency calculation task
    if calc_effmaker_task:
        nuclide = 'effmaker'
        for det, geom in tqdm(product(det_list, effmaker_geom_list)):
            tccfcalc_name = form_infile_json_name(det, geom, nuclide)
            outfname = form_outfile_name(det, geom, nuclide)
            logging.info('calc with: ' + tccfcalc_name)
            shutil.copy(tccfcalc_name, 'tccfcalc_input.json')
            calculate_eff_json(N, False, SEED, ACTIVITY)
            res = compare_out_files('tccfcalc.out', outfname, rel_eps=rel_eps)
            if not res:
                logging.error(f'tccfcal.out != {outfname}')
            else:
                logging.info(f'tccfcal.out == {outfname}')
            shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))

    # effmaker additional efficiency calculation task
    if calc_addition_effmaker:
        nuclide = 'effmaker'
        for det, geom in tqdm(product(det_list, effmaker_additional_geom_list)):
            tccfcalc_name = form_infile_json_name(det, geom, nuclide)
            outfname = form_outfile_name(det, geom, nuclide)
            logging.info('calc with: ' + tccfcalc_name)
            shutil.copy(tccfcalc_name, 'tccfcalc_input.json')
            calculate_eff_json(N, False, SEED, ACTIVITY)
            res = compare_out_files('tccfcalc.out', outfname, rel_eps=rel_eps)
            if not res:
                logging.error(f'tccfcal.out != {outfname}')
            else:
                logging.info(f'tccfcal.out == {outfname}')
            shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))


if __name__ == '__main__':
    main()
