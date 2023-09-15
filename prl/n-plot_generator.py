import math
import sys

import numpy as np
import typer
from rich import print
from pandas import DataFrame
from pathlib import Path

from rich.pretty import pprint
import pickle
import os
app = typer.Typer(add_completion=False)


def get_percentiles(percentiles_list, distribution):
    cumulatives = [distribution[0]]
    for i in range(1,len(distribution)):
        cumulatives.append(distribution[i] + cumulatives[i-1])

    def find_cumulative(val):
        for j in range(len(cumulatives)):
            if cumulatives[j] >= val:
                return j + 1
        else:
            return len(cumulatives)

    return [find_cumulative(p) for p in percentiles_list]

# Using typer here: https://typer.tiangolo.com/tutorial/arguments/optional/
@app.command()
def main(
        cache_dir: Path = typer.Option(
            'cached', "--cache-dir", help="Path to cache result dict to",
            exists=False, dir_okay=True, readable=True, file_okay=False
        ),
):
    """
    Generates the plot over the number of vehicles in the paper.
    """

    # pick a series
    n_start = 400
    n_stop = 1000
    n_step = 100
    n_range = range(n_start, n_stop+1, n_step)

    e_range = [30]

    print(f'I will plot for a range of number of vehicles in: {str(n_range)} and a range of possible time epochs (T_PRL) in: {str(e_range)}')

    # p range for manual attackers
    honest1 = 0.000000116323325
    honest2 = 0.000053299160406
    honest1_attacker1 = [0.000007813830433, 0.000015511337541, 0.000038603858866, 0.000077091394407, 0.000154066465489]
    honest2_attacker1 = [0.000060464839143, 0.000067630517880, 0.000089127554093, 0.000124955947779, 0.000196612735153]

    # For the p's in this graph we only pick the two honest probabilities and pair them with the 20% attacker
    p_range = [honest1]
    p_range.append(honest1_attacker1[4])
    p_range.append(honest2)
    p_range.append(honest2_attacker1[4])

    attacker_occurrences = ['1%', '2%', '5%', '10%', '20%']
    plot_xlabels_dict = { honest1: 'Scenario 1 - 0%', honest2: 'Scenario 2 - 0%' }
    for i in range(len(honest1_attacker1)):
        plot_xlabels_dict[honest1_attacker1[i]] = f'Scenario 1 - {attacker_occurrences[i]}'
    for i in range(len(honest2_attacker1)):
        plot_xlabels_dict[honest2_attacker1[i]] = f'Scenario 2 - {attacker_occurrences[i]}'
    plot_xlabels = []
    print("I will use the following probabilities:")
    print(plot_xlabels_dict)
    for prob in p_range:
        plot_xlabels.append(plot_xlabels_dict[prob])

    print(f'Parsing all stationary distribution files in directory "{cache_dir}"...')
    all_dicts = []
    for expected_e in e_range:
        for expected_p in p_range:
            for expected_n in n_range:
                expected_filename = f'n{expected_n}_e{expected_e}_p{expected_p:.15f}.stat_dist'
                if expected_filename in os.listdir(cache_dir):
                    print(f'Including {expected_filename}')
                    with (cache_dir / expected_filename).open('rb') as f:
                        all_dicts.append(pickle.load(f))
                else:
                    print(f'Could not find file {expected_filename}! Aborting.')
                    sys.exit(-1)

    print('The list of markov matrices I loaded is (tuples of (n,T_PRL,p)):')
    print(str([(dd['n'], dd['e'], dd['p']) for dd in all_dicts]))

    percentiles = [0.99]
    print(f'Percentiles for lower/middle/upper are {str(percentiles)}')
    all_percentiles = [get_percentiles(percentiles, d['dist']) for d in all_dicts]
    print("Above percentiles for each markov matrix:")
    print(all_percentiles)

    plot_data = []
    plot_labels = []

    for i in range(len(p_range)):
        data = []

        for j in range(len(n_range)):
            append_tuple = all_percentiles[(i*len(n_range))+j]
            data.append(append_tuple[0])

        plot_data.append(data)
        plot_labels.append(plot_xlabels_dict[p_range[i]])


    import matplotlib.pyplot as plt
    marker_styles=['o','^','s','D','p','+','*']

    fig, ax = plt.subplots()
    plot_range = n_range
    for i in range(len(plot_data)):
        ax.scatter(plot_range, plot_data[i], marker=marker_styles[i])

    plt.legend(plot_labels, loc="upper left")

    import tikzplotlib
    filename = f"n-plot_e{e_range[0]}"
    tikzplotlib.save(filename + '.tex')
    plt.title(filename)
    plt.savefig(filename + '.png')
    print(f'Saved plot to {filename}[.tex, .png]')

if __name__ == "__main__":
    app()
