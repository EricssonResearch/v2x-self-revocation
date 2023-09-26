import asyncio
import signal
import subprocess
from typing import List

import numpy as np
import typer
from rich import print
from rich.progress import Progress
from pathlib import Path
from datetime import datetime

app = typer.Typer(add_completion=False)

# Using typer here: https://typer.tiangolo.com/tutorial/arguments/optional/
@app.command()
def main(
        n: int = typer.Option(
            2, "-n",
            help="Size of the PRL.",
        ),
        n_max: int = typer.Option(
            1, "--n-max",
            help="Max PRL size. Relative to n (used in `range(n, n + n_max, n_step)`).",
        ),
        n_step: int = typer.Option(
            1, "--n-step",
            help="Increment for n (used in `range(n, n + n_max, n_step)`).",
        ),
        e: int = typer.Option(
            2, "-e",
            help="Number of epochs that a certificate stays in the PRL.",
        ),
        e_max: int = typer.Option(
            1, "--e-max",
            help="Max epochs. behaves the same as n-max",
        ),
        e_step: int = typer.Option(
            1, "--e-step",
            help="Increment for e, behaves the same as n-step",
        ),
        p: List[float] = typer.Option(
            [0.1], "-p",
            help="Probability of a certificate being revoked. Argument can be given multiple times to create a list of probabilities to generate.",
        ),
        p_max: float = typer.Option(
            0.1, "--p-max",
            help="Max probability if p is not given multiple times. Then, behaves the same as n-max.",
        ),
        p_step: float = typer.Option(
            0.1, "--p-step",
            help="Increment for p if p is not given multiple times. Then, behaves the same as n-step.",
        ),
        cache_dir: Path = typer.Option(
            'cached', "--cache-dir", help="Path to cache directory",
            exists=False, dir_okay=True, readable=True, file_okay=False
        ),
        plot_dir: Path = typer.Option(
            'plots', "--path", help="Path to folder to write plots",
                exists=False, dir_okay=True, file_okay=False, readable=True, writable=True,
        )
):
    '''
    Calculate a series of markov matrices for a range of pseudonym revocation lists. In the paper graphs, this equates to one series, e.g. the series of n=100 to n=1000 for otherwise fixed parameters.
    '''

    print(f'Running main script for n=[{n},{n+n_max}], e=[{e},{e+e_max}], and p={p}')
    num_threads = (n_max) * (e_max)
    
    # write plots on the "distributions" folder within plot_dir
    plot_dir = plot_dir.joinpath("distributions")
    print(f'Creating dir {str(plot_dir)}')
    plot_dir.mkdir(parents=True, exist_ok=True)

    def shutdown():
        for task in asyncio.all_tasks():
            task.cancel()

    async def control_eventloop():
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, shutdown)
        loop.add_signal_handler(signal.SIGINT, shutdown)

        # Getting the current date and time
        dt = datetime.now()

        # getting the timestamp
        timestamp = dt.strftime("%Y-%m-%d_%H-%M-%S")

        n_range = range(n, n + n_max, n_step)
        e_range = range(e, e + e_max, e_step)

        if len(p) > 1:
            p_range = p
        else:
            p_range = np.arange(p[0], p[0] + p_max + p_step, p_step)

        print(f'Generating for ranges n {str(n_range)}, e {str(e_range)}, p {str(p_range)}')

        # Start creating tasks
        task_list=[]
        task_counter = 0
        for i in n_range:
            for j in e_range:
                for k in p_range:
                    task_counter += 1
                    task_list.append(                        
                        asyncio.create_subprocess_shell(
                            f'python3 main.py '
                            f'-n {i} '
                            f'-e {j} '
                            f'-p {k:.15f} '
                            f'-g '
                            f'--plot-path={plot_dir}/{timestamp}-{task_counter}_n{i}_e{j}_p{k:.15f}.svg '
                            f'--cache-dir={cache_dir} '
                            f'--allow-cached',
                            stdout=subprocess.DEVNULL,
                            loop=loop)
                    )

        print(f'Created {len(task_list)} tasks. Starting to run them...')

        process_list = []
        with Progress() as progress:
            progress_task = progress.add_task("[green]Starting tasks...", total=len(task_list))
            for f in asyncio.as_completed(task_list):
                process_list.append(await f)
                progress.update(progress_task, advance=1)

        with Progress() as progress:
            progress_task = progress.add_task("[green]Running tasks...", total=len(task_list))
            for pr in process_list:
                await pr.wait()
                progress.update(progress_task, advance=1)

    asyncio.run(control_eventloop())
    print('Done.')

if __name__ == "__main__":
    app()
