# End-to-end simulation

Simulations can run using either Docker Compose or Kubernetes. The
[.env](./.env) file contains a list of all configurable parameters.

**NOTE:** Python3 with the
[cryptography](https://pypi.org/project/cryptography/) package is required to
run the simulations, which can be installed by running `pip install
cryptography`.

A visual representation of the simulation is provided by the `web` component,
which runs a web server on port 80. This is a pretty simple web app that is only
intended for demonstrative purposes, and for best results it is recommended to
not exceed 30-40 virtual vehicles and 10 groups in total, and no more than 16
vehicles per group on average.

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

**NOTE:** pods are configured to run on K8s nodes with label `workerNode=yes`.
So, either make sure nodes have such label or remove this restriction from the
resource files.

```bash
# (if minikube) add label to node
kubectl label nodes minikube workerNode=yes

# run simulation
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