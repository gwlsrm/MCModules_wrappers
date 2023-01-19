"""
    test tccfcalc.dll calculation
"""

import logging
import os
import shutil
import sys

from effcalc import calculate_eff, calculate_eff_json
from nuclide import Nuclide


det_list = ['hpge', 'scintil']
geom_list = ['point', 'cylinder', 'marinelli', 'cone']
nuclide_list = ['co-60', 'eu-152']


def form_infile_name(det, geom, nuclide):
    if len(nuclide) == 0:
        return f'in_files{os.sep}tccfcalc_{det}_{geom}.in'
    else:
        return f'in_files{os.sep}tccfcalc_{det}_{geom}_{nuclide}.in'


def form_infile_json_name(det, geom, nuclide):
    if len(nuclide) == 0:
        return f'in_files{os.sep}tccfcalc_input_{det}_{geom}.json'
    else:
        return f'in_files{os.sep}tccfcalc_input_{det}_{geom}_{nuclide}.json'


def form_outfile_name(det, geom, nuclide):
    if len(nuclide) == 0:
        return f'out_files{os.sep}tccfcalc_{det}_{geom}.out'
    else:
        return f'out_files{os.sep}tccfcalc_{det}_{geom}_{nuclide}.out'


def form_resfile_name(det, geom, nuclide):
    if len(nuclide) == 0:
        return f'results{os.sep}tccfcalc_{det}_{geom}.out'
    else:
        return f'results{os.sep}tccfcalc_{det}_{geom}_{nuclide}.out'


def form_res_spectrum_name(det, geom, nuclide):
    return f'results{os.sep}spectrum_{det}_{geom}_{nuclide}.spe'


def form_res_coincspectrum_name(det, geom, nuclide):
    return f'results{os.sep}spectrum_coinc_{det}_{geom}_{nuclide}.spe'


calc_params = {
    'seed': '-s 42',
    'co-60': '-n Co-60',
    'eu-152': '-n Eu-152',
    'N10000': '-N 10000',
    }


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

    # calculation cycle
    for det in det_list:
        nuclide = ''
        for geom in geom_list:
            tccfcalc_name = form_infile_name(det, geom, nuclide)
            outfname = form_outfile_name(det, geom, nuclide)
            logging.info('calc with: ' + tccfcalc_name)
            shutil.copy(tccfcalc_name, 'tccfcalc.in')
            calculate_eff(Nuclide.get_default(), N, None, SEED, ACTIVITY)
            os.system(f'out_cmp.exe tccfcalc.out {outfname}')  # 1e-3')
            shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))

        geom = 'point'
        for nuclide in nuclide_list:
            tccfcalc_name = form_infile_name(det, geom, nuclide)
            outfname = form_outfile_name(det, geom, nuclide)
            logging.info('calc with: ' + tccfcalc_name)
            shutil.copy(tccfcalc_name, 'tccfcalc.in')
            calculate_eff(Nuclide.parse_from(nuclide), N, anal_path, SEED, ACTIVITY)
            os.system(f'out_cmp.exe tccfcalc.out {outfname}')  # 1e-3')
            shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))
            shutil.copy('test_spectr.spe', form_res_spectrum_name(det, geom, nuclide))
            shutil.copy('test_spectr_coi.spe', form_res_coincspectrum_name(det, geom, nuclide))

    # json calculation cycle
    for det in det_list:
        nuclide = ''
        for geom in geom_list:
            tccfcalc_name = form_infile_json_name(det, geom, nuclide)
            outfname = form_outfile_name(det, geom, nuclide)
            logging.info('calc with: ' + tccfcalc_name)
            shutil.copy(tccfcalc_name, 'tccfcalc_input.json')
            calculate_eff_json(N, None, SEED, ACTIVITY)
            os.system(f'out_cmp.exe tccfcalc.out {outfname} 1e-3')
            shutil.copy('tccfcalc.out', form_resfile_name(det, geom, nuclide))
