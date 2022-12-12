import os.path
import sys
import typing as tp
from ctypes import CDLL, RTLD_GLOBAL, POINTER, c_int, c_bool, c_double, c_char_p

from read_output_bin import convert_from_bin_to_txt


PREPARE_ERROR_CODES = [
    "",
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


class AppspecDllWrapper:
    def __init__(self, path_to_dll: tp.Optional[str] = None, lib_name: tp.Optional[str] = None) -> None:
        if path_to_dll is None:
            path_to_dll = os.getcwd()
        if lib_name is None:
            lib_name = self._auto_select_lib_name(path_to_dll)
        self._lib = CDLL(os.path.join(path_to_dll, lib_name), RTLD_GLOBAL)
        # efficiency
        # prepare
        self._prepare_efficiency_calculation = _get_attribute(
            self._lib,
            ['prepare_efficiency_calculation@20', 'prepare_efficiency_calculation']
        )
        self._prepare_efficiency_calculation.argtypes = [c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), c_bool]
        # calculate
        self._calculate_efficiency = _get_attribute(self._lib, ['calculate_efficiency@40', 'calculate_efficiency'])
        self._calculate_efficiency.argtypes = [c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double)]
        self._calculate_efficiency.restype = c_double
        # reset
        self._reset_efficiency_calculation = _get_attribute(
            self._lib,
            ['reset_efficiency_calculation@0', 'reset_efficiency_calculation']
        )
        # spectrum
        self._calc_apparatus_spectrum = _get_attribute(self._lib, ['calc_apparatus_spectrum@4', 'calc_apparatus_spectrum'])
        self._calc_apparatus_spectrum.argtypes = [c_char_p]

    @staticmethod
    def _auto_select_lib_name(path_to_dll: str):
        for lib_name in ['appspec.dll', 'libappspec.dll', 'libappspec.so']:
            if os.path.exists(os.path.join(path_to_dll, lib_name)):
                return lib_name
        raise AttributeError(f'cannot find appspec library in "{path_to_dll}"')

    def prepare_efficiency_calculation(self, arrays_size: int, energy_array: tp.List[float],
                                       nfep_array: tp.List[float], dfep_array: tp.List[float],
                                       is_log: bool) -> None:
        return self._prepare_efficiency_calculation(arrays_size, energy_array, nfep_array, dfep_array, is_log)

    def calculate_efficiency(self, energy: float, peak_count_rate: float, dpeak_count_rate: float,
                             peak_intensity: float, efficiency: float, defficiency: float) -> tp.Tuple[tp.List[float], tp.List[float], int]:
        efficiency = []
        defficiency = []
        error_num = self._calculate_efficiency(energy, peak_count_rate, dpeak_count_rate, peak_intensity,
                                          efficiency, defficiency)
        return efficiency, defficiency, error_num

    def reset_efficiency_calculation(self) -> None:
        self._reset_efficiency_calculation()

    def calc_apparatus_spectrum(self, input_filename: str) -> int:
        return self._calc_apparatus_spectrum(bytes(input_filename, 'utf-8'))


def main():
    cur_path = os.getcwd()
    lib = AppspecDllWrapper()

    # calc
    input_filename = os.path.join(cur_path, 'appspec_input.json')
    res = lib.calc_apparatus_spectrum(input_filename)
    if res:
        print("Apparatus spectrum calculation error {}".format(res))
        sys.exit()

    convert_from_bin_to_txt('appspec_output.bin', 'appspec_output.txt')

    print('done')


if __name__ == '__main__':
    main()
