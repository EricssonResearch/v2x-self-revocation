#!/bin/bash

set -e

echo "Generating T_PRL plot (Fig. 10)."
for value in `seq 10 10 200`
do
python3 generate_plots.py -e $value -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153 "$@"
done

echo "Data generated. Generating plot."
python3 t-plot_generator.py "$@"