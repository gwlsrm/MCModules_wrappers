"""
    compare 2 csv files
"""
import csv
import logging


def compare_csv(filename1: str, filename2: str):
    with open(filename1) as f1, open(filename2) as f2:
        reader1 = csv.reader(f1, delimiter=',')
        reader2 = csv.reader(f2, delimiter=',')
        for r1, r2 in zip(reader1, reader2):
            if r1 != r2:
                logging.error(f'{filename1} != {filename2} in row:\n{r1} != {r2}')
                return False
    return True

