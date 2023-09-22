#!/bin/bash

set -e

echo "Generating probability plot (Fig. 6)."

python3 generate_plots.py -e 30 -n 800 -p 0.000000116323325 -p 0.000007813830433 -p 0.000015511337541 -p 0.000038603858866 -p 0.000077091394407 -p 0.000154066465489 "$@"
python3 generate_plots.py -e 30 -n 800 -p 0.000053299160406 -p 0.000060464839143 -p 0.000067630517880 -p 0.000089127554093 -p 0.000124955947779 -p 0.000196612735153 "$@"

echo "Data generated. Generating plot."
python3 p-plot_generator.py "$@"