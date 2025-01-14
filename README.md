# MCModules wrappers

Python wrappers to [lsrm](http://lsrm.ru/en/) Monte-Carlo calculation libraries:

- tccfcalc.dll
- response.dll
- physspec.dll

They are intended for testing MC-calculation libraries.

### Install

- copy code from github.
- install requirements: `pip install -r requirements.txt`
- copy calculation dlls (*.so) to the corresponding directories, e.g. copy `tccfcalc.dll` (or `libtccfcalc.so`) to tccfcalc_wrapper.
- copy `Lib` directory to the corresponding directories, e.g. copy `Lib` from EffCalcMC to tccfcalc_wrapper.


### tccfcalc wrapper

wrapper for tccfcalc.dll (calculation library for EffCalcMC)

Example: effcalc.py run:

```bash
python effcalc.py <arguments>
positional arguments:
  positional            element Z, A, M

optional arguments:
  -h, --help            show this help message and exit
  -n NUCLIDE, --nuclide NUCLIDE
                        nuclide as string, e.g. Co-60 or Cs-137m
  -N HISTORIES, --histories HISTORIES
                        calculation histories, thsnds
  -s SEED, --seed SEED  seed for random generator, default = 0 <- random seed
  -a ANALYZER, --analyzer ANALYZER
                        analyzer filename (*.ain), will calculate spectrum
  -v, --verbose         verbose mode
```

Test tccfcalc:
```bash
python python tccfcalc_test.py
```


### response wrapper

wrapper for response.dll (calculation library for EffMaker)

Example: response.py run:

```sh
python response.py <arguments>
positional arguments:
  positional            energy grid parameters: minimal energy, maximal energy, points

optional arguments:
  -h, --help            show this help message and exit
  --grid_log            is energy grid logarithmic
  -N HISTORIES, --histories HISTORIES
                        calculation histories, thsnds
  -s SEED, --seed SEED  seed for random generator, default = 0 <- random seed
  -v, --verbose         verbose mode
```

Test tccfcals:

```bash
python response_test.py
```


### physspec wrapper

wrapper for physspec.dll (calculation library for EffMaker)

Example: physspec.py run:

```sh
python physspec.py <arguments>
optional arguments:
  -h, --help            show this help message and exit
  -N HISTORIES, --histories HISTORIES
                        calculation histories, thsnds
  -s SEED, --seed SEED  seed for random generator, default = 0 <- random seed
  -v, --verbose         verbose mode
  --pretty              pretty json output file
```

Test physspec:

```bash
python physspec_test.py
```
