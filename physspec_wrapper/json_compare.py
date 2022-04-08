"""
    compare 2 json files
"""
import json
import logging
import math
import sys
import os.path


def _calc_diff(v1, v2):
    return (v2 - v1) / (v1 + v2)


def _compare_dicts(data1, data2, prefix=''):
    res = True
    for k, v1 in data1.items():
        full_key = '.'.join((prefix, k)) if prefix else k
        if k not in data2:
            logging.info(f'{full_key} not in data2')
            res = False
            continue
        v2 = data2[k]
        if isinstance(v1, dict):
            res &= _compare_dicts(v1, v2, full_key)
        elif isinstance(v1, list):
            for vv1, vv2 in zip(v1, v2):
                if not math.isclose(vv1, vv2):
                    logging.info(f'{full_key}: {vv1} != {vv2}')
                    res = False
        else:
            if not math.isclose(v1, v2):
                logging.info(f'{full_key} is not equal: {v1} != {v2}, diff={_calc_diff(v1, v2)}')
                res = False
    return res


def compare_json(filename1: str, filename2: str):
    with open(filename1) as f1, open(filename2) as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
        res = _compare_dicts(data1, data2)
        if not res:
            logging.error(f'{filename1} != {filename2}')
        return res


def main():
    if len(sys.argv) < 3:
        print('compares 2 json files')
        sys.exit()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s : %(levelname)s : %(message)s',
        stream=sys.stderr,
    )
    filename1 = os.path.abspath(sys.argv[1])
    filename2 = os.path.abspath(sys.argv[2])
    res = compare_json(filename1, filename2)
    print(res)


if __name__ == '__main__':
    main()
