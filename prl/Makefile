# https://stackoverflow.com/a/23324703
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

DOCKER_NAME ?= selfrevocation/prl_size
DOCKER_BINDING = -v $(ROOT_DIR):/usr/src/app -t
# It would be nice to use the local user for permissions but that breaks matplotlib
#--user "$(shell id -u):$(shell id -g)"
# To mitigate this, we now just run the make clean inside docker to have the right permissions to remove the files we created.

build-docker:
	docker build . -t $(DOCKER_NAME)

test:
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 main.py -n 3 -p 0.01 -e 2 --cache-dir=cached/ --allow-cached

single:
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 main.py -n 800 -p 0.0001 -e 30 --cache-dir=cached/ --allow-cached

tikz:
	@echo "Generating transition graph (Fig. 15)."
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 main.py -n 3 -p 0.01 -e 2 -f tikz-graph.tex
	cat tikz-graph.tex

p-plot:
	@echo "Generating probability plot (Fig. 6)."
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 800 -p 0.000000116323325 -p 0.000007813830433 -p 0.000015511337541 -p 0.000038603858866 -p 0.000077091394407 -p 0.000154066465489
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 800 -p 0.000053299160406 -p 0.000060464839143 -p 0.000067630517880 -p 0.000089127554093 -p 0.000124955947779 -p 0.000196612735153

	@echo "Data generated. Generating plot."
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 p-plot_generator.py

n-plot:
	@echo "Generating n (number of vehicles) plot (Fig. 17)."
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 400 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 500 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 600 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 700 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 900 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 1000 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153

	@echo "Data generated. Generating plot."
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 n-plot_generator.py

t-plot:
	@echo "Generating T_PRL plot (Fig. 16)."
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 10 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 20 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 40 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 50 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 60 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 70 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 80 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 90 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 100 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 110 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 120 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 130 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 140 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 150 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 160 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 170 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 180 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 190 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 200 -n 800 -p 0.000000116323325 -p 0.000053299160406 -p 0.000154066465489 -p 0.000196612735153

	@echo "Data generated. Generating plot."
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 t-plot_generator.py

tv-distribution:
	@echo "Generating data for T_v distribution (Fig. 7)."
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 30 -n 800 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 150 -n 800 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 300 -n 800 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 generate_plots.py -e 900 -n 800 -p 0.000196612735153
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 tv-distribution.py

	@echo "Data generated. Generating distribution."
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) python3 tv-distribution.py

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
	docker run $(DOCKER_BINDING) $(DOCKER_NAME) rm -rf cached plots *.tex *.png