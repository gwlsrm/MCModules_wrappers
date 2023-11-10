import os.path
import sys
import typing as tp
from ctypes import CDLL, RTLD_GLOBAL, POINTER, byref, c_int, c_char_p


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


class RespapproxDllWrapper:
    def __init__(self, path_to_dll: tp.Optional[str] = None, lib_name: tp.Optional[str] = None) -> None:
        if path_to_dll is None:
            path_to_dll = os.getcwd()
        if lib_name is None:
            lib_name = self._auto_select_lib_name(path_to_dll)
        self._lib = CDLL(os.path.join(path_to_dll, lib_name), RTLD_GLOBAL)
        # init_single
        self._init_single_json = _get_attribute(self._lib, ['init_single_json', 'init_single_json@4'])
        self._init_single_json.argtypes = [c_char_p]
        self._init_single_json.restype = c_int
        # init
        self._init_json = _get_attribute(self._lib, ['init_json', 'init_json@4'])
        self._init_json.argtypes = [c_char_p]
        self._init_json.restype = c_int
        # calculate
        self._calculate = _get_attribute(self._lib, ['calculate', 'calculate@4'])
        self._calculate.argtypes = [c_int]
        # calculate all
        self._calculate_all = _get_attribute(self._lib, ['calculate_all', 'calculate_all@0'])
        # get channel
        self._get_channel = _get_attribute(self._lib, ['get_channel', 'get_channel@0'])
        # stop
        self._stop = _get_attribute(self._lib, ['stop', 'stop@0'])
        # close
        self._close = _get_attribute(self._lib, ['close', 'close@0'])

    @staticmethod
    def _auto_select_lib_name(path_to_dll: str):
        for lib_name in ['respapprox.dll', 'librespapprox.dll', 'librespapprox.so']:
            if os.path.exists(os.path.join(path_to_dll, lib_name)):
                return lib_name
        raise AttributeError(f'cannot find respapprox library in "{path_to_dll}"')

    def init_single_json(self, input_filename: str) -> int:
        return self._init_single_json(bytes(input_filename, 'utf-8'))

    def init_json(self, input_filename: str) -> int:
        return self._init_json(bytes(input_filename, 'utf-8'))

    def calculate(self, channel_num: int) -> None:
        return self._calculate(channel_num)

    def calculate_all(self) -> None:
        return self._calculate_all()

    def get_channel(self) -> int:
        return self._get_channel()

    def stop(self):
        self._stop()

    def close(self):
        self._close()


def main():
    cur_path = os.getcwd()
    lib = RespapproxDllWrapper()

    # stop
    lib.stop()
    lib.close()
    print('close successfull')

    # init single
    input_filename = os.path.join(cur_path, 'respapprox_input.json')
    res = lib.init_single_json(input_filename)
    if res > 0:
        print("Respprox init single error {}".format(res))
        sys.exit()
    channels_number = -res
    print("Initialized, channels number=", channels_number)
    # # close
    # lib.close()

    # # init
    # res = lib.init_json(input_filename)
    # if res > 0:
    #     print("Respprox init error {}".format(res))
    #     sys.exit()
    # channels_number = -res
    # print("Initialized, channels number=", channels_number)

    # calculate
    for ch in range(channels_number):
        lib.calculate(ch)
    lib.close()

    print('done')


if __name__ == '__main__':
    main()
