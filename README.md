# Efficient and Timely Revocation of V2X Credentials

This repository contains software artifacts for the paper _Efficient and Timely
Revocation of V2X Credentials_ that will appear at NDSS Symposium 2024.

## Abstract

In Intelligent Transport Systems, secure communication between vehicles,
infrastructure, and other road users is critical to maintain road safety. This
includes the revocation of cryptographic credentials of misbehaving or malicious
vehicles in a timely manner. However, current standards are vague about how
revocation should be handled, and recent surveys suggest severe limitations in
the scalability and effectiveness of existing revocation schemes. In this paper,
we present a formally verified mechanism for self-revocation of
Vehicle-to-Everything (V2X) pseudonymous credentials, which relies on a trusted
processing element in vehicles but does not require a trusted time source. Our
scheme is compatible with ongoing standardization efforts and, leveraging the
Tamarin prover, is the first to guarantee the actual revocation of credentials
with a predictable upper bound on revocation time and in the presence of
realistic attackers. We test our revocation mechanism in a virtual 5G-Edge
deployment scenario where a large number of vehicles communicate with each
other, simulating real-world conditions such as network malfunctions and delays.
Results show that our scheme upholds formal guarantees in practice, while
exhibiting low network overhead and good scalability.

## Structure

The repository is structured into three parts:

- `prl`
   contains scripts to generate and plot the markov matrices 
   (Sec. VII-B / Appendix D)
- `proofs`
   contains the Tamarin models used to formally verify our revocation scheme 
   (Sec. VI / Appendix B)
- `simulation`
   Containing the code used for our evaluation 
   (Sec. VII-A / Appendix C)

A README is also included on each individual folder containing instructions to
run our artifacts.

## Artifact Evaluation

Below you can find detailed instructions to reproduce the results of our paper.

To facilitate the artifact evaluation process, we give instructions for running
the experiments using our pre-built Docker images. However, if desired, the
README files on each folder contains extensive instructions for running all the
experiments locally.

For reference, our results are also computed via our [CI
pipeline](https://github.com/gianlucascopelliti/v2x-self-revocation/actions/workflows/simulation.yml).
The latest workflow contains the same steps described in this section and the
artifacts generated as output.

### Overview

* Getting started (~10-30 human-minutes, ~15 compute-minutes)
* Kick-the-tires stage
* Run Tamarin proofs
* Run simulations
* Run Markov model

### Getting started

Our artifacts can be ran on a commodity desktop machine with a x86-64 CPU an a
recent Linux operating system installed (preferably one between Ubuntu 20.04,
Ubuntu 22.04 and Debian 12).

Below, we require the following software components installed and configured on
the machine:
- `git`, `make`, `screen` installed via apt: `sudo apt install -y git make screen`
- `Python 3`: We recommend Python >= 3.8
   - To install our Python dependencies, we recommend setting up a fresh
     [environment](https://docs.python.org/3/library/venv.html)
- [Docker](https://docs.docker.com/engine/install/)
   - The `Docker Compose` plugin is also needed but should be installed
     automatically
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)

Below, we provide instructions to set up all dependencies on a fresh VM (we
tested on Ubuntu 20.04 and 22.04). This will also install Python dependencies
needed in the next steps.

```bash
# Install dependencies
./install.sh

# enable docker group in the current shell
# NOTE: to make it permanent, you should logout and login again
newgrp docker

# create a Python virtual environment
python3 -m venv env-v2x

# enable environment in the current shell
# NOTE: this must be done every time a new shell is created
source env-v2x/bin/activate

# Upgrade pip (since some old versions might not work)
pip install --upgrade pip

# Install python dependencies
pip install -r simulation/scripts/requirements.txt
```

In the end, make sure of the following:
1. Docker is installed correctly: the `docker run --rm hello-world` command
   succeeds
2. Docker Compose is installed: `docker compose version` succeeds
3. Kubectl is installed: `kubectl version` succeeds
4. Minikube is installed: `minikube version` succeeds
5. The `env-v2x` environment is enabled: you should see `(env-v2x)` in the
   prompt of your shell

The time to complete this step depends on whether you already have some (or all)
of the dependencies installed, and whether you use our `install.sh` script or
you install the dependencies manually. Overall, this should not take more than
30 human-minutes and 15 compute-minutes.

### Kick-the-tires stage

In this step, we will test our setup to ensure that our artifacts run correctly.

```bash
### Step 1: prl ###

### Step 2: proofs ###

### Step 3: simulation ###
```