# MCModules wrappers
Python wrappers to [lsrm](http://lsrm.ru/en/) Monte-Carlo calculation libraries:

- tccfcalc_wrapper
- response_wrapper



### tccfcalc_wrapper

wrapper for tccfcalc.dll (calculation library for EffCalcMC)

run:

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



### response_wrapper

wrapper for response.dll (calculation library for EffMaker)

