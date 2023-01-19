import argparse
import os.path
import sys
import logging

from tccfcalc_wrapper import TccFcalcDllWrapper, PREPARE_ERROR_CODES
from nuclide import Nuclide


def calculate_eff(nuclide, N, anal_fname, seed, activity):
    # prepare
    cur_path = os.getcwd()
    cur_lib_path = os.path.join(cur_path, 'Lib')
    lib = TccFcalcDllWrapper()
    error_num = lib.tccfcalc_prepare(nuclide.a, nuclide.z, nuclide.m, cur_path, cur_lib_path, seed)
    if error_num:
        error_msg = PREPARE_ERROR_CODES[error_num] if error_num < len(PREPARE_ERROR_CODES) else ''
        logging.error(f'Prepare error #{error_num}: {error_msg}')
        sys.exit()
    logging.info('Prepared successfully')

    # calculate
    logging.info(f'Starting calculation with N = {N}')
    percent = 0
    for i in range(N):
        lib.tccfcalc_calculate(1000)
        new_percent = int(10 * i / N)
        if percent != new_percent:
            percent = new_percent
            logging.debug(f'{percent*10}%')

    # spectrum
    if anal_fname:
        logging.info('Start calculating spectr with analyzer: ' + anal_fname)
        error_num = lib.tccfcalc_calc_spectrum(anal_fname, activity)
        if error_num:
            logging.error('Spectrum calculation error #' + str(error_num))
            sys.exit()
        logging.info('Spectrum calculation done')


def calculate_eff_json(N, anal_fname, seed, activity):
    # prepare
    cur_path = os.getcwd()
    input_filename = os.path.join(cur_path, 'tccfcalc_input.json')
    lib = TccFcalcDllWrapper()
    error_num = lib.tccfcalc_prepare_json(input_filename, seed)
    if error_num:
        logging.error(f'Prepare error #{error_num}: {PREPARE_ERROR_CODES.get(error_num)}')
        sys.exit()
    logging.info('Prepared successfully')

    # calculate
    logging.info(f'Starting calculation with N = {N}')
    percent = 0
    for i in range(N):
        lib.tccfcalc_calculate(1000)
        new_percent = int(10 * i / N)
        if percent != new_percent:
            percent = new_percent
            logging.debug(f'{percent*10}%')

    # spectrum
    if anal_fname:
        logging.info('Start calculating spectrum with analyzer: ' + anal_fname)
        error_num = lib.tccfcalc_calc_spectrum(anal_fname, activity)
        if error_num:
            logging.error('Spectrum calculation error #' + str(error_num))
            sys.exit()
        logging.info('Spectrum calculation done')


def main():
    parser = argparse.ArgumentParser(description='effcalc -- util for efficiency calcultion with Monte-Carlo method')

    parser.add_argument('positional', help='element Z, A, M', nargs='*', type=int)

    parser.add_argument('-n', '--nuclide', help='nuclide as string, e.g. Co-60 or Cs-137m')
    parser.add_argument('-N', '--histories', help='calculation histories, thsnds', type=int, default=1000)
    parser.add_argument('-s', '--seed', help='seed for random generator, default = 0 <- random seed',
                        type=int, default=0)
    parser.add_argument('-a', '--analyzer', help='analyzer filename (*.ain), will calculate spectrum')
    parser.add_argument('--activity', help='activity for source in Bq, default = 1000 Bq',
                        type=float, default=1000)
    parser.add_argument('--json', help='search tccfcalc_input.json', action="store_true", default=False)
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

    # other
    N = args.histories
    anal_fname = os.path.abspath(args.analyzer) if args.analyzer is not None else None
    seed = args.seed
    activity = args.activity

    if args.json:
        calculate_eff_json(N, anal_fname, seed, activity)
    else:
        calculate_eff(nuclide, N, anal_fname, seed, activity)


if __name__ == '__main__':
    main()
