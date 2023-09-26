LOG_DIR_MOUNT           ?= /logs
LOG_DIR_LOCAL           ?= $(shell pwd)/logs
CONF                    ?= conf/paper.yaml
SIM_DIR                 ?= simulations
LOG_FILE                ?= $(SIM_DIR)/out.log
SCENARIO                ?=
RUN                     ?=
PLOTS			        ?= 
PLOT_NAME		        ?= $(SCENARIO)

MINIKUBE_CPUS           ?= $(shell nproc)
MINIKUBE_MEMORY         ?= $(shell expr `free -m | grep Mem: | awk '{print $$2}'` / 2)

DOCKER_PYTHON           ?= selfrevocation/python

# Set PYTHON to "python" to work locally
PYTHON                  ?= docker run --rm -v $(shell pwd):/usr/src/app -v $(LOG_DIR_LOCAL):$(LOG_DIR_LOCAL) $(DOCKER_PYTHON)

ENV_FILE                ?= .env
DOCKER_REGISTRY         ?= docker.io
DOCKER_USERNAME         ?= selfrevocation
DOCKER_TOKEN            ?= 

VERSION                 ?= $(shell cat $(ENV_FILE) | grep VERSION | cut -d "=" -f2)
NUM_VEHICLES            ?= $(shell cat $(ENV_FILE) | grep NUM_VEHICLES | cut -d "=" -f2)
NUM_ATTACKERS           ?= $(shell cat $(ENV_FILE) | grep NUM_ATTACKERS | cut -d "=" -f2)

SIM_TIME                ?= -1
DOWN_TIME               ?= -1

REPLICASET_VEHICLES      = $(shell kubectl describe deployment -n v2x vehicle | grep "replica set" | sed -r "s/ /\n/g" | grep "vehicle")
REPLICASET_ATTACKERS     = $(shell kubectl describe deployment -n v2x attacker | grep "replica set" | sed -r "s/ /\n/g" | grep "attacker")

PORT_FORWARD_ADDR       ?= 127.0.0.1

MKDIR                   ?= mkdir -m 777 -p

mkdir:
	$(MKDIR) cred

gen_ra_key: mkdir
	$(PYTHON) scripts/gen_keys.py

build:
	docker compose build

build_minikube:
	./scripts/build.sh

build_python_image:
	docker build -t $(DOCKER_PYTHON) .

run_docker: gen_ra_key
	docker compose up --build --remove-orphans --force-recreate

test: gen_ra_key
	docker compose up --remove-orphans --force-recreate --abort-on-container-exit --exit-code-from admin

run_kubernetes: gen_ra_key
	kubectl create namespace v2x
	#kubectl --namespace v2x create secret docker-registry regcred --docker-username=$(DOCKER_USERNAME) --docker-password=$(DOCKER_TOKEN) --docker-email=$(DOCKER_EMAIL)
	kubectl --namespace v2x create configmap system --from-env-file=$(ENV_FILE)
	kubectl --namespace v2x create secret generic ra-keys --from-file=private=cred/ra_private.pem --from-file=public=cred/ra_public.pem
	scripts/deploy.sh res/deployments/infra/issuer.yaml VERSION=$(VERSION) LOG_DIR=$(LOG_DIR_MOUNT)
	scripts/deploy.sh res/deployments/infra/ra.yaml VERSION=$(VERSION) LOG_DIR=$(LOG_DIR_MOUNT)
	scripts/deploy.sh res/deployments/infra/web.yaml VERSION=$(VERSION) LOG_DIR=$(LOG_DIR_MOUNT)
	#kubectl apply -f res/deployments/infra/admin.yaml LOG_DIR=$(LOG_DIR_MOUNT)
	scripts/check_infra.sh
	scripts/deploy.sh res/deployments/area/rsu.yaml VERSION=$(VERSION) LOG_DIR=$(LOG_DIR_MOUNT)
	scripts/deploy.sh res/deployments/area/reporter.yaml VERSION=$(VERSION) LOG_DIR=$(LOG_DIR_MOUNT)
	scripts/deploy.sh res/deployments/area/vehicle.yaml VERSION=$(VERSION) NUM_VEHICLES=$(NUM_VEHICLES) LOG_DIR=$(LOG_DIR_MOUNT)
	scripts/deploy.sh res/deployments/area/attacker.yaml VERSION=$(VERSION) NUM_ATTACKERS=$(NUM_ATTACKERS) LOG_DIR=$(LOG_DIR_MOUNT)

scale_vehicles:
	kubectl -n v2x scale --replicas $(NUM_VEHICLES) deployment vehicle

scale_attackers:
	kubectl -n v2x scale --replicas $(NUM_ATTACKERS) deployment attacker

port_forward:
	kubectl -n v2x port-forward --address $(PORT_FORWARD_ADDR) service/web 8080:80

check_pods:
	kubectl describe replicaset -n v2x $(REPLICASET_VEHICLES) | grep Running
	kubectl describe replicaset -n v2x $(REPLICASET_ATTACKERS) | grep Running

init_simulations:
	@echo "Initializing folders.."
	rm -rf $(LOG_DIR_LOCAL)/*
	test -f $(CONF)
	$(MKDIR) $(SIM_DIR)
	cp -r $(CONF) $(SIM_DIR)/simulation.yaml
	rm -rf $(SIM_DIR)/scenarios
	rm -rf $(SIM_DIR)/results
	rm -rf $(SIM_DIR)/data
	rm -rf $(SIM_DIR)/figs
	$(MKDIR) $(SIM_DIR)/scenarios
	$(MKDIR) $(SIM_DIR)/results
	@echo "Parsing simulation YAML file and environment variables.."
	$(PYTHON) scripts/parse_simulations.py --env_file $(ENV_FILE) --sim_dir $(SIM_DIR) --scenario $(SCENARIO) --run $(RUN)

run_minikube:
	$(MKDIR) $(LOG_DIR_LOCAL)
	minikube start --mount --mount-string="$(LOG_DIR_LOCAL):$(LOG_DIR_MOUNT)" \
		--cpus $(MINIKUBE_CPUS) --memory $(MINIKUBE_MEMORY) --driver=docker 
	kubectl label nodes minikube workerNode=yes

run_simulations: init_simulations
	./scripts/run_sim.sh $(SIM_DIR) $(SIM_TIME) $(DOWN_TIME) $(LOG_DIR_LOCAL)

run_simulations_background: init_simulations
	rm -rf $(LOG_FILE)
	@echo "Running simulations in the background.."
	@echo "You can check the current progress on $(LOG_FILE)"
	screen -A -m -d -S v2x-sims -L -Logfile $(LOG_FILE) ./scripts/run_sim.sh $(SIM_DIR) $(SIM_TIME) $(DOWN_TIME) $(LOG_DIR_LOCAL) &
	sleep 0.5
	screen -r v2x-sims -X colon "logfile flush 0.001^M"

aggregate_logs:
	$(PYTHON) scripts/log_aggregator.py $(LOG_DIR_LOCAL) $(LOG_FILE) $(SIM_TIME) $(DOWN_TIME) $(ENV_FILE)

plot:
	$(MKDIR) $(SIM_DIR)/figs
	$(MKDIR) $(SIM_DIR)/tikz
	$(MKDIR) $(SIM_DIR)/data
	$(PYTHON) scripts/plot_data.py $(SIM_DIR) $(SCENARIO) $(PLOTS)

plot_all:
	$(MKDIR) $(SIM_DIR)/figs
	$(MKDIR) $(SIM_DIR)/tikz
	$(MKDIR) $(SIM_DIR)/data
	$(PYTHON) scripts/plot_data.py $(SIM_DIR) scenario-a1 honest,smart,blind,smart-prl
	$(PYTHON) scripts/plot_data.py $(SIM_DIR) scenario-a2 honest,smart,blind,smart-prl
	$(PYTHON) scripts/plot_data.py $(SIM_DIR) scenario-b1 honest,smart,blind,smart-prl
	$(PYTHON) scripts/plot_data.py $(SIM_DIR) scenario-b2 honest,smart,blind,smart-prl

clean:
	screen -XS v2x-sims quit || true
	docker compose down || true
	kubectl delete ns v2x > /dev/null 2>&1 || true
	rm -rf cred $(LOG_DIR_LOCAL)/* $(SIM_DIR)

clean_minikube:
	minikube delete
	rm -rf $(LOG_DIR_LOCAL)

clean_all: clean clean_minikube

push_all: build
	docker push $(DOCKER_USERNAME)/e2e-sim-issuer:$(VERSION)
	docker push $(DOCKER_USERNAME)/e2e-sim-ra:$(VERSION)
	docker push $(DOCKER_USERNAME)/e2e-sim-rsu:$(VERSION)
	docker push $(DOCKER_USERNAME)/e2e-sim-tc:$(VERSION)
	docker push $(DOCKER_USERNAME)/e2e-sim-obu:$(VERSION)
	docker push $(DOCKER_USERNAME)/e2e-sim-reporter:$(VERSION)
	docker push $(DOCKER_USERNAME)/e2e-sim-web:$(VERSION)