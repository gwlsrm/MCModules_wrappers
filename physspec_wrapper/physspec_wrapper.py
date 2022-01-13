import os.path
import sys
from ctypes import *


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
]


class CalculationResults(Structure):
    _fields_ = [
        ('npeaks', c_int),
        ('y0', POINTER(c_double)),
        ('x1', POINTER(c_double)),
        ('y1', POINTER(c_double)),
        ('dy1', POINTER(c_double)),
        ('nchannels', c_int),
        ('x2', POINTER(c_double)),
        ('y2', POINTER(c_double)),
        ('fcol', c_double),
        ('dfcol', c_double),
    ]


class PhysspecDllWrapper:
    def __init__(self, path_to_dll=None, lib_name='libphysspec_p_gw.dll') -> None:
        if path_to_dll is None:
            path_to_dll = os.path.dirname(__file__)
        self._lib = CDLL(os.path.join(path_to_dll, lib_name), RTLD_GLOBAL)
    
    def get_physspec_prepare(self):
        tccfcalc_prepare = getattr(self._lib, 'PhysSpecPrepareJson@8')
        tccfcalc_prepare.argtypes = [c_char_p, c_int]
        return tccfcalc_prepare

    def get_physspec_calculate(self):
        physspec_calculate = getattr(self._lib, 'PhysSpec_Calculate@8')
        physspec_calculate.argtypes = [c_int, c_bool]
        physspec_calculate.restype = POINTER(CalculationResults)
        return physspec_calculate

    def get_physspec_reset(self):
        return getattr(self._lib, 'PhysSpec_Reset@0')

    def get_physspec_save_json(self):
        physspec_save_json = getattr(self._lib, 'PhysSpec_Save_Json@4')
        physspec_save_json.argtypes = [c_char_p]
        return physspec_save_json


def main():
    cur_path = os.path.dirname(__file__)
    lib = PhysspecDllWrapper(lib_name='libphysspec_p_gw.dll')
    
    # prepare
    physspec_prepare = lib.get_physspec_prepare()
    input_filename = os.path.join(cur_path, 'physspec_input.json')
    res = physspec_prepare(bytes(input_filename, 'utf-8'), 42)
    print(f'prepare {res=}')
    if res:
        sys.exit()

    # calc
    physspec_calculate = lib.get_physspec_calculate()
    res = physspec_calculate(100000, True)
    
    # save
    physspec_save_json = lib.get_physspec_save_json()
    output_filename = os.path.join(cur_path, 'physspec_output.json')
    physspec_save_json(bytes(output_filename, 'utf-8'))

    print('done')


if __name__ == '__main__':
    main()    
