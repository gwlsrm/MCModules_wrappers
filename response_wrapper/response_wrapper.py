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


class CalculationResults(Structure):
    _fields_ = [
        ('nchannels', c_int),
        ('x', POINTER(c_double)),
        ('y1', POINTER(c_double)),
        ('y2', POINTER(c_double)),
        ('y3', POINTER(c_double)),
        ('intUnc', c_double * 7),
    ]


class ResponseDllWrapper:
    def __init__(self, path_to_dll=None, lib_name='libresponse_p_gw.dll') -> None:
        if path_to_dll is None:
            path_to_dll = os.path.dirname(__file__)
        self._lib = CDLL(os.path.join(path_to_dll, lib_name), RTLD_GLOBAL)
    
    def get_response_prepare(self):
        tccfcalc_prepare = getattr(self._lib, 'Response_Prepare_Json@8')
        tccfcalc_prepare.argtypes = [c_char_p, c_int]
        return tccfcalc_prepare

    def get_response_calculate(self):
        response_calculate = getattr(self._lib, 'Response_Calculate@20')
        response_calculate.argtypes = [c_int, c_double, c_double]
        response_calculate.restype = POINTER(CalculationResults)
        return response_calculate

    def get_response_reset(self):
        return getattr(self._lib, 'Response_Reset@0')

    def get_response_save_rfc_csv(self):
        response_save_rfc_csv = getattr(self._lib, 'Response_Save_RFC_CSV@8')
        response_save_rfc_csv.argtypes = [c_char_p, c_bool]
        return response_save_rfc_csv


def main():
    cur_path = os.path.dirname(__file__)
    lib = ResponseDllWrapper(lib_name='libresponse_p_gw.dll')
    
    # prepare
    response_prepare = lib.get_response_prepare()
    input_filename = os.path.join(cur_path, 'response_input.json')
    res = response_prepare(bytes(input_filename, 'utf-8'), 42)
    print(f'prepare {res=}')

    # calc and save
    response_calculate = lib.get_response_calculate()
    response_save_rfc_csv = lib.get_response_save_rfc_csv()
    output_filename = os.path.join(cur_path, 'response_output.csv')
    is_first = True
    for e in [0.5, 1.0]:
        res = response_calculate(1000, e, 0.001)
        response_save_rfc_csv(bytes(output_filename, 'utf-8'), not is_first)
        is_first = False
    print('done')


if __name__ == '__main__':
    main()    
