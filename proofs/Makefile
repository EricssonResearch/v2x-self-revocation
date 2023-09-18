IMAGE           ?= selfrevocation/tamarin
VERSION         ?= v1.6.1
NAME            ?= tamarin
MODEL           ?= centralized-time
THREADS         ?= 4

ENV              = -e LC_ALL=C.UTF-8
VOLUME           = $(shell cd $(MODEL); pwd)
OUT_FOLDER       = $(shell pwd)/out

prove: clean __create_out
	docker run --name $(NAME) -it $(ENV) -d -v $(OUT_FOLDER):/home/tamarin $(IMAGE):$(VERSION) tamarin-prover --prove --output=output.spthy theory.spthy +RTS -N$(THREADS) -RTS

interactive: clean __create_out
	docker run --name $(NAME) -it $(ENV) --network host -d -v $(OUT_FOLDER):/home/tamarin $(IMAGE):$(VERSION) tamarin-prover interactive theory.spthy +RTS -N$(THREADS) -RTS

clean:
	@docker stop $(NAME) || true
	@docker rm $(NAME) || true

__create_out:
	@rm -rf $(OUT_FOLDER)
	@mkdir -p $(OUT_FOLDER)
	@chmod o+rw $(OUT_FOLDER)
	@cp $(MODEL)/theory.spthy $(OUT_FOLDER)
	@cp $(MODEL)/oracle.py $(OUT_FOLDER)