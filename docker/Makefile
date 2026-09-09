.PHONY: build tag push

IMAGE_NAME := positro/gr00t-base
GIT_SHA := $(shell git rev-parse --short HEAD)
IMAGE_TAG ?= $(shell git branch --show-current | tr '/' '-')

build:
	docker build --platform linux/amd64 -f Dockerfile -t $(IMAGE_NAME):local ..

tag: build
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):$(IMAGE_TAG)
	docker tag $(IMAGE_NAME):local $(IMAGE_NAME):$(GIT_SHA)

push: tag
	docker push $(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(IMAGE_NAME):$(GIT_SHA)
