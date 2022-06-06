import os.path
import sys
from ctypes import CDLL, RTLD_GLOBAL, c_int, c_double, c_char_p


PREPARE_ERROR_CODES = [
    "",
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
    "Bad input json file",
    "Error while parsing input json file"
]


class TccFcalcDllWrapper:
    def __init__(self, path_to_dll=None, lib_name='libtccfcalc.dll') -> None:
        if path_to_dll is None:
            path_to_dll = os.path.dirname(__file__)
        self._lib = CDLL(os.path.join(path_to_dll, lib_name), RTLD_GLOBAL)
        # prepare
        self._tccfcalc_prepare = getattr(self._lib, 'TCCFCALC_Prepare@24')
        self._tccfcalc_prepare.argtypes = [c_int, c_int, c_int, c_char_p, c_char_p, c_int]
        # prepare json
        self._tccfcalc_prepare_json = getattr(self._lib, 'TCCFCALC_Prepare_Json@8')
        self._tccfcalc_prepare_json.argtypes = [c_char_p, c_int]
        # calculate
        self._tccfcalc_calculate = getattr(self._lib, 'TCCFCALC_Calculate@4')
        self._tccfcalc_calculate.argtypes = [c_int]
        # reset
        self._tccfcalc_reset = getattr(self._lib, 'TCCFCALC_Reset@0')
        # calc spectrum
        self._tccfcalc_calc_spectrum = getattr(self._lib, 'TCCFCALC_CalcSpectrumFile@12')
        self._tccfcalc_calc_spectrum.argtypes = [c_char_p, c_double]

    def tccfcalc_prepare(self, a: int, z: int, m, cur_path: str, library_path: str, seed: int = 0) -> int:
        return self._tccfcalc_prepare(a, z, m, bytes(cur_path, 'utf-8'), bytes(library_path, 'utf-8'), seed)

    def tccfcalc_prepare_json(self, input_filename: str, seed: int) -> int:
        return self._tccfcalc_prepare_json(bytes(input_filename, 'utf-8'), seed)

    def tccfcalc_calculate(self, histories: int) -> None:
        return self._tccfcalc_calculate(histories)

    def tccfcalc_reset(self) -> None:
        self._tccfcalc_reset()

    def tccfcalc_calc_spectrum(self, analyzer_filename: str, activity: float) -> int:
        return self._tccfcalc_calc_spectrum(bytes(analyzer_filename, 'utf-8'), activity)


def main():
    cur_path = os.path.dirname(__file__)
    cur_lib_path = os.path.join(cur_path, 'Lib')
    lib = TccFcalcDllWrapper()
    res = lib.tccfcalc_prepare(290, 27, 0, cur_path, cur_lib_path, 42)
    if res:
        print(f'prepare {res=}: {PREPARE_ERROR_CODES.get(res)}')
        sys.exit()

    for _ in range(1000):
        lib.tccfcalc_calculate(1000)
    print('done')


if __name__ == '__main__':
    main()
