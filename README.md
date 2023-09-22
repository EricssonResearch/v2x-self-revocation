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
* Kick-the-tires stage (~8-10 human-minutes, ~14-16 compute-minutes)
* Run Tamarin proofs
* Run simulations
* Run Markov model

### Getting started

Our artifacts can be run on a commodity desktop machine with a x86-64 CPU an a
recent Linux operating system installed (preferably one between Ubuntu 20.04,
Ubuntu 22.04 and Debian 12). A machine with at least 8 cores and 16 GB of RAM is
_recommended_ to ensure that all the artifacts run correctly.

Below, we require the following software components installed and configured on
the machine:
- `git`, `make`, `screen` installed via apt: `sudo apt install -y git make screen`
- [Docker](https://docs.docker.com/engine/install/)
   - The `Docker Compose` plugin is also needed but should be installed
     automatically
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)

Below, we provide instructions to set up all dependencies on a fresh VM (we
tested on Ubuntu 20.04 and 22.04).

```bash
# Install dependencies
./install.sh

# enable docker group in the current shell
# NOTE: to make it permanent, you should logout and login again
newgrp docker
```

In the end, make sure of the following:
1. Docker is installed correctly: the `docker run --rm hello-world` command
   succeeds
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

**Step 1: PRL (~1-2 human-minutes, ~3-5 compute-minutes)**

```bash
# go to the `prl` folder
cd prl

# 1A: test setup (~1-5 seconds)
#     Expected output: markov matrix and the "Done" message, two cached files under `./cached`
make test

# 1B: single distribution (~3-5 minutes)
#     Expected output: markov matrix and "Done" message, two cached files under `./cached`
make single

# 1C: clean up (~1-5 seconds)
make clean

# go back to the root folder
cd ..
```

**STEP 2: Proofs (~2-3 human-minutes, ~1 compute-minutes)**

```bash
# go to the `proofs` folder
cd proofs

# 2A: prove the lemma `all_heartbeats_processed_within_tolerance` of the `centralized-time` model (~5 seconds)
#     Expected output: 
#     - Tamarin computations and "summary of summaries" at the end
#     - `all_heartbeats_processed_within_tolerance` marked as "verified"
#     - a `output_centralized.spthy` file under `./out`
make test MODEL=centralized-time OUT_FILE=output_centralized.spthy

# 2B: prove the lemma `all_heartbeats_processed_within_tolerance` of the `distributed-time` model (~20 seconds)
#     Expected output: 
#     - Tamarin computations and "summary of summaries" at the end
#     - `all_heartbeats_processed_within_tolerance` marked as "verified"
#     - a `output_distributed.spthy` file under `./out`
make test MODEL=distributed-time OUT_FILE=output_distributed.spthy

# 2C: clean up (~1-5 seconds)
make clean

# go back to the root folder
cd ..
```

**STEP 3: Simulation (~5 human-minutes, ~10 compute-minutes)**

Note: for step 3C, please follow the [Test instructions](./simulation/README.md#test).

```bash
# go to the `simulation` folder
cd simulation

# 3A: create a new Minikube instance (~1-5 minutes)
#     Note: by default we use all CPUs and half the memory in your machine
#     You can override this by setting the MINIKUBE_CPUS and MINIKUBE_MEMORY variables
#     Expected output:
#     - A success message similar to "Done! kubectl is now configured..."
#     - The "./logs" folder created
#     - kubectl works correctly: try running `kubectl get nodes`
make run_minikube

# 3B: build application from source on the Minikube instance (~3 minutes)
#     Expected output:
#     - No error messages
make build_minikube

# 3C: run and interact with the application (~5 minutes)
#     Please follow closely the "Test" section in "simulation/README.md" (see above)

# 3D: Shut down application and delete minikube instance (~2 minutes)
make clean_all

# go back to the root folder
cd ..
```

### Tamarin proofs

| Artifact     | Paper reference     | Description                            |
|--------------|---------------------|----------------------------------------|
|              |                     |                                        |