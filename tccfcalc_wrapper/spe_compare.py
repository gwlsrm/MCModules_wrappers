import logging

import numpy as np

from utils.speparser import SpectrumReader


def compare_spectra(txt_filename_1: str, txt_filename_2: str) -> bool:
    spe1 = SpectrumReader.parse_txt(txt_filename_1)
    spe2 = SpectrumReader.parse_txt(txt_filename_2)

    if spe1.info.tlive != spe2.info.tlive:
        logging.error(f"different live times: {spe1.info.tlive} != {spe2.info.tlive}")
        return False
    if spe1.info.treal != spe2.info.treal:
        logging.error(f"different live times: {spe1.info.treal} != {spe2.info.treal}")
        return False

    data_res = np.all(spe1.data == spe2.data)
    if not data_res:
        logging.error("different spectrum counts")
    return data_res
