IMAGE           ?= selfrevocation/tamarin
VERSION         ?= v1.8.0
NAME            ?= tamarin
MODEL           ?= centralized-time
THREADS         ?= 4
OUT_FILE        ?= output.spthy
LEMMA           ?=

ENV              = -e LC_ALL=C.UTF-8
VOLUME           = $(shell cd $(MODEL); pwd)
OUT_FOLDER       = $(shell pwd)/out

BACKGROUND      ?= 

ifdef BACKGROUND
DOCKER_DETACHED  = -d
endif

LEMMAS		  ?= $(shell echo $(LEMMA) | sed s/,/" --prove="/g)

MKDIR           ?= mkdir -m 777 -p

check: clean_docker __create_out
	docker run --name $(NAME) $(DOCKER_DETACHED) --entrypoint tamarin-prover $(ENV) -v $(OUT_FOLDER):/home/tamarin $(IMAGE):$(VERSION) -v theory.spthy

prove: clean_docker __create_out
	docker run --name $(NAME) $(DOCKER_DETACHED) --entrypoint tamarin-prover $(ENV) -v $(OUT_FOLDER):/home/tamarin $(IMAGE):$(VERSION) --prove=$(LEMMAS) --output=$(OUT_FILE) theory.spthy +RTS -N$(THREADS) -RTS

interactive: clean_docker __create_out
	docker run --name $(NAME) --entrypoint tamarin-prover $(ENV) --network host -d -v $(OUT_FOLDER):/home/tamarin $(IMAGE):$(VERSION) interactive theory.spthy +RTS -N$(THREADS) -RTS

test: clean_docker __create_out
	docker run --name $(NAME)  $(DOCKER_DETACHED) --entrypoint tamarin-prover $(ENV) -v $(OUT_FOLDER):/home/tamarin $(IMAGE):$(VERSION) --prove=all_heartbeats_processed_within_tolerance --output=$(OUT_FILE) theory.spthy +RTS -N$(THREADS) -RTS

clean: clean_docker
	rm -rf out

clean_docker:
	@docker stop $(NAME) || true
	@docker rm $(NAME) || true

__create_out:
	@$(MKDIR) $(OUT_FOLDER)
	@cp $(MODEL)/theory.spthy $(OUT_FOLDER)
	@cp $(MODEL)/oracle.py $(OUT_FOLDER)