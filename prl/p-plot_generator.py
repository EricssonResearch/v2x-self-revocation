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
    # print(f'Cumulatives are {cumulatives[0:6]}')

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

    # print(all_dicts)

    # pick a series
    # here let's do n=100 to 1000 and e = 5 and p = 0.0001
    n_start = 400
    n_stop = 400
    n_step = 100
    n_range = range(n_start, n_stop+1, n_step)
    n_range = [400]

    e_start = 400
    e_stop = 400
    e_step = 1
    e_range = range(e_start, e_stop+1, e_step)
    e_range = [300]

    float_digits = 10
    p_start = 0.0001
    p_stop = 0.001
    p_step = 0.0001
    p_range = [round(f, float_digits) for f in np.arange(p_start, p_stop+p_step, p_step)]
    #
    # p range for manual attackers
    honest1 = 0.000000116323325
    honest2 = 0.000053299160406
    honest1_attacker1 = [0.000007813830433, 0.000015511337541, 0.000038603858866, 0.000077091394407, 0.000154066465489]
    honest2_attacker1 = [0.000060464839143, 0.000067630517880, 0.000089127554093, 0.000124955947779, 0.000196612735153]

    p_range = [honest1]
    p_range.extend(honest1_attacker1)
    p_range.append(honest2)
    # p_range.extend(honest1_attacker2)
    p_range.extend(honest2_attacker1)
    # p_range.extend(honest2_attacker2)
    # p_range = sorted(p_range)
    print(p_range)

    attacker_occurrences = ['1%', '2%', '5%', '10%', '20%']
    plot_xlabels_dict = { honest1: 'Scenario 1 - 0%', honest2: 'Scenario 2 - 0%' }
    for i in range(len(honest1_attacker1)):
        plot_xlabels_dict[honest1_attacker1[i]] = f'Scenario 1 - {attacker_occurrences[i]}'
    for i in range(len(honest2_attacker1)):
        plot_xlabels_dict[honest2_attacker1[i]] = f'Scenario 2 - {attacker_occurrences[i]}'
    plot_xlabels = []
    print(plot_xlabels_dict)
    for prob in p_range:
        plot_xlabels.append(plot_xlabels_dict[prob])

    def fits_criteria(filename):
        split = filename.split('_')
        file_n = int(split[0][1:])
        file_e = int(split[1][1:])
        file_p = round(float('0.' + split[2][1:].split('.')[1]), float_digits)
        # print(f'Checking {file_n} {file_e} {file_p}')
        if file_n in n_range \
                and file_e in e_range \
                and file_p in p_range:
            return True
        # elif file_n in range(n_start, n_stop+1, n_step) \
        #         and file_e in range(e_start, e_stop+1, e_step):
        #     print(f'Not including {filename} because {file_p} does not fit')

        return False


    print(f'Parsing all stationary distribution files in {cache_dir}')
    all_dicts = []
    # for f in os.listdir(cache_dir):
    #     if str(f).endswith('stat_dist') and fits_criteria(str(f)):
    #         print(f'Including {f}')
    #         with (cache_dir / f).open('rb') as f:
    #             all_dicts.append(pickle.load(f))
    for expected_p in p_range:
        for expected_n in n_range:
            for expected_e in e_range:
                expected_filename = f'n{expected_n}_e{expected_e}_p{expected_p:.15f}.stat_dist'
                if expected_filename in os.listdir(cache_dir):
                    print(f'Including {expected_filename}')
                    with (cache_dir / expected_filename).open('rb') as f:
                        all_dicts.append(pickle.load(f))
                else:
                    print(f'Could not find file {expected_filename}! Aborting.')
                    sys.exit(-1)


    # print(all_dicts)
    # all_dicts.sort(key=lambda dd : dd['p'])
    # all_dicts.sort(key=lambda dd : dd['e'])
    # all_dicts.sort(key=lambda dd : dd['n'])
    print('List is:')
    print(str([(dd['n'], dd['e'], dd['p']) for dd in all_dicts]))


    percentiles = [0.75, 0.9, 0.9999]
    print(f'Percentiles for lower/middle/upper are {str(percentiles)}')
    all_percentiles = [get_percentiles(percentiles, d['dist']) for d in all_dicts]
    print(all_percentiles)
    print('Medians (indeces with the highest probability):')
    print([dd['dist'].index(max(dd['dist'])) for dd in all_dicts])

    # get all_percentiles as set
    all_percentiles_set = set([item for tuple in all_percentiles for item in tuple])

    plot_data = []
    plot_labels = []

    def add_percentile_to_plot(percentile_index):
        for i in range(len(e_range)):
            data = []

            for j in range(len(p_range)):
                append_tuple = all_percentiles[(i*len(p_range))+j]
                data.append(append_tuple[percentile_index])

            plot_data.append(data)
            plot_labels.append(f'{percentiles[percentile_index]*100:g}th percentile')

    for i in range(len(percentiles)):
        add_percentile_to_plot(i)

    import matplotlib.pyplot as plt
    marker_styles=['o','^','s','D','p','+','*']

    fig, ax = plt.subplots()
    plot_range = list(range(len(p_range)))
    for i in range(len(plot_data)):
        ax.scatter(plot_range, plot_data[i], marker=marker_styles[i])

    # dot_prod[0].plot(kind='bar')
    # ax.axis('equal')

    # plt.yticks(range(0, max(all_percentiles_set)+1))
    plt.xticks(plot_range, plot_xlabels, rotation=45)
    plt.legend(plot_labels, loc="upper left")
    # plt.title(f'Maximum PRL sizes for n={n_start} and varying probabilities of revocation')

    import tikzplotlib
    filename = f"n{n_range[0]}_e{e_range[0]}"
    tikzplotlib.save(filename + '.tex')
    plt.title(filename)
    plt.savefig(filename + '.png')
    # plt.show()

if __name__ == "__main__":
    app()
