"""
    compare 2 json files
"""
import json
import logging


def compare_json(filename1: str, filename2: str):
    with open(filename1) as f1, open(filename2) as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
        if data1 != data2:
            logging.error(f'{filename1} != {filename2}: {data1} != {data2}')
            return False
        return True

