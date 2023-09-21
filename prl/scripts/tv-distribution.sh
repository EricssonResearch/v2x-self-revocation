#!/bin/bash

set -e

echo "Generating data for T_v distribution (Fig. 7)."
for value in {30,150,300,900}
do
python3 generate_plots.py -e $value -n 800 -p 0.000196612735153
done

echo "Data generated. Generating distribution."
python3 tv-distribution.py