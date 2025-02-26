import argparse
import os.path
import sys
import logging

from response_wrapper import ResponseDllWrapper, PREPARE_ERROR_CODES
from energy_grid import EnergyGrid


DE = 0.001


def calc_response_with_params(emin, emax, grid_points, grid_log, seed, histories):
    # energy grid
    grid = EnergyGrid(emin, emax, grid_points, grid_log)
    calc_response_with(grid, seed, histories)


def calc_response_with(grid, seed, histories):
    # load lib and prepare
    cur_path = os.getcwd()
    lib = ResponseDllWrapper()
    input_filename = os.path.join(cur_path, 'response_input.json')
    error_num = lib.response_prepare(input_filename, seed)
    if error_num:
        error_msg = PREPARE_ERROR_CODES[error_num] if error_num < len(PREPARE_ERROR_CODES) else ''
        logging.error(f'Prepare error #{error_num}: {error_msg}')
        sys.exit()
    logging.info('Prepared successfully')

    # calculate
    output_filename = os.path.join(cur_path, 'response_output.csv')
    is_first = True
    N = histories * 1000
    logging.info(f'Starting calculation with N = {N}')
    for energy in grid.grid:
        logging.info(f'Calculate response for energy: {energy} keV')
        lib.response_calculate(N, energy/1000,  DE)
        lib.response_save_rfc_csv(output_filename, not is_first)
        is_first = False

    logging.info('done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='response -- util for detector response calculation with Monte-Carlo method')

    parser.add_argument('positional', help='energy grid parameters: minimal energy, maximal energy, points', nargs='*')
    parser.add_argument('--grid_log', help='is energy grid logarithmic', action="store_true")
    parser.add_argument('-N', '--histories', help='calculation histories, thsnds', type=int, default=1)
    parser.add_argument('-s', '--seed', help='seed for random generator, default = 0 <- random seed',
                        type=int, default=0)
    parser.add_argument('-v', '--verbose', help='verbose mode', action="store_true", default=False)

    args = parser.parse_args()

    # logger
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    # grid
    if len(args.positional) != 3:
        raise ValueError('need 3 positional arguments')

    grid = EnergyGrid(
        min_energy=float(args.positional[0]),
        max_energy=float(args.positional[1]),
        point_count=int(args.positional[2]),
        is_log=args.grid_log
    )

    calc_response_with(grid, args.seed, args.histories)
