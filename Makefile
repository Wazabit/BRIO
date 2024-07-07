IMAGE_NAME="brio_frontend"
CONTAINER_NAME="brio"
MONGO_CONTAINER_NAME="mongodb"
MONGO_VERSION="7.0-ubi8"
MONGO_USER="brio"
MONGO_PWD="q+Y!h2s+JH*10La"
CURRENT_TIME := $(shell date +"%Y%m%d_%H%M%S")

UNAME := $(shell uname -o)
ifeq ($(UNAME), GNU/Linux)
    HOST_IP=$(shell hostname -I | cut -d ' ' -f1)
endif
ifeq ($(UNAME), Darwin)
    HOST_IP=$(shell osascript -e "IPv4 address of (system info)")
endif

.PHONY: help build test shell stop

help:
	@echo "- make build         Build docker image"
	@echo "- make frontend      Start the frontend application is a container"
	@echo "- make shell		    Open a shell inside docker container"
	@echo "- make stop		    Stop the docker container"


.DEFAULT_GOAL := help

.PHONY: network
network:
	@docker network create -d bridge ${MONGO_CONTAINER_NAME}

.PHONY: build
build:
	@docker build \
		--tag ${IMAGE_NAME}:latest \
		--tag ${IMAGE_NAME}:$$(cat VERSION.txt) \
		.

.PHONY: frontend
frontend: build
	@docker run -dp 80:80 \
		--name ${CONTAINER_NAME} \
		--env HOST_IP=$(HOST_IP) \
		${IMAGE_NAME}

.PHONY: mongodb
mongodb:
	@docker run --name ${MONGO_CONTAINER_NAME} \
		-d -p 27017:27017 \
		mongodb/mongodb-community-server:${MONGO_VERSION}
	@docker cp  datasources/restore/mongo/schema/* ${MONGO_CONTAINER_NAME}:data
	@docker exec -i ${MONGO_CONTAINER_NAME} /usr/bin/mongorestore \
		-d brio \
		data/brio/

mongodb_stop:
	@docker exec -i ${MONGO_CONTAINER_NAME} mkdir -p tmp/brio_${CURRENT_TIME}
	@docker exec -i ${MONGO_CONTAINER_NAME} /usr/bin/mongodump \
		-d brio \
		-o tmp/brio_${CURRENT_TIME}
	@docker cp  ${MONGO_CONTAINER_NAME}:tmp/brio_${CURRENT_TIME}/ 	datasources/backups/mongo/${CURRENT_TIME}/
	@docker stop ${MONGO_CONTAINER_NAME} && docker rm ${MONGO_CONTAINER_NAME}

.PHONY: shell
shell:
	@docker exec -it ${CONTAINER_NAME} /bin/bash

.PHONY: stop
stop:
	@docker stop ${CONTAINER_NAME}
	@docker rm ${CONTAINER_NAME}

.PHONY: test
test:
	@python3 -m tests.unit.TestBiasDetector

.PHONY: venv
venv:
	python3 -m virtualenv .
	. bin/activate; pip install -Ur requirements.txt
	. bin/activate; pip install -Ur requirements-dev.txt

.PHONY: clean
clean:
	-rm -rf build dist
	-rm -rf *.egg-info
	-rm -rf bin lib share pyvenv.cfg
