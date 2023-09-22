import sys
import os

import typer
from rich import print
from pathlib import Path
import pickle

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
            'cached', "--cache-dir", help="Path to cache directory",
            exists=False, dir_okay=True, readable=True, file_okay=False
        ),
        plot_dir: Path = typer.Option(
            'plots', "--path", help="Path to folder to write plots",
            exists=False, dir_okay=True, file_okay=False, readable=True, writable=True,
        )
):
    """
    Generates the plot over the probabilities in the paper.
    """

    # create plot_dir if not exists
    print(f'Creating dir {str(plot_dir)}')
    plot_dir.mkdir(parents=True, exist_ok=True)

    n_range = [800]

    e_range = [30]

    print(f'I will plot for a range of number of pseudonyms in: {str(n_range)} and a range of possible time epochs (T_PRL) in: {str(e_range)}')

    # p range for manual attackers
    honest1 = 0.000000116323325
    honest2 = 0.000053299160406
    honest1_attacker1 = [0.000007813830433, 0.000015511337541, 0.000038603858866, 0.000077091394407, 0.000154066465489]
    honest2_attacker1 = [0.000060464839143, 0.000067630517880, 0.000089127554093, 0.000124955947779, 0.000196612735153]

    p_range = [honest1]
    p_range.extend(honest1_attacker1)
    p_range.append(honest2)
    p_range.extend(honest2_attacker1)

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

    print('The list of markov matrices I loaded is (tuples of (n,T_PRL,p)):')
    print(str([(dd['n'], dd['e'], dd['p']) for dd in all_dicts]))

    percentiles = [0.75, 0.9, 0.9999]
    print(f'Percentiles for lower/middle/upper are {str(percentiles)}')
    all_percentiles = [get_percentiles(percentiles, d['dist']) for d in all_dicts]
    print("Above percentiles for each markov matrix:")
    print(all_percentiles)
    print('Medians (indices with the highest probability):')
    print([dd['dist'].index(max(dd['dist'])) for dd in all_dicts])

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

    plt.xticks(plot_range, plot_xlabels, rotation=45)
    plt.legend(plot_labels, loc="upper left")

    filename = f"p-plot_n{n_range[0]}_e{e_range[0]}"
    filename_path = os.path.join(plot_dir, filename)

    plt.title(filename)
    plt.savefig(filename_path + '.png')
    print(f'Saved plot to {filename_path}[.tex, .png]')

    import tikzplotlib
    tikzplotlib.save(filename_path + '.tex')

if __name__ == "__main__":
    app()
