import argparse
import os.path
import sys
import logging

from tccfcalc_wrapper import TccFcalcDllWrapper
from nuclide import Nuclide


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='effcalc -- util for efficiency calcultion with Monte-Carlo method')
    
    parser.add_argument('positional', help='element Z, A, M', nargs='*', type=int)

    parser.add_argument('-n', '--nuclide', help='nuclide as string, e.g. Co-60 or Cs-137m')
    parser.add_argument('-N', '--histories', help='calculation histories, thsnds', type=int, default=1000)
    parser.add_argument('-s', '--seed', help='seed for random generator, default = 0 <- random seed', 
        type=int, default=0)
    parser.add_argument('-a', '--analyzer', help='analyzer filename (*.ain), will calculate spectrum')
    parser.add_argument('-v', '--verbose', help='verbose mode', action="store_true", default=False)
    
    args = parser.parse_args()

    # logger
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    # nuclide
    if len(args.positional) not in (0, 3):
        raise ValueError('need 3 or 0 positional arguments')

    if len(args.positional) == 3:
        nuclide = Nuclide(*args.positional)
    else:
        if args.nuclide is not None:
            nuclide = Nuclide.parse_from(args.nuclide)
        else:
            nuclide = Nuclide.get_default()
    logging.info(nuclide)

    # prepare
    cur_path = os.path.dirname(__file__)
    cur_lib_path = os.path.join(cur_path, 'Lib')
    lib = TccFcalcDllWrapper()
    tcc_prepare = lib.get_tccfcalc_prepare()
    error_num = tcc_prepare(nuclide.a, nuclide.z, nuclide.m, bytes(cur_path, 'utf-8'), 
                      bytes(cur_lib_path, 'utf-8'), args.seed)
    if error_num:
        logging.error(f'Prepare error #{error_num}')
        sys.exit()
    logging.info('Prepared successfully')

    # calculate
    tcc_calculate = lib.get_tccfcalc_calculate()
    N = args.histories
    logging.info(f'Starting calculation with N = {N}')
    percent = 0
    for i in range(N):
        tcc_calculate(1000)
        new_percent = int(10 * i / N)
        if percent != new_percent:
            percent = new_percent
            logging.info(f'{percent*10}%')

    # spectrum
    if args.analyzer:
        tcc_calc_spectrum = lib.get_tccfcalc_calc_spectrum()
        anal_fname = os.path.abspath(args.analyzer)
        logging.info('Start calculating spectr with analyzer: ' + anal_fname)
        error_num = tcc_calc_spectrum(bytes(args.analyzer, 'utf-8'), 1e3)
        if error_num:
            logging.error('Spectrum calculation error #' + str(error_num))
            sys.exit()
        logging.info('Spectrum calculation done')
    
    logging.info('done')
