import argparse
import json
import logging
import os.path
import sys

from physspec_wrapper import PhysspecDllWrapper, PREPARE_ERROR_CODES
        

def calc_physspec(seed, histories):
    # load lib and prepare
    cur_path = os.path.dirname(__file__)
    lib = PhysspecDllWrapper(lib_name='libphysspec_p_gw.dll')
    physspec_prepare = lib.get_physspec_prepare()
    input_filename = os.path.join(cur_path, 'physspec_input.json')
    error_num = physspec_prepare(bytes(input_filename, 'utf-8'), seed)
    if error_num:
        logging.error(f'Prepare error #{error_num}: {PREPARE_ERROR_CODES[error_num]}')
        sys.exit()
    logging.info('Prepared successfully')

    # calculate
    physspec_calculate = lib.get_physspec_calculate()
    N = histories * 1000
    logging.info(f'Starting calculation with N={N} and seed={seed}')
    res = physspec_calculate(N, True)
    
    # save results
    physspec_save_json = lib.get_physspec_save_json()
    output_filename = os.path.join(cur_path, 'physspec_output.json')
    physspec_save_json(bytes(output_filename, 'utf-8'))

    logging.info('done')


def _pretty_output_json(filename):
    with open(filename) as f:
        data = json.load(f)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='physspec -- util for physical spectr calculation with Monte-Carlo method')
    
    parser.add_argument('-N', '--histories', help='calculation histories, thsnds', type=int, default=1)
    parser.add_argument('-s', '--seed', help='seed for random generator, default = 0 <- random seed', 
        type=int, default=0)
    parser.add_argument('-v', '--verbose', help='verbose mode', action="store_true", default=False)
    parser.add_argument('--pretty', help='pretty json output file', action="store_true")

    args = parser.parse_args()

    # logger
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    calc_physspec(args.seed, args.histories)

    if args.pretty:
        _pretty_output_json('physspec_output.json')