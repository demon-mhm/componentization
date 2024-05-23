SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

DOT:=.
DASH:=-
SLASH:=/

export DOCKER_BUILDKIT = 1
ifndef CI_PROJECT_PATH
export CI_PROJECT_PATH = $(shell python utils/pyproject.py project.name)
endif
ifndef CI_PROJECT_PATH_SLUG
export CI_PROJECT_PATH_SLUG = $(subst $(DOT),$(DASH),$(CI_PROJECT_PATH))
endif
ifndef CI_COMMIT_REF_SLUG
export CI_COMMIT_REF_SLUG = $(subst $(SLASH),$(DASH),$(shell git symbolic-ref --short HEAD))
endif
export TAG = $(shell git describe)
ifndef CI_COMMIT_SHORT_SHA
export CI_COMMIT_SHORT_SHA = $(shell git rev-parse --short HEAD )
endif

ifndef RABBITMQ_DSN
export RABBITMQ_DSN := amqp://guest:guest@localhost:5672
endif
ifndef PIP_INDEX_URL
export PIP_INDEX_URL = https://pip-yc:p6iHshE5@nexus.qsrapp.ru/repository/pypi-group/simple
endif
ifndef YA_REGISTRY
export YA_REGISTRY = cr.yandex/crp6sr2nghu2nr05j1j2
endif


.venv: 
	 python -m venv .venv
	 .venv/bin/pip install --upgrade pip

lib: pyproject.toml .venv
	 .venv/bin/pip install --editable '.[develop]'

wires: $(wildcard wire/**/requirements.txt) .venv
	$(foreach wire,$(wildcard wire/*), .venv/bin/pip install -r $(wire)/requirements.txt)

local: lib wires

build: 
	docker build \
		--no-cache \
		--tag=${YA_REGISTRY}/$(CI_PROJECT_PATH_SLUG)-$(wire):${CI_COMMIT_SHORT_SHA}-${CI_COMMIT_REF_SLUG}
		--file=wire/$(wire)/Dockerfile \
		--network=host \
		.

proto:
	.venv/bin/python utils/generate_proto.py

tmp/.tests-passed.sentinel: $(shell find src -type f) $(shell find tests -type f) pyproject.toml local
	mkdir -p $(@D)
	.venv/bin/python -m pytest $(name)
	touch $@

test: tmp/.tests-passed.sentinel
 
adapter-up:
	uvicorn wire.adapter.main:app

stop:
	docker compose stop

clean:
	rm -rf \
		tmp \
		.venv \
		.mypy_cache \
		.pytest_cache \
		.coverage 
	find ./src -name "*_pb2.py*" -type f -delete
	find ./wire -name "*_pb2.py*" -type f -delete

reset: clean local
