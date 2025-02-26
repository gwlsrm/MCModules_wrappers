import os.path
import sys
import typing as tp
from ctypes import CDLL, RTLD_GLOBAL, POINTER, Structure, \
    c_int, c_bool, c_double, c_char_p


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
    "Error while parsing input json file",
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


def _get_attribute(lib, attributes: tp.List[str]):
    """
        tries to get exported attribute from attributes list
        returns first successful
    """
    for attribute in attributes:
        try:
            res = getattr(lib, attribute)
            return res
        except AttributeError:
            continue
    raise AttributeError('Cannot find good symbol from ' + str(attributes))


class ResponseDllWrapper:
    def __init__(self, path_to_dll: tp.Optional[str] = None, lib_name: tp.Optional[str] = None) -> None:
        if path_to_dll is None:
            path_to_dll = os.getcwd()
        if lib_name is None:
            lib_name = self._auto_select_lib_name(path_to_dll)
        self._lib = CDLL(os.path.join(path_to_dll, lib_name), RTLD_GLOBAL)
        # prepare
        self._response_prepare = _get_attribute(self._lib, ['Response_Prepare_Json@8', 'Response_Prepare_Json'])
        self._response_prepare.argtypes = [c_char_p, c_int]
        # calculate
        self._response_calculate = _get_attribute(self._lib, ['Response_Calculate@20', 'Response_Calculate'])
        self._response_calculate.argtypes = [c_int, c_double, c_double]
        self._response_calculate.restype = POINTER(CalculationResults)
        # reset
        self._response_reset = _get_attribute(self._lib, ['Response_Reset@0', 'Response_Reset'])
        # save response
        self._response_save_rfc_csv = _get_attribute(self._lib, ['Response_Save_RFC_CSV@8', 'Response_Save_RFC_CSV'])
        self._response_save_rfc_csv.argtypes = [c_char_p, c_bool]

    @staticmethod
    def _auto_select_lib_name(path_to_dll: str):
        for lib_name in ['response_p_gw.dll', 'libresponse_p_gw.dll', 'libresponse_p_gw.so']:
            if os.path.exists(os.path.join(path_to_dll, lib_name)):
                return lib_name
        raise AttributeError(f'cannot find response library in "{path_to_dll}"')

    def response_prepare(self, input_filename: str, seed: int) -> int:
        return self._response_prepare(bytes(input_filename, 'utf-8'), seed)

    def response_calculate(self, histories: int, energy_MeV: float, de: float):
        return self._response_calculate(histories, energy_MeV, de)

    def response_reset(self) -> None:
        self._response_reset()

    def response_save_rfc_csv(self, output_filename: str, write_header: bool) -> None:
        self._response_save_rfc_csv(bytes(output_filename, 'utf-8'), write_header)


def main():
    cur_path = os.getcwd()
    lib = ResponseDllWrapper()

    # prepare
    input_filename = os.path.join(cur_path, 'response_input.json')
    error_num = lib.response_prepare(input_filename, 42)
    if error_num:
        error_msg = PREPARE_ERROR_CODES[error_num] if error_num < len(PREPARE_ERROR_CODES) else ''
        print(f'Prepare error #{error_num}: {error_msg}')
        sys.exit()

    # calc and save
    output_filename = os.path.join(cur_path, 'response_output.csv')
    is_first = True
    for e in [0.5, 1.0]:
        lib.response_calculate(1000, e, 0.001)
        lib.response_save_rfc_csv(output_filename, not is_first)
        is_first = False
    print('done')


if __name__ == '__main__':
    main()
