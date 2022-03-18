import os.path
from ctypes import *


PREPARE_ERROR_CODES = [
    "Memory allocation error.",
    "Unable to load Photon Attenuation Library files.",
    "No GLECS database.",
    "Could not find ECCBINDX.BIN data file.",
    "TCCFCALC.IN file not found.",
    "Incorrect input geometry or material data",
    "No ENSDF data found for the specified A, Z and M.",
    "There is no valid record in ENSDF data library.",
    "ENSDF: Normalization record is not complete.",
    "Could not find ICC.BIN data file.",
    "No X- or gamma-rays are emitted by the source.",
    "No EPDL97 library",
    "No Ttb library",
    "No Elib library",
]


class TccFcalcDllWrapper:
    def __init__(self, path_to_dll=None, lib_name='libtccfcalc.dll') -> None:
        if path_to_dll is None:
            path_to_dll = os.path.dirname(__file__)
        self._lib = CDLL(os.path.join(path_to_dll, lib_name), RTLD_GLOBAL)

    def get_tccfcalc_prepare(self):
        tccfcalc_prepare = getattr(self._lib, 'TCCFCALC_Prepare@24')
        tccfcalc_prepare.argtypes = [c_int, c_int, c_int, c_char_p, c_char_p, c_int]
        return tccfcalc_prepare

    def get_tccfcalc_prepare_json(self):
        tccfcalc_prepare_json = getattr(self._lib, 'TCCFCALC_Prepare_Json@8')
        tccfcalc_prepare_json.argtypes = [c_char_p, c_int]
        return tccfcalc_prepare_json

    def get_tccfcalc_calculate(self):
        tcc_calculate = getattr(self._lib, 'TCCFCALC_Calculate@4')
        tcc_calculate.argtypes = [c_int]
        return tcc_calculate

    def get_tccfcalc_reset(self):
        return getattr(self._lib, 'TCCFCALC_Reset@0')

    def get_tccfcalc_calc_spectrum(self):
        tcc_calc_spectrum = getattr(self._lib, 'TCCFCALC_CalcSpectrumFile@12')
        tcc_calc_spectrum.argtypes = [c_char_p, c_double]
        return tcc_calc_spectrum


def main():
    cur_path = os.path.dirname(__file__)
    cur_lib_path = os.path.join(cur_path, 'Lib')
    lib = TccFcalcDllWrapper()
    tcc_prepare = lib.get_tccfcalc_prepare()
    res = tcc_prepare(290, 27, 0, bytes(cur_path, 'utf-8'), bytes(cur_lib_path, 'utf-8'), 42)
    if res:
        print(f'prepare {res=}: {PREPARE_ERROR_CODES[res]}')

    tcc_calculate = lib.get_tccfcalc_calculate()
    for i in range(1000):
        tcc_calculate(1000)
    print('done')


if __name__ == '__main__':
    main()
