#!/bin/bash

set -e

echo "Generating n (number of vehicles) plot (Fig. 17)."
for value in `seq 400 100 1000`
do
python3 generate_plots.py -e 30 -n $value -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
done

echo "Data generated. Generating plot."
python3 n-plot_generator.py