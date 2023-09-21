# https://stackoverflow.com/a/23324703
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

DOCKER_NAME ?= selfrevocation/prl_size
DOCKER_BINDING = -v $(ROOT_DIR):/usr/src/app -t
# It would be nice to use the local user for permissions but that breaks matplotlib
#--user "$(shell id -u):$(shell id -g)"
# To mitigate this, we now just run the make clean inside docker to have the right permissions to remove the files we created.

build-docker:
	docker build . -t $(DOCKER_NAME)

run-docker:
	docker run -it --rm $(DOCKER_BINDING) $(DOCKER_NAME) bash

test:
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) python3 main.py -n 3 -p 0.01 -e 2 --cache-dir=cached/ --allow-cached

single:
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) python3 main.py -n 800 -p 0.000000116323325 -e 30 --cache-dir=cached/ --allow-cached

tikz:
	@echo "Generating transition graph (Fig. 15)."
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) python3 main.py -n 3 -p 0.1 -e 2 -f tikz-graph.tex
	cat tikz-graph.tex

p-plot:
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) ./scripts/p-plot.sh

n-plot:
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) ./scripts/n-plot.sh

t-plot:
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) ./scripts/t-plot.sh

tv-distribution:
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) ./scripts/tv-distribution.sh

.PHONY: check
check:
	@if [ -d "$(ROOT_DIR)/cached" ]; then \
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

all: check p-plot t-plot n-plot tv-distribution tikz
	@echo Successfully created all graphs!

# Run clean inside docker so that we can clear the cached Directory and files created by the root user in docker.
clean:
	docker run --rm $(DOCKER_BINDING) $(DOCKER_NAME) rm -rf cached plots *.tex *.png