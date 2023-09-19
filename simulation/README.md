# Simulation of a V2X scenario with self-revocation

We implemented a simulated V2X scenario where vehicles communicate on an edge
area via broadcast messages. The infrastructure manages enrollment to the
network (via an Issuer) and revocation (via a Revocation Authority (RA)).

Simulations can run using either Docker Compose or Kubernetes. Below, we provide
instructions for running on a Kubernetes cluster.

## Prerequisites

We require a Linux-based operating system running a recent Linux distribution.
We tested our code on Ubuntu 22.04, but other recent distros should work as
well. Python 3 needs to be installed on the machine.

1. Install Python dependencies: `pip3 install -r scripts/requirements` 
    - We recommend using a [virtual environment](https://docs.python.org/3/library/venv.html)
2. Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)

## Kubernetes cluster setup

Here you can choose to run the application on an existing Kubernetes cluster or
to setup a local cluster, e.g., using
[Minikube](https://minikube.sigs.k8s.io/docs/).

### Existing cluster

If you have an existing cluster already running, make sure it is reachable via
`kubectl`.

All our Deployment specifications have a `nodeSelector` that ensures that pods
are only deployed on nodes with the `workerNode: "yes"` label. Therefore, make
sure to either (1) set a label to each node you want to use for the application
using the `kubectl label nodes` command, or (2) remove the node selector from
the specifications in `res`.

**NOTE 1:** Our application uses multicast for communication between
vehicles. However, not all Kubernetes network plugin support this feature. In
order to run our application correctly, make sure your network plugin supports
multicast. As far as we know,
[Calico](https://docs.tigera.io/calico/3.25/reference/faq#can-calico-do-ip-multicast)
*does not* support multicast, but [Weave
net](https://www.weave.works/docs/net/latest/install/) does.

**NOTE 2:** To compute average revocation times shown in our paper, each
component logs to a file each action performed (with a timestamp). These files
are automatically collected by our scripts after the simulation ends. Our
scripts assume that all K8s nodes and the host share a volume, where logs will
be stored. This volume can be specified by setting the `LOG_DIR_MOUNT` and
`LOG_DIR_LOCAL` variables in the Makefile. If, however, there is no such shared
volume, logs must be collected separately for each pod and put under
`LOG_DIR_LOCAL` before calling `log_aggregator.py`.

### Minikube

Our application can be easily deployed locally using Minikube, which is a tool
that sets up a local fully-configured Kubernetes cluster with only one node. Our
scripts and Makefile should support such a deployment without requiring any
changes.

To set up a minikube cluster, first make sure
[Docker](https://docs.docker.com/engine/install/ubuntu/) is correctly installed
(you can verify this by running `docker run --rm hello-world`). Then, [install
Minikube](https://minikube.sigs.k8s.io/docs/start/).

Then, run `make run_minikube` to start the Minikube instance and set up the
node.

## Test

The [.env](./.env) file contains a list of all configurable parameters.

A visual representation of the simulation is provided by the `web` component,
which runs a web server on port 80. This is a pretty simple web app that is only
intended for demonstrative purposes, and for best results it is recommended to
not exceed 30-40 virtual vehicles and 10 groups in total, and no more than 16
vehicles per group on average. The web application can be exposed locally on
port 8080 via the `make port_forward` command.

## Setup cluster

`825` millicores and `288` MiB

## Quick start with Docker Compose

This requires a recent version of [Docker](https://docs.docker.com/get-docker/)
with the [Compose](https://docs.docker.com/compose/install/) plugin.

```bash
# run simulation
make run_docker

# cleanup - after pressing CTRL-C
make clean
```

## Quick start with Kubernetes

This requires a running [Kubernetes](https://kubernetes.io/) cluster reachable
with `kubectl`. A [minikube](https://minikube.sigs.k8s.io/docs/) environment
also works.

**NOTE 1:** Pods use multicast for communication. Therefore, make sure your
Kubernetes network plugin supports multicast in order to run the simulation
correctly.

**NOTE 2:** pods are configured to run on K8s nodes with label `workerNode=yes`.
So, either make sure nodes have such label or remove this restriction from the
resource files.

```bash
# (if minikube) add label to node
kubectl label nodes minikube workerNode=yes

# run simulation. All resources are deployed in the `v2x` namespace
make run_kubernetes

# cleanup
make clean
```

## Parameters

```properties
VERSION=v1.0.2
LOG_LEVEL=info
LOG_TO_FILE=1 # write logs to file
LOG_TO_UDP=1 # write functional logs to UDP -- needed for the web app
LOG_MAX_SIZE=0 # optionally indicates a maximum size of each log file, in MB
# Revocation parameters
T_V=10
# Vehicles, attackers and groups
NUM_VEHICLES=2 # honest vehicles
NUM_ATTACKERS=1 # malicious vehicles
ATTACKER_LEVEL=smarter # attacker level (see Sect. 6.1.2)
NUM_GROUPS=20 # groups within an area to simulate proximity (Sect 6.1.1)
# Pseudonyms
NUM_PSEUDONYMS=2 # concurrent pseudonyms
PSEUDONYM_SIZE=16 # size of pseudonym identifier in bytes
PSEUDONYM_REFRESH_PERIOD=300 # Period in seconds the OBU requests a refresh
MIN_PSEUDONYM_LIFETIME=360000 # Min lifetime in seconds, enforced by the TC
# Heartbeats and V2V messages
HEARTBEAT_DISTRIBUTION_PERIOD=1 # By the RSU
HEARTBEAT_GENERATION_PERIOD=1 # By the RA
V2V_GENERATION_PERIOD=1 # By vehicles
# TC parameters
TRUSTED_TIME=0 # enable/disable local trusted time source
TC_STORE_LAST_PRL=0 # enable/disable active revocation
HARD_REVOCATION=1 # revoke all credentials in case of self-revocation, or that pseudonym only
# OBU parameters
JOIN_MAX_DELAY=20 # random delay to avoid all vehicles joining at the same time
AUTO_REJOIN=1 # re-join the network automatically after revocation
BLIND_ATTACKER_DROP_RATE=0.9 # for blind-1 attacker
BLIND_2_ATTACKER_DELAYED=0 # for blind-2 attacker
VEHICLE_MOVING=1 # vehicle can move between groups
RANDOM_MOVEMENT=1 # ordered movement (1->2->3) or random (1->9->4)
MOVEMENT_PERIOD=30 # period of movement
# RSU parameters
RSU_DROP_RATE=0.4 # probability to drop a HB
RSU_DELAY_RATE=0.4 # probability to delay a HB with random delay
# Reporter parameters
REPORT_MALICIOUS_ONLY=1 # either report all vehicles or attackers only
REPORT_PERIOD=10 # period in seconds of reports
REPLAY_RATE=0.3 # replay probability for malicious messages
# Web app parameters
THRESHOLD_MALICIOUS=2
THRESHOLD_UNSEEN=2
THRESHOLD_UNUSED=300
```