# MCModules wrappers
Python wrappers to [lsrm](http://lsrm.ru/en/) Monte-Carlo calculation libraries:

- tccfcalc.dll
- response.dll
- physspec.dll



### tccfcalc wrapper

wrapper for tccfcalc.dll (calculation library for EffCalcMC)

Example: effcalc.py run:

```sh
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

