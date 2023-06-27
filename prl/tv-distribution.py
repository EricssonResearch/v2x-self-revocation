import sys

import typer
from rich import print
from pathlib import Path

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
    # value of n (i.e., number of pseudonyms)
    n = 800

    # value of p using Scenario 2 with 20% of attackers
    p = 0.000196612735153

    # values of e (i.e., T_prl)
    e_range = [30, 150, 300, 900]

    print(f'Parsing all stationary distribution files in {cache_dir}')
    all_dicts = []
    for expected_e in e_range:
        expected_filename = f'n{n}_e{expected_e}_p{p:.15f}.stat_dist'
        if expected_filename in os.listdir(cache_dir):
            print(f'Including {expected_filename}')
            with (cache_dir / expected_filename).open('rb') as f:
                all_dicts.append(pickle.load(f))
        else:
            print(f'Could not find file {expected_filename}! Aborting.')
            sys.exit(-1)

    print('List is:')
    print(str([(dd['n'], dd['e'], dd['p']) for dd in all_dicts]))

    # using the 99 percentile
    percentiles = [0.5, 0.75, 0.9, 0.99, 0.9999]
    print(f'Percentiles are {str(percentiles)}')
    all_percentiles = [get_percentiles(percentiles, d['dist']) for d in all_dicts]

    print("Elements in PRL:")
    all_percentiles = list(zip(*all_percentiles))

    for i in range(len(percentiles)):
        print(f"{percentiles[i]}: {all_percentiles[i]}")

 
if __name__ == "__main__":
    app()