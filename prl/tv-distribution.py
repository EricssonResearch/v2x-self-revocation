import sys
import re
import os

import pickle
import typer
from rich import print
from pathlib import Path
import matplotlib.pyplot as plt
import tikzplotlib

app = typer.Typer(add_completion=False)

## Fixed parameters -- Check Sect. VII-C for more info ##
TV_VALUES = [30, 150, 300, 900] # Values of T_V to consider, in the X axis
NUM_PSEUDONYMS = 800 # number of pseudonyms
P = 0.000196612735153 # revocation probability of the scenario that we consider
HB_PER_TV = 30 # Heartbeats sent each T_v seconds. This is "N" in Sect. VII-C
PS_SIZE = 64 # Pseudonym size, in bytes
TS_SIZE = 8 # Timestamp size, in bytes
SIG_SIZE = 512 # Signature size, in bytes

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

def plot(plot_dir, y_prl):
    # first plot: revocation time t_eff (values in minutes)
    y_teff = [a * 2 / 60 for a in TV_VALUES]

    # second plot: frequency of HBs (values in HB/minutes)
    y_hb_freq = [HB_PER_TV / a * 60 for a in TV_VALUES]

    # third plot: size of PRL (values in KB)
    # NOTE: These values correspond to the 99.99th percentile if the PRL size
    # for each value of T_V, computed in the previous step
    y_prl = [16, 43, 71, 160]

    # fourth plot: bandwidth (values in KBit/s)
    hb_sizes = [(a * PS_SIZE + TS_SIZE + SIG_SIZE) * 1e-3 for a in y_prl] # KB
    hb_frequencies = [HB_PER_TV / a for a in TV_VALUES] # 1/s
    y_bandwidth = [a * b * 8 for a, b in zip(hb_sizes, hb_frequencies)] # KBit/s


    print(f"X values: {TV_VALUES}")
    print(f"T_eff: {y_teff}")
    print(f"HB sizes: {hb_sizes}")
    print(f"Frequency of HBs: {y_hb_freq}")
    print(f"Bandwidth: {y_bandwidth}")

    #plt.figure(figsize=(20,4))
    fig, axs = plt.subplots(2,2, sharex=True, sharey=False)
    #fig.suptitle('Impact of $T_v$ on different dimensions')

    fst = axs[0,0]
    snd = axs[0,1]
    trd = axs[1,0]
    fth = axs[1,1]

    #fst = axs[0]
    #snd = axs[1]
    #trd = axs[2]
    #fth = axs[3]

    # seaborn `colorblind` palette: 
    # ['#0173b2', '#de8f05', '#029e73', '#d55e00', '#cc78bc', '#ca9161', '#fbafe4', '#949494', '#ece133', '#56b4e9']

    # first plot
    fst.plot(TV_VALUES, y_teff, '#0173b2')
    fst.set_title('$T_{eff}$ (min)')
    fst.get_yaxis().set_label_coords(-0.1,0.5)

    # second plot
    snd.plot(TV_VALUES, y_hb_freq, '#de8f05')
    snd.set_title('HB frequency (HB/min)')
    snd.get_yaxis().set_label_coords(-0.1,0.5)

    # third plot
    trd.plot(TV_VALUES, hb_sizes, '#029e73')
    trd.set_title('HB size (KB)')
    trd.get_yaxis().set_label_coords(-0.1,0.5)

    # fourth plot
    fth.plot(TV_VALUES, y_bandwidth, '#d55e00')
    fth.set_title('Required bandwidth (KBit/s)')
    fth.get_yaxis().set_label_coords(-0.1,0.5)

    for ax in axs.flat:
        #ax.set(xlabel='$T_v$ (s)')
        ax.xaxis.set_tick_params(labelbottom=True)


    # set ticks and tick labels
    plt.xticks(TV_VALUES)
    #formatter = matplotlib.ticker.FuncFormatter(lambda s, x: f"{s/60:.1f}")
    #ax.xaxis.set_major_formatter(formatter)

    plt.subplots_adjust(left=0.12,
                        bottom=0.1,
                        right=0.95,
                        top=0.85,
                        wspace=0.4,
                        hspace=0.8)

    plt.savefig(os.path.join(plot_dir, "tv-distribution.png"), format="png")
    save_tikz(os.path.join(plot_dir, "tv-distribution.tex"), height="6cm")

def save_tikz(file, width="15cm", height="8cm"):
    tikzplotlib.save(file, strict=True, axis_width=width, axis_height=height)

    with open(file, "r") as f:
        tikz_file = f.read()

    # fix legend size
    tikz_file = tikz_file.replace("legend style={", "legend style={font=\\small,")
    
    # show tick labels
    tikz_file = tikz_file.replace("xmajorticks=false", "xmajorticks=true")
    tikz_file = tikz_file.replace("ymajorticks=false", "ymajorticks=true")

    tickstyle_regex = "([xy])tick style={(.+)}"
    matches = re.findall(tickstyle_regex, tikz_file)

    # hide ticks
    for match in matches:
        tikz_file = tikz_file.replace(
            f"{match[0]}tick style={{{match[1]}}}",
            f"{match[0]}tick style={{{match[1]},draw=none}}"
        )

    # adjust vertical spacing between plots
    tikz_file = tikz_file.replace(
        "group style={",
        "group style={vertical sep=3.5cm, horizontal sep=2.5cm,"
    )

    options = [
        "clip=false", # set clip=false to show labels outside the plot
        "label style={font=\Huge}",
        "tick label style={font=\Huge}",
        "title style={font=\Huge}"
    ]

    options_str = ",\n".join(options)
    tikz_file = tikz_file.replace(
        "}\n]",
        "},\n" + options_str + "\n]"
    )

    # TODO fix "yticklabel style": "anchor=center,yshift=6pt"

    with open(file, "w") as f:
        f.write(tikz_file)


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
    # create plot_dir if not exists
    print(f'Creating dir {str(plot_dir)}')
    plot_dir.mkdir(parents=True, exist_ok=True)

    # values of e (i.e., T_prl)
    e_range = TV_VALUES

    print(f'Parsing all stationary distribution files in {cache_dir}')
    all_dicts = []
    for expected_e in e_range:
        expected_filename = f'n{NUM_PSEUDONYMS}_e{expected_e}_p{P:.15f}.stat_dist'
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

    # plot results using the last percentile (i.e., 0.9999)
    plot(plot_dir, all_percentiles[-1])

 
if __name__ == "__main__":
    app()