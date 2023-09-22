# https://stackoverflow.com/a/23324703
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

DOCKER_NAME ?= selfrevocation/prl_size
DOCKER_BINDING = -v $(ROOT_DIR):/usr/src/app -t
# It would be nice to use the local user for permissions but that breaks matplotlib
#--user "$(shell id -u):$(shell id -g)"
# To mitigate this, we now just run the make clean inside docker to have the right permissions to remove the files we created.

CACHE_DIR ?= cached
PLOT_DIR ?= plots

build-docker:
	docker build . -t $(DOCKER_NAME)

run-docker: init_dirs
	docker run -it --rm $(DOCKER_BINDING) $(DOCKER_NAME) bash

test: init_dirs
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) python3 main.py -n 3 -p 0.01 -e 2 --cache-dir=$(CACHE_DIR) --allow-cached

single: init_dirs
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) python3 main.py -n 800 -p 0.000000116323325 -e 30 --cache-dir=$(CACHE_DIR) --allow-cached

tikz: init_dirs
	@echo "Generating transition graph (Fig. 15)."
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) python3 main.py -n 3 -p 0.1 -e 2 -f $(PLOT_DIR)/tikz-graph.tex
	cat $(PLOT_DIR)/tikz-graph.tex

p-plot: init_dirs
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) ./scripts/p-plot.sh --cache-dir $(CACHE_DIR) --path $(PLOT_DIR)

n-plot: init_dirs
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) ./scripts/n-plot.sh --cache-dir $(CACHE_DIR) --path $(PLOT_DIR)

t-plot: init_dirs
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) ./scripts/t-plot.sh --cache-dir $(CACHE_DIR) --path $(PLOT_DIR)

tv-distribution: init_dirs
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) ./scripts/tv-distribution.sh --cache-dir $(CACHE_DIR) --path $(PLOT_DIR)

.PHONY: check
check:
	@if [ -d "$(ROOT_DIR)/$(CACHE_DIR)" ]; then \
		echo "Cached Directory exists. Continuing under the assumption that you know this might take a while."; \
	else \
		echo "!!! Cache dir does not exist!\n!!! This means that \`make all\` will take a long time. We suggest to start small and run \`make test\` first and check the Readme.\n!!! Continue anyway? [y/n]"; \
	read line; \
	if [ ! $$line = "y" ]; then \
		echo aborting; \
		exit 1; \
	else \
		echo okay, continuing. This might take a while..; \
	fi ; \
	fi

all: init_dirs check p-plot t-plot n-plot tv-distribution tikz
	@echo Successfully created all graphs!

init_dirs:
	@mkdir -p $(CACHE_DIR)
	@chmod o+rw $(CACHE_DIR)
	@mkdir -p $(PLOT_DIR)
	@chmod o+rw $(PLOT_DIR)

clean:
	rm -rf $(CACHE_DIR) $(PLOT_DIR)