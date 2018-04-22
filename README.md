# clm_to_cmip

A cli utility to transform E3SM land model output into CMIP compatible data.

## clm_singlevar_ts

Extract single variables from clm2.h0 files into single-variable-per-file time series.

usage: clm_singlevar_ts.py [-h] [-v VAR_LIST [VAR_LIST ...]] -c CASE_ID -i
                           INPUT_PATH -o OUTPUT_PATH -s START_YEAR -e END_YEAR
                           [-n NUM_PROC] [-N]
```
optional arguments:
  -h, --help            show this help message and exit
  -v VAR_LIST [VAR_LIST ...], --var-list VAR_LIST [VAR_LIST ...]
                        space sepperated list of variables, use 'all' to
                        extract all variables
  -c CASE_ID, --case-id CASE_ID
                        name of case, e.g.
                        20180129.DECKv1b_piControl.ne30_oEC.edison
  -i INPUT_PATH, --input-path INPUT_PATH
                        path to input directory
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        path to output directory
  -s START_YEAR, --start-year START_YEAR
                        first year to extract
  -e END_YEAR, --end-year END_YEAR
                        last year to split
  -n NUM_PROC, --num-proc NUM_PROC
                        number of parallel processes, default = 6
  -N, --proc-vars       set the number of process to the number of variables
```

## clm_to_cmip

Transform clm style time series variables into cmip compatible data
```
usage: clm_to_cmip.py [-h] -v VAR_LIST [VAR_LIST ...] -c CASEID -i INPUT -o
                      OUTPUT [-n NUM_PROC] [-H HANDLERS]

optional arguments:
  -h, --help            show this help message and exit
  -v VAR_LIST [VAR_LIST ...], --var-list VAR_LIST [VAR_LIST ...]
                        space seperated list of variables to convert from clm
                        to cmip
  -c CASEID, --caseid CASEID
                        name of case e.g.
                        20180129.DECKv1b_piControl.ne30_oEC.edison
  -i INPUT, --input INPUT
                        path to directory containing clm data with single
                        variables per file
  -o OUTPUT, --output OUTPUT
                        where to store cmorized outputoutput
  -n NUM_PROC, --num-proc NUM_PROC
                        optional: number of processes, default = 6
  -H HANDLERS, --handlers HANDLERS
                        optional: path to cmor handlers directory, default =
                        ./cmor_handlers
```