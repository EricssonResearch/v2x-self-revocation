import math
import sys

import numpy as np
import pandas
import typer
from rich import print
from pandas import DataFrame
from pathlib import Path


def draw_as_tikz(matrix, file):
    """
    Draw the specified markov chain as a transition graph and output it as LaTeX code with tikz.
    """
    tex = '''
\\documentclass[]{article}
\\usepackage[a0paper]{geometry}
\\pagenumbering{gobble}
\\usepackage{tikz}
\\usepackage{amsmath}
\\usetikzlibrary{shapes, arrows, positioning}
\\begin{document}
\\begin{tikzpicture}[->,>=stealth',shorten >=2pt, line width=2pt, node distance=5cm, style = {minimum size = 20mm}]
\\tikzstyle{every node}=[font =\\huge]
'''

    tex +=  '\\node[circle, draw](n0){0};\n'
    angle_counter = 90
    for i in range(1,len(matrix)):
        tex += f'\\node[circle, draw](n{i})[right = of n{i-1}] {{{i}}};\n'
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i == j:
                tex += f'\\path(n{i}) edge [loop right] node {{{matrix[i][j]:.3f}}} (n{i});\n'
            elif i>j:
                tex += f'\\draw[->] (n{i}) to [out=-{angle_counter}, in=-{angle_counter}, edge node={{node [below=-.5cm] {{{matrix[i][j]:.3f}}}}}] (n{j});\n'
            elif i<j:
                tex += f'\\draw[->] (n{i}) to [out={angle_counter}, in={angle_counter}, edge node={{node [above=-.5cm] {{{matrix[j][i]:.3f}}}}}] (n{j});\n'
    tex +="""
\\end{tikzpicture}
\\end{document}
"""

    with  open(file, 'w') as f:
        f.writelines(tex)


app = typer.Typer(add_completion=False)



# Using typer here: https://typer.tiangolo.com/tutorial/arguments/optional/
@app.command()
def main(
        n: int = typer.Option(
            2, "-n",
            help="Size of the PRL.",
        ),
        e: int = typer.Option(
            2, "-e",
            help="Number of epochs that a certificate stays in the PRL.",
        ),
        p: float = typer.Option(
            0.1, "-p",
            help="Probability of a certificate being revoked.",
        ),
        tikz_file: Path = typer.Option(
            None, "-f", help="Give a path to write the transition graph to a tikz file (Fig. 15 in paper).",
                exists=False, dir_okay=False, readable=True,
        ),
        plot: bool = typer.Option(
            False, "-g",
            help="Set to true to plot the state probabilities into a bar graph.",
        ),
        plot_file: Path = typer.Option(
            None, "--plot-path", help="Path to plot file to write bar graph to",
                exists=False, dir_okay=False, readable=True,
        ),
        cache_dir: Path = typer.Option(
            None, "--cache-dir", help="Path to cache directory",
            exists=False, dir_okay=True, readable=True, file_okay=False
        ),
        allow_cached: bool = typer.Option(
            False, '--allow-cached', help='Skip calculations if cached folder already contains data of this run.'
        ),
        force_cached: bool = typer.Option(
            False, '--force-cached', help='Enforce to skip calculations and use cached data. Abort otherwise.'
        )
):
    '''
    Calculate a single markov matrix for a pseudonym revocation list of specific given parameters. In the paper graphs, this equates to one of the dots, i.e., to one data point.
    '''

    actual_n = n+1
    loss_probabilities = []
    gain_probabilities = []

    # Keep a cache of already calculated tuples to speed up the process
    gain_cache = {}
    loss_cache = {}

    # Filename patterns
    filename_base = f'n{n}_e{e}_p{p:.15f}'
    filename_stat_dist = filename_base + '.stat_dist'
    filename_markov = filename_base + '.markov'

    def get_gain(i, k):
        if (i, k) not in gain_cache:
            gain_cache[(i, k)] = math.comb(n - i, k) * math.pow(p, k) * math.pow(1 - p, n - i - k)
        return gain_cache[(i, k)]

    def get_loss(i, k):
        if (i,k) not in loss_cache:
            val = math.comb(i, k)
            if val > 0:
                val = val * math.pow(1 / e, k) * math.pow(1 - (1 / e), i - k)
            loss_cache[(i, k)] = val
        return loss_cache[(i,k)]

    def get_markov(i, j):
        prob = 0.0
        for l in range(max(i-j, 0), i+1):
            try:
                this_prob = get_loss(i,l) * get_gain(i, abs(j-i+l))
                prob += this_prob
            except KeyError:
                pass
        return prob

    def get_matrix(func, name):
        if name != 'markov':
            print(f'Probabilities to {name} a certificate at each markov step: ')
        else:
            print('Probabilities for the markov matrix')
        # Calculate the n x n matrix based on the given function
        matrix = [[func(i, j) for j in range(actual_n)] for i in range(actual_n)]
        # For pretty printing, use pandas and add a sum column
        original_df = DataFrame(matrix)

        df = original_df.copy()
        df.loc[:,'Sum'] = df.sum(axis=1)

        print(df)
        print('')
        return original_df

    print(f'Modeling PRL as a markov chain.')
    print(f'Parameters:')
    params = {'Size of PRL (n)': n,
              'Number of epochs that a cerificate stays in PRL (e)' : e,
              'Probability for a certificate to be revoked at each epoch (p)': p
              }
    print(params)

    markov_process = None
    loss_probabilities = None
    gain_probabilities = None

    if (allow_cached or force_cached) and cache_dir:
        desired_file = cache_dir / filename_markov
        if desired_file.exists():
            print(f'Using cached file {desired_file}')
            markov_process = pandas.read_pickle(desired_file)

    if markov_process is None:
        if force_cached:
            print('No cached data read. Aborting instead.')
            sys.exit(-1)
        loss_probabilities = get_matrix(get_loss, 'lose')
        gain_probabilities = get_matrix(get_gain, 'gain')
        markov_process =     get_matrix(get_markov, 'markov')

    if tikz_file:
        print(f'Writing tikz to file {tikz_file}')
        draw_as_tikz(markov_process, tikz_file)


    # Next, calculate the stationary distribution of the markov matrix
    # This will give us the distribution that occurs after an arbitrary amount of steps (after ramp up period)

    # https://stackoverflow.com/a/67172991
    # https://stephens999.github.io/fiveMinuteStats/stationary_distribution.html
    """
    x − x P = 0
    x (I−P) = 0 
    (I−P)^T * x^T = 0
    add a row of all 1’s to (I−P)^T
    add a 1 to the last element of the zero vector b
    solve A x = b 
    """
    # The intuitive formula is this:
    # # Get identity matrix of actual_x squared
    # I = np.eye(actual_n)
    # # Get A as P.T -I
    # A = markov_process.T - I
    # A = np.vstack([A, np.ones((1, len(A)))])  # add row of ones
    # b = np.zeros(len(A))  # prepare solution vector
    # b[-1] = 1.0  # add a one to the last entry
    # sol = np.linalg.solve(A.T @ A, A.T @ b)  # solve the normal equation
    # print(sol)
    # print(np.sum(sol))

    # However, we can also solve this equation:
    # Get identity matrix of actual_x squared
    I = np.eye(actual_n)
    # Get A as I.T - P.T
    A = I.T - markov_process.T
    # Add row of 1s to A
    A = np.vstack([A, np.ones((1, len(A)))])
    # Prepare zero vector with a 1 at end
    b = np.zeros(len(A))  # prepare solution vector
    b[-1] = 1.0  # add a one to the last entry
    # Solve A x = b
    sol2 = np.linalg.lstsq(A, b, rcond=None)  # solve the normal equation
    print("Markov matrix:")
    print(sol2[0])
    print("Sum (should sum to 1 but there is always an approxmiation error):")
    print(np.sum(sol2[0]))

    # print('diff')
    # print(sol2[0] - sol)
    # print(np.sum(sol2[0] - sol))

    # For development purposes, we can also sanity check our solution like this:
    # do a double check how sane the solution is by stepping it and taking diff
    # check = sol2[0]
    # for i in range(100):
    #     check = np.dot(check, markov_process)
    # print('Diff between solution and solution after some step with the markov matrix:')
    # check_diff = sol2[0] - check
    # print(check_diff)
    # check_error = 0
    # for i in check_diff:
    #     check_error += abs(i)
    # print(f'Summed diff: {check_error}')
    # print(f'sum of check vector: {sum(check)}')

    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        stat_dist_dict = {
            'n' : n,
            'e' : e,
            'p' : p,
            'dist': list(sol2[0])
        }
        import pickle

        with (cache_dir / filename_stat_dist ).open('wb') as f:
            pickle.dump(stat_dist_dict, f)
        markov_process.to_pickle(cache_dir / filename_markov)


    if plot:
        import matplotlib.pyplot as plt
        plt.bar(range(actual_n), sol2[0])
        plt.title(f'Probability for each PRL size for n={n}, p={p}, e={e}')

        if plot_file:
            print(f'Writing plot to {str(plot_file)}')
            plt.savefig(plot_file)
        else:
            print('Showing plot:')
            plt.show()

    print('Done.')

if __name__ == "__main__":
    app()
