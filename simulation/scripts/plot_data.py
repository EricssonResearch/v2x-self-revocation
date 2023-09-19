import sys
import json
from matplotlib import pyplot as plt
import os
import re
from os.path import join
import pandas as pd
import seaborn as sns
import numpy as np
import tikzplotlib

input_dir = sys.argv[1]
scenario = sys.argv[2]
out = sys.argv[3]

if len(sys.argv) > 4:
    attackers = sys.argv[4].split(",")
else:
    attackers = None

print(attackers)

scenarios_folder = join(input_dir, "scenarios")
results_folder = join(input_dir, "results")
data_folder = join(input_dir, "data")
figs_folder = join(input_dir, "figs")
tikz_folder = join(input_dir, "tikz")

files_regex = f"{scenario}_([0-9]*)\-?(.+).json"
x_axis = []
files = []

def mkdir(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)

def get_ordering(key):
    order = ["honest", "blind", "smart", "smarter"]
    for level in order:
        if key[1].startswith(level):
            return f"{key[0]}_{order.index(level)}_{key[1]}"

    return f"{key[0]}_99_{key[1]}"

def compute_max_time(file):
    with open(join(results_folder, file), "r") as f:
        data = json.load(f)

    env = data["env"]
    t_v = int(env["T_V"])
    return t_v, t_v, t_v + t_v

def compute_data(file):
    with open(join(results_folder, file), "r") as f:
        data = json.load(f)

    revoke_to_sign = []
    revoke_to_verify = []
    sign_to_verify = []

    pseudonyms = data["pseudonyms"]

    for ps in pseudonyms:
        time_revoke_sign = pseudonyms[ps]["last_sign"] - pseudonyms[ps]["revoked"]
        time_revoke_verify = pseudonyms[ps]["last_verify"] - pseudonyms[ps]["revoked"]
        time_sign_verify = pseudonyms[ps]["last_verify"] - pseudonyms[ps]["last_sign"]
        revoke_to_sign.append(time_revoke_sign)
        revoke_to_verify.append(time_revoke_verify)
        sign_to_verify.append(time_sign_verify)
        #print(f"{ps}: {time_revoke_sign} {time_revoke_verify}")

    return revoke_to_sign, revoke_to_verify, sign_to_verify

def compute_distribution(file):
    with open(join(results_folder, file), "r") as f:
        data = json.load(f)

    verify_distribution = []
    for ps_index in data["pseudonyms"]:
        ps = data["pseudonyms"][ps_index]

        distribution = list(filter(lambda x : x > 0, ps["distribution"]))
        verify_distribution += list(map(lambda x : x - ps["revoked"], distribution))
    return verify_distribution

def save_tikz(file, width="15cm", height="8cm", fix_rects=False):
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

    # set clip=false to show labels outside the plot
    tikz_file = tikz_file.replace(
        "\\begin{axis}[",
        "\\begin{axis}[\nclip=false,"
    )

    # TODO fix "yticklabel style": "anchor=center,yshift=6pt"

    # fix rectangles in box plot
    if fix_rects:
        ymin = float(re.findall("ymin=([\-0-9.]+),", tikz_file)[0])
        ymax = float(re.findall("ymax=([\-0-9.]+),", tikz_file)[0])
        rect_regex = "(draw\[.+\] (\(axis cs:.+,.+\)) rectangle (\(axis cs:.+,.+\));)"
        matches = re.findall(rect_regex, tikz_file)

        for match in matches:
            yvalue_1 = re.findall("axis cs:[\-0-9.]+,([\-0-9.]+)", match[1])[0]
            yvalue_2 = re.findall("axis cs:[\-0-9.]+,([\-0-9.]+)", match[2])[0]
            if float(yvalue_1) < ymin:
                repl = match[1].replace(f",{yvalue_1})", f",{ymin})")
                repl_string = match[0].replace(match[1],repl)
                tikz_file = tikz_file.replace(match[0], repl_string)
            elif float(yvalue_1) > ymax:
                repl = match[1].replace(f",{yvalue_1})", f",{ymax})")
                repl_string = match[0].replace(match[1],repl)
                tikz_file = tikz_file.replace(match[0], repl_string)

            if float(yvalue_2) < ymin:
                repl = match[2].replace(f",{yvalue_2})", f",{ymin})")
                repl_string = match[0].replace(match[2],repl)
                tikz_file = tikz_file.replace(match[0], repl_string)
            elif float(yvalue_2) > ymax:
                repl = match[2].replace(f",{yvalue_2})", f",{ymax})")
                repl_string = match[0].replace(match[2],repl)
                tikz_file = tikz_file.replace(match[0], repl_string)

    with open(file, "w") as f:
        f.write(tikz_file)


def boxplot(data, t_v, t_rev, t_eff):
    sns.set_style("darkgrid")
    sns.set(font_scale = 1.5)

    line_text = 290 if t_eff == 300 else 58
    xlims = (-5,305) if t_eff == 300 else (-2,62)
    height = 2.5 * len(x_axis)
    
    # First plot: sign and verify together
    plt.figure(figsize=(20,height))
    plot = sns.boxplot(x="time", y="class", data=data, hue="operation")
    plt.xlabel("Time (s)")
    plt.ylabel("")

    plot.set_yticklabels(plot.get_yticklabels(), rotation=90, va="center")
    #if len(x_axis) <= 3:
    #    

    plot.set(xlim=xlims)
    #plt.legend(framealpha=1)
    #sns.move_legend(plot, "upper center", bbox_to_anchor=(1.02, 1))
    sns.move_legend(
        plot, "lower center",
        bbox_to_anchor=(.5, 1), ncols=2, title=None, frameon=False, 
        facecolor="white", fontsize=20
    )
    #plt.title("TEST", size=25)
    #if t_rev != t_eff:
    #    plot.axvline(t_rev)
    #    plt.text(t_rev, -0.55, "$T_{rev}$")

    [plot.axhline(y+.5,color='w') for y in plot.get_yticks()]
    plot.axvline(t_eff, color="chocolate")
    plt.text(line_text, -0.6, "$T_{eff}$")
    plt.savefig(join(figs_folder, out, f'{scenario}_sign_verify.svg'), format="svg")
    save_tikz(join(tikz_folder, out, f'{scenario}_sign_verify.tex'), height=f"{height}cm")

    # second plot: only sign
    plt.figure(figsize=(20,height))
    plot = sns.boxplot(
        x="time",
        y="class",
        data=data[data['operation'] == "sign"],
        palette="colorblind"
    )
    plt.xlabel("Time (s)")
    plt.ylabel("")
    plot.set_yticklabels(plot.get_yticklabels(), rotation=90, va="center")

    #plt.title("TEST", size=25)
    plot.axvline(t_rev, color="black")
    plt.text(t_rev - 1.5, -0.58, "$T_{rev}$")
    plt.savefig(join(figs_folder, out, f'{scenario}_sign.svg'), format="svg")
    save_tikz(join(tikz_folder, out, f'{scenario}_sign.tex'))

    # third plot: only verify
    plt.figure(figsize=(20,height))
    plot = sns.boxplot(
        x="time",
        y="class",
        data=data[data['operation'] == "verify"],
        palette="colorblind"
    )
    plt.xlabel("Time (s)")
    plt.ylabel("")
    plot.set_yticklabels(plot.get_yticklabels(), rotation=90, va="center")

    #plt.title("TEST", size=25)
    plot.axvline(0, color="blue")
    plt.text(0 - 3.5, -0.58, "$REVOKE$")

    plot.axvline(t_v, color="black")
    plt.text(t_v - 1, -0.58, "$T_{v}$")

    plot.axvline(t_eff, color="black")
    plt.text(t_eff - 1.5, -0.58, "$T_{eff}$")
    plt.savefig(join(figs_folder, out, f'{scenario}_verify.svg'), format="svg")
    save_tikz(join(tikz_folder, out, f'{scenario}_verify.tex'))


# create folders
mkdir(data_folder)
mkdir(figs_folder)
mkdir(tikz_folder)
mkdir(join(data_folder, out))
mkdir(join(figs_folder, out))
mkdir(join(tikz_folder, out))

# check number of files we have for this scenario and their attacker value
scenario_files = "\n".join(os.listdir(results_folder))
matches = re.findall(files_regex, scenario_files)

matches.sort(key=get_ordering)
matches = [x for x in matches if attackers is None or x[1] in attackers]
print(matches)

for prefix, level in matches:
    f = f"{scenario}_{prefix}-{level}.json"
    
    x_axis.append(level)
    files.append(f)

#print(x_axis)
#print(files)
data_sign = []
data_verify = []
data_distr = []

min_median = None
max_median = None

# get data and normalize negative values
for f in files:
    sign, verify, _ = compute_data(f)
    distr = compute_distribution(f)

    # filtering out negative values -> not interesting
    sign = list(filter(lambda x : x > 0, sign))
    verify = list(filter(lambda x : x > 0, verify))
    distr = list(filter(lambda x : x > 0, distr))

    #data_sign.append(list(map(lambda x : x if x >= 0 else -1, sign)))
    #data_verify.append(list(map(lambda x : x if x >= 0 else -1, verify)))
    #data_distr.append(list(map(lambda x : x if x >= 0 else -1, distr)))

    data_sign.append(sign)
    data_verify.append(verify)
    data_distr.append(distr)

    q1 = np.quantile(verify,0.25)
    q3 = np.quantile(verify,0.75)
    iqr15 = 1.5 * (q3-q1)

    print(
        f"{f}: verify_data: {len(verify)} median: {np.median(verify)} "
        f"Q1: {q1} Q3: {q3} 1.5 IQR: {iqr15} "
        f"lower: {q1 - iqr15} upper: {q3 + iqr15}"
    )

# create dataset
data_sv = []
data_m = []

for i in range(0, len(x_axis)):
    median = np.median(data_verify[i]) - np.median(data_sign[i])
    min_median = min_median if min_median is not None and min_median <= median else median
    max_median = max_median if max_median is not None and max_median >= median else median

    label = x_axis[i]

    for j in range(len(data_sign[i])):
        data_sv.append(
            {
                "class": label,
                "operation": "sign",
                "time": data_sign[i][j],
            }
        )

    for j in range(len(data_verify[i])):
        data_sv.append(
            {
                "class": label,
                "operation": "verify",
                "time": data_verify[i][j],
            }
        )

    data_m.append(
        {
            "class": label,
            "median": median
        }
    )


svf = pd.DataFrame(data_sv)
mf = pd.DataFrame(data_m)

# Optional - store DataFrame to file
svf.to_csv(join(data_folder, out, f'{scenario}_sign_verify.csv'))
mf.to_csv(join(data_folder, out, f'{scenario}_median.csv'))

# get T_rev and T_eff from a file
t_v, t_rev, t_eff = compute_max_time(files[0])
print(f"T_rev: {t_rev} T_eff: {t_eff}")

# Revoke to SIGN and revoke to VERIFY
boxplot(
    svf,
    t_v,
    t_rev,
    t_eff
)

# Sign -> Verify median difference
plt.figure()
sns.set(font_scale = 1)
sns.color_palette("colorblind")

plot = sns.barplot(x='class', y='median', data=mf, palette="icefire")
#plt.title('Time between last SIGN and last VERIFY')
plt.ylabel("Time (s)")
plt.xlabel("")
plt.ylim([min_median - 1, max_median + 1])
#plot.bar_label(plot.containers[0])

"""
sm = plt.cm.ScalarMappable(cmap="icefire")
cbar = plot.figure.colorbar(sm, ticks=[0,1], ax=plot)
cbar.ax.set_yticklabels(["good", "bad"])
cbar.ax.tick_params(size=0)
"""

plt.savefig(join(figs_folder, out, f'{scenario}_median.svg'), format="svg")
save_tikz(join(tikz_folder, out, f'{scenario}_median.tex'), "8cm", "8cm", fix_rects=True)
