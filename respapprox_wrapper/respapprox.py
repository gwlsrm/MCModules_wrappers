import argparse
import logging
import os
import sys
import time

from respapprox_wrapper import RespapproxDllWrapper


def calc_response_matrix_singlethread(lib: RespapproxDllWrapper, input_filename: str) -> bool:
    # init
    res = lib.init_single_json(input_filename)
    if res > 0:
        logging.error("Respprox init single error {}".format(res))
        lib.close()
        return False
    channels_number = -res
    logging.info("Initialized single thread, channels number={}".format(channels_number))
    # calc
    for ch in range(channels_number):
        lib.calculate(ch)
    logging.info("calculation is done")
    lib.close()
    return True


def calc_response_matrix_multithread(lib: RespapproxDllWrapper, input_filename: str) -> bool:
    # init
    res = lib.init_json(input_filename)
    if res > 0:
        logging.error("Respprox init error {}".format(res))
        lib.close()
        return False
    channels_number = -res
    logging.info("Initialized multithread, channels number={}".format(channels_number))
    # calc
    lib.calculate_all()
    cur_channel = 0
    while cur_channel < channels_number:
        cur_channel = lib.get_channel()
        time.sleep(1)
    is_all_saved = False
    for _ in range(10):
        is_all_saved = lib.finished_saving()
        if is_all_saved:
            break
        time.sleep(0.1)
    logging.info(f"calculation is done, is all saved={is_all_saved}")
    lib.close()
    return True


def calc_response_matrix(is_multithread: bool = False) -> bool:
    cur_path = os.getcwd()
    lib = RespapproxDllWrapper()
    input_filename = os.path.join(cur_path, 'respapprox_input.json')
    if is_multithread:
        return calc_response_matrix_multithread(lib, input_filename)
    else:
        return calc_response_matrix_singlethread(lib, input_filename)


def main():
    parser = argparse.ArgumentParser(
        description='respapprox -- util for detector response matrix calculation')
    parser.add_argument('--multithread', help='calculate in multithread mode', action="store_true", default=False)
    parser.add_argument('-v', '--verbose', help='verbose mode', action="store_true", default=False)
    args = parser.parse_args()

    # logger
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )

    calc_response_matrix(args.multithread)


if __name__ == "__main__":
    main()
