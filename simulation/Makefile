ENV_FILE        ?= .env
DOCKER_REGISTRY ?= docker.io
DOCKER_USERNAME ?= selfrevocation
DOCKER_TOKEN    ?= 

VERSION         ?= $(shell cat $(ENV_FILE) | grep VERSION | cut -d "=" -f2)
NUM_VEHICLES    ?= $(shell cat $(ENV_FILE) | grep NUM_VEHICLES | cut -d "=" -f2)
NUM_ATTACKERS   ?= $(shell cat $(ENV_FILE) | grep NUM_ATTACKERS | cut -d "=" -f2)
NUM_GROUPS      ?= $(shell cat $(ENV_FILE) | grep NUM_GROUPS | cut -d "=" -f2)
ATTACKER_LEVEL  ?= $(shell cat $(ENV_FILE) | grep ATTACKER_LEVEL | cut -d "=" -f2)

REPLICASET_VEHICLES = $(shell kubectl describe deployment -n v2x vehicle | grep "replica set" | sed -r "s/ /\n/g" | grep "vehicle")
REPLICASET_ATTACKERS = $(shell kubectl describe deployment -n v2x attacker | grep "replica set" | sed -r "s/ /\n/g" | grep "attacker")

mkdir:
	mkdir -p cred

gen_ra_key: mkdir
	python3 scripts/gen_keys.py

build:
	docker compose build

run_docker: gen_ra_key
	docker compose up --build --remove-orphans --force-recreate

run_kubernetes: gen_ra_key
	kubectl create namespace v2x
	#kubectl --namespace v2x create secret docker-registry regcred --docker-username=$(DOCKER_USERNAME) --docker-password=$(DOCKER_TOKEN) --docker-email=$(DOCKER_EMAIL)
	kubectl --namespace v2x create configmap system --from-env-file=$(ENV_FILE)
	kubectl --namespace v2x create secret generic ra-keys --from-file=private=cred/ra_private.pem --from-file=public=cred/ra_public.pem
	scripts/deploy.sh res/deployments/infra/issuer.yaml VERSION=$(VERSION)
	scripts/deploy.sh res/deployments/infra/ra.yaml VERSION=$(VERSION)
	scripts/deploy.sh res/deployments/infra/web.yaml VERSION=$(VERSION)
	#kubectl apply -f res/deployments/infra/admin.yaml
	scripts/check_infra.sh
	scripts/deploy.sh res/deployments/area/rsu.yaml VERSION=$(VERSION)
	scripts/deploy.sh res/deployments/area/reporter.yaml VERSION=$(VERSION)
	scripts/deploy.sh res/deployments/area/vehicle.yaml VERSION=$(VERSION) NUM_VEHICLES=$(NUM_VEHICLES)
	scripts/deploy.sh res/deployments/area/attacker.yaml VERSION=$(VERSION) NUM_ATTACKERS=$(NUM_ATTACKERS)

scale_vehicles:
	kubectl -n v2x scale --replicas $(NUM_VEHICLES) deployment vehicle

scale_attackers:
	kubectl -n v2x scale --replicas $(NUM_ATTACKERS) deployment attacker

port_forward:
	kubectl -n v2x port-forward service/web 8080:80

check_pods:
	kubectl describe replicaset -n v2x $(REPLICASET_VEHICLES) | grep Running
	kubectl describe replicaset -n v2x $(REPLICASET_ATTACKERS) | grep Running

clean:
	docker compose down || true
	kubectl delete ns v2x || true
	rm -rf cred

zip:
	zip -r simulation.zip res/ src/ .env docker-compose.yml Makefile README.md simulation.yaml scripts/check_infra.sh scripts/deploy.sh scripts/gen_keys.py