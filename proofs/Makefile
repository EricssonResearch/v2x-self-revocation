IMAGE           ?= selfrevocation/tamarin
VERSION         ?= v1.6.1
NAME            ?= tamarin
MODEL           ?= centralized-time
THREADS         ?= 4
OUT_FILE        ?= output.spthy   

ENV              = -e LC_ALL=C.UTF-8
VOLUME           = $(shell cd $(MODEL); pwd)
OUT_FOLDER       = $(shell pwd)/out

prove: clean __create_out
	docker run --name $(NAME) --entrypoint tamarin-prover $(ENV) -d -v $(OUT_FOLDER):/home/tamarin $(IMAGE):$(VERSION) --prove --output=$(OUT_FILE) theory.spthy +RTS -N$(THREADS) -RTS

interactive: clean __create_out
	docker run --name $(NAME) --entrypoint tamarin-prover $(ENV) --network host -d -v $(OUT_FOLDER):/home/tamarin $(IMAGE):$(VERSION) interactive theory.spthy +RTS -N$(THREADS) -RTS

test: clean __create_out
	docker run --name $(NAME) --entrypoint tamarin-prover $(ENV) -v $(OUT_FOLDER):/home/tamarin $(IMAGE):$(VERSION) --prove=sign_possible theory.spthy

clean:
	@docker stop $(NAME) || true
	@docker rm $(NAME) || true

__create_out:
	@mkdir -p $(OUT_FOLDER)
	@chmod o+rw $(OUT_FOLDER)
	@cp $(MODEL)/theory.spthy $(OUT_FOLDER)
	@cp $(MODEL)/oracle.py $(OUT_FOLDER)