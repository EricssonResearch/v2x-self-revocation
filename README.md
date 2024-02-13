# Efficient and Timely Revocation of V2X Credentials

[![test-running](https://github.com/gianlucascopelliti/v2x-self-revocation/actions/workflows/ci.yml/badge.svg)](https://github.com/gianlucascopelliti/v2x-self-revocation/actions/workflows/ci.yml)
[![artifacts](https://github.com/gianlucascopelliti/v2x-self-revocation/actions/workflows/artifacts.yml/badge.svg)](https://github.com/gianlucascopelliti/v2x-self-revocation/actions/workflows/artifacts.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10210425.svg)](https://doi.org/10.5281/zenodo.10210425)

This repository contains software artifacts for the paper _Efficient and Timely
Revocation of V2X Credentials_ that will appear at [NDSS Symposium 2024](https://www.ndss-symposium.org/ndss-paper/efficient-and-timely-revocation-of-v2x-credentials/). The
camera-ready version of the paper is available
[here](https://bobspot.org/assets/docs/2023-11-ndss-v2x.pdf).

The evaluated artifacts for NDSS'24 are available at the `ndss-24-artifacts`
[release](https://github.com/EricssonResearch/v2x-self-revocation/releases/tag/ndss-24-artifacts).
A snapshot of the release has also been uploaded to
[Zenodo](https://zenodo.org/records/10210425), containing a DOI and citation
text. The `main` branch, instead, contains an up-to-date version of the code,
which may present some differences compared to the evaluated one.

## Artifact Abstract

In Intelligent Transport Systems, secure communication between vehicles,
infrastructure, and other road users is critical to maintain road safety. This
includes the revocation of cryptographic credentials of misbehaving or malicious
vehicles in a timely manner. However, current standards are vague about how
revocation should be handled, and recent surveys suggest severe limitations in
the scalability and effectiveness of existing revocation schemes. In our paper
"Efficient and Timely Revocation of V2X Credentials" (to appear at NDSS
Symposium 2024), we present a formally verified mechanism for self-revocation of
Vehicle-to-Everything (V2X) pseudonymous credentials, which relies on a trusted
processing element in vehicles but does not require a trusted time source. Our
scheme is compatible with ongoing standardization efforts and, leveraging the
Tamarin prover, is the first to guarantee the actual revocation of credentials
with a predictable upper bound on revocation time and in the presence of
realistic attackers. We further test our revocation mechanism in a virtual
5G-Edge deployment scenario running on Kubernetes, where a large number of
vehicles communicate with each other simulating real-world conditions such as
network malfunctions and delays. Our approach relies on distributing revocation
information via so-called Pending Revocation Lists (PRLs) where, unlike classic
Certificate Revocation Lists (CRLs), a pseudonym only needs to stay for a
limited time, needed to guarantee revocation. The process of adding and removing
pseudonyms from PRLs can be represented as a finite state machine where the
states are the possible sizes of the list, and a Markov model to describe the
probability of moving from state to state. We use such a model to predict the
size of PRLs and the related impact on the V2X system for different scenarios.

## Structure

The repository contains the following sub-artifacts:

- `proofs`
   contains the Tamarin models used to formally verify our revocation scheme 
   (Sect. VI / Appendix A)
- `simulation`
   Containing the code used for our evaluation 
   (Sect. VII-A)
- `prl`
   contains scripts to generate and plot the markov matrices 
   (Sect. VII-B / Appendix B)

A README is also included on each individual folder containing instructions to
run the artifacts.

## Artifact Evaluation

Below you can find detailed instructions to reproduce the results of our paper.

To facilitate the artifact evaluation process, we give instructions for running
the experiments using our pre-built Docker images. However, if desired, the
README files on each folder contains extensive instructions for running all the
experiments locally.

For reference, our results are also computed via our [CI
pipeline](https://github.com/gianlucascopelliti/v2x-self-revocation/actions/workflows/artifacts.yml).
The latest workflow contains the same steps described in this section and the
artifacts generated as output.

### Overview

* [Getting started](#getting-started) (~1-30 human-minutes, ~5-15 compute-minutes)
* [Kick-the-tires stage](#kick-the-tires-stage) (~8-10 human-minutes, ~14-16 compute-minutes)
* [Tamarin models](#tamarin-models) (~2 human-minutes, ~10 compute-minutes)
* [Simulations](#simulations) (~20-30 human-minutes, ~5 compute-hours)
* [PRL evaluation](#prl-evaluation) (~10-20 human-minutes, ~2.5-3.5 compute-hours)

### Getting started

Our artifacts can be run on a commodity desktop machine with a x86-64 CPU an a
recent Linux operating system installed (preferably one between Ubuntu >= 20.04
and Debian >= 10). A machine with at least 8 cores and 16 GB of RAM is
_recommended_ to ensure that all the artifacts run correctly.

For Ubuntu and Debian users, we provide a script `install.sh` to install all
dependencies automatically:

```bash
# Install all dependencies. 
# Note: the script will skip installation of any dependencies that you have already installed
#        if you want install up-to-date packages, pass the flag "-f" to the script
./install.sh

# Note: if this is the first installation of Docker, logout from the current shell
#        and login again to enable the "docker" group in the current user
```

If you opt for a manual installation, make sure the following software
components are installed and configured on the machine. The table also shows the
version that was used in our experiments, for reference (different versions
should work as well). _Note_: the Docker Compose plugin should come together
with recent Docker versions.

| Software                                                   | Reference version                               |
|------------------------------------------------------------|-------------------------------------------------|
| `git`, `make`, `screen` (installed via package manager)    | `git`: 2.34.1, `make`: 4.3, `screen`: 4.09.00   |
| [Docker](https://docs.docker.com/engine/install/)          | 23.0.2                                          |
| [Docker Compose](https://docs.docker.com/compose/install/) | 2.17.2                                          |
| [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) | 1.28.2                            |
| [Minikube](https://minikube.sigs.k8s.io/docs/start/)       | 1.31.2 (running Kubernetes 1.27.4)              |

In the end, make sure of the following:
1. Docker is installed correctly: the `docker run --rm hello-world` command
   succeeds
   - If you get a permission error, make sure [your user is in the "docker" group](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
2. Docker Compose is installed: `docker compose version` succeeds
3. Kubectl is installed: `kubectl version` succeeds
4. Minikube is installed: `minikube version` succeeds

The time to complete this step depends on whether you already have some (or all)
of the dependencies installed, and whether you use our `install.sh` script or
you install the dependencies manually. Overall, this should not take more than
30 human-minutes and 15 compute-minutes.

### Kick-the-tires stage

In this step, we will test our setup to ensure that our artifacts run correctly.

Note, we assume you are using a _fresh_ environment (e.g., no containers or
Minikube clusters are running) and you already followed the [Getting
started](#getting-started) instructions.

**STEP 1: Tamarin models (~2-3 human-minutes, ~1 compute-minutes)**

```bash
# go to the `proofs` folder
cd proofs

# 1A: prove the lemma `all_heartbeats_processed_within_tolerance` of the `centralized-time` model (~5 seconds)
#     Expected output: 
#     - Tamarin computations and "summary of summaries" at the end
#     - `all_heartbeats_processed_within_tolerance` marked as "verified"
#     - all other lemmas marked as "analysis incomplete" (since we do not verify them in this stage)
#     - a `output_centralized.spthy` file under `./out`
make test MODEL=centralized-time OUT_FILE=output_centralized.spthy

# 1B: prove the lemma `all_heartbeats_processed_within_tolerance` of the `distributed-time` model (~20 seconds)
#     Expected output: 
#     - Tamarin computations and "summary of summaries" at the end
#     - `all_heartbeats_processed_within_tolerance` marked as "verified"
#     - all other lemmas marked as "analysis incomplete" (since we do not verify them in this stage)
#     - a `output_distributed.spthy` file under `./out`
make test MODEL=distributed-time OUT_FILE=output_distributed.spthy

# 1C: clean up (~1-5 seconds)
make clean

# go back to the root folder
cd ..
```

**STEP 2: Simulations (~5 human-minutes, ~10 compute-minutes)**

Note: for step 3C, please follow the [Test instructions](./simulation/README.md#test).

```bash
# go to the `simulation` folder
cd simulation

# 2A: create a new Minikube instance (~1-5 minutes)
#     Note 1: by default we use all CPUs and half the memory in your machine
#     You can override this by setting the MINIKUBE_CPUS and MINIKUBE_MEMORY variables
#     Note 2: Make sure you are *not* running your shell as `root`, otherwise
#     Minikube will fail to start.
#     Expected output:
#     - A success message similar to "Done! kubectl is now configured..."
#     - The "./logs" folder created
#     - kubectl works correctly: try running `kubectl get nodes`
make run_minikube

# 2B: build application from source on the Minikube instance (~3 minutes)
#     Expected output:
#     - No error messages
make build_minikube

# 2C: run and interact with the application (~5 minutes)
#     Please follow closely the "Test" section in "simulation/README.md" (see above)

# 2D: Shut down application, delete minikube instance and remove files (~2 minutes)
make clean_all

# go back to the root folder
cd ..
```

**Step 3: PRL evaluation (~1-2 human-minutes, ~3-5 compute-minutes)**

```bash
# go to the `prl` folder
cd prl

# 3A: test setup (~1-5 seconds)
#     Expected output: markov matrix and the "Done" message, two cached files under `./cached`
make test

# 3B: single distribution (~3-5 minutes)
#     Expected output: markov matrix and "Done" message, two cached files under `./cached`
make single

# 3C: clean up (~1-5 seconds)
make clean

# go back to the root folder
cd ..
```

### Tamarin models

| Artifact     | Paper references    | Description                            |
|--------------|---------------------|----------------------------------------|
| `centralized-time` Tamarin model | Sect. VI, Appendix A, Table I | Model and proofs that verify the properties defined in Sect. V-A, for the main design of Sect. V |
| `distributed-time` Tamarin model | Appendix A, Table II | Variant of the model that assumes a trusted time source in TCs, as discussed in Sect. V-B, and proofs |

The steps for reproducing our results are the same as done in kick-the-tires
stage, but this time we will ask Tamarin to verify _all_ lemmas.

In total, this evaluation should take around **10 compute-minutes**.

```bash
# go to the `proofs` folder
cd proofs

# Step 1: prove all lemmas of `centralized-time` model (~5 minutes)
#     Expected output: 
#     - Tamarin computations and "summary of summaries" at the end
#     - In the summary, all lemmas are marked as "verified"
#     - a `output_centralized.spthy` file under `./out`
make prove MODEL=centralized-time OUT_FILE=output_centralized.spthy

# Step 2: prove all lemmas of `distributed-time` model (~5 minutes)
#     Expected output: 
#     - Tamarin computations and "summary of summaries" at the end
#     - In the summary, all lemmas are marked as "verified"
#     - a `output_distributed.spthy` file under `./out`
make prove MODEL=distributed-time OUT_FILE=output_distributed.spthy

# Step 3 (optional): Copy results somewhere safe (`out` folder will be deleted in the next step!)

# Step 4: clean up (~1-5 seconds)
make clean

# go back to the root folder
cd ..
```

### Simulations

| Artifact        | Paper references        | Description                            |
|-----------------|-------------------------|----------------------------------------|
| `scenario-a1`   | Sect. VII-A, Fig. 5     | Box plots showing distributions of revocation times under different attacker classes, for T_v = 30 seconds and no trusted time in TCs |
| `scenario-a2`   | Not in the paper        | Box plots showing distributions of revocation times under different attacker classes, for T_v = 150 seconds and no trusted time in TCs |
| `scenario-b1`   | Not in the paper        | Box plots showing distributions of revocation times under different attacker classes, for T_v = 30 seconds and assuming a trusted time in TCs |
| `scenario-b2`   | Not in the paper        | Box plots showing distributions of revocation times under different attacker classes, for T_v = 150 seconds and assuming a trusted time in TCs |

Scenarios A2, B1 and B2 and corresponding plots have been removed from the paper
due to page limits. However, we discuss them in the simulations'
[README](./simulation/README.md#extended-discussion-of-our-results).

In order to run the simulations locally and within a few hours, we provide a
scaled-down configuration that spawns 50 vehicles and runs all simulations in
around **4.5 to 5 compute-hours**. This configuration is described in the
`conf/ae.yaml` file, and should provide _similar_ results compared to ours,
although with much less collected data. For a more detailed description of this
setup, [click here](./simulation/README.md#scaled-down-setups).

Note: we recommend running the simulations when nothing else is running on the
same machine.

```bash
# go to the `simulation` folder
cd simulation

# Step 1: create a new Minikube instance and build application (~3-8 minutes)
#     Note: These are the same steps as done in the kick-the-tires stage
#           If you still have a Minikube cluster running, you can skip this step
#     Expected output:
#     - Same as the `kick-the-tires` stage (no errors, `logs/` created)
make run_minikube
make build_minikube

# Step 2: Test - run the first run of the first scenario for five minutes (~5 minutes)
#     This step is only to make sure our setup works
#     Expected output:
#     - a `simulation` folder created
#     - (after ~1 minute since start) the log file `simulations/out.log` does not show errors and is "SLEEPING"
#     - (after ~2-3 minutes since start) `kubectl -n v2x get pods` shows all pods in "Running" state
#     - (after ~5-6 minutes since start) `kubectl -n v2x get pods` shows pods in "Terminating" state or no pods at all
#     - (after ~6-7 minutes since start) the log file `simulations/out.log` shows "ALL DONE" as last message
#     - (after ~6-7 minutes since start) the `simulations/results` folder contains `scenario-a1_1-honest.json`
make run_simulations_background CONF=conf/ae.yaml SCENARIO=scenario-a1 RUN=1-honest SIM_TIME=300 DOWN_TIME=30

# Step 3: Run all simulations (~4.5-5 hours)
#     Note: you can run the command, grab a coffee and come back in 5 hours
#     Expected output:
#     - a `simulations` folder created. `simulations/scenarios` contain one `.properties` file for each run (total: 16 files)
#     - (after ~1 minute since start) the log file `simulations/out.log` does not show errors and is "SLEEPING"
#     - (after ~2 minutes since start) `kubectl -n v2x get pods` shows all pods in "Running" state
#     - (after ~4.5 hours since start) `kubectl -n v2x get pods` shows pods in "Terminating" state or no pods at all
#     - (after ~4.5 hours since start) the log file `simulations/out.log` shows "ALL DONE" as last message
#     - (after ~4.5 hours since start) the `simulations/results` folder contains one JSON file for each run (total: 16 files)
make run_simulations_background CONF=conf/ae.yaml

# Step 4: Plot results (~2 minutes)
#     Expected output:
#     - `data`, `figs` and `tikz` folders created under `simulations`
#     - `data` contains 8 .csv files (2 for each scenario)
#     - `figs` and `tikz` contain 4 files each, i.e., one plot for each scenario
make plot_all

# Step 5 (optional): Copy results somewhere safe (`simulations` folder will be deleted in the next step!)

# Step 6: Shut down application, delete minikube instance and remove files (~2 minutes)
make clean_all

# go back to the root folder
cd ..
```

### PRL evaluation

| Artifact              | Paper references    | Description                            |
|-----------------------|---------------------|----------------------------------------|
| `probabilities`       | Sect. VII-B, Appendix B | Probabilities used for each scenario, and expected number of revocations |
| `p-plot`              | Sect. VII-B, Fig. 6 | Plots percentiles for maximum PRL sizes under different scenarios and shares of attackers, with fixed `T_prl` and number of pseudonyms |
| `tv-distribution`     | Sect. VII-B, Fig. 7 | Evaluates `T_eff`, heartbeat frequency, heartbeat size, and required bandwidth under different values for `T_v` |
| `tikz-graph`          | Appendix B, Fig. 9  | Simple transition graph |
| `n-plot`              | Appendix B, Fig. 10 | Plots 99th percentile for maximum PRL sizes under different number of pseudonyms, in four different scenarios |
| `t-plot`              | Appendix B, Fig. 11 | Plots 99th percentile for maximum PRL sizes under different values for `T_prl`, in four different scenarios |

In total, this evaluation should take between **2.5 and 3.5 compute-hours**,
depending on your hardware.

```bash
# go to the `prl` folder
cd prl

# Step 1: compute probabilities (~1-5 seconds)
#     Expected output:
#     - probabilities and expected number of revocations printed to standard output
#     - "All done!" message
make probabilities

# Step 2: transition graph (~1-5 seconds)
#     Expected output:
#     - markov matrix and the "Done" message printed to standard output
#     - `tikz-graph.tex` plot under `./plots`
make tikz

# Step 3: Plot series over the different probabilities (~15-20 minutes)
#     Expected output: 
#     - no errors printed to standard output
#     - several distributions cached in `./cached` and plotted in `./plots/distributions`
#     - plots `p-plot_n800_e30.{tex,png}` under `./plots`
make p-plot

# Step 4: Plot series over the number of pseudonyms (~25-35 minutes)
#     Expected output:
#     - no errors printed to standard output
#     - several distributions cached in `./cached` and plotted in `./plots/distributions`
#     - plots `n-plot_e30.{tex,png}` under `./plots`
make n-plot

# Step 5: Plot series over the time each pseudonym stays in the list (~90-140 minutes)
#     Expected output:
#     - no errors printed to standard output
#     - several distributions cached in `./cached` and plotted in `./plots/distributions`
#     - plots `t-plot_n800.{tex,png}` under `./plots`
make t-plot

# Step 6: Generate distribution for Tv (~15-20 minutes)
#     Expected output:
#     - no errors printed to standard output
#     - several distributions cached in `./cached` and plotted in `./plots/distributions`
#     - plots `tv-distribution.{tex,png}` under `./plots`
make tv-distribution

# Step 7 (optional): Copy results somewhere safe (`plots` folder will be deleted in the next step!)

# Step 8: clean up
make clean

# go back to the root folder
cd ..
```
