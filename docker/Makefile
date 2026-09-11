.PHONY: all build tag push clean prune help

# Image configuration
IMAGE_NAME_GROOT := positro/gr00t-base

# Extract version from pyproject.toml (first literal version entry)
VERSION := $(shell sed -n 's/^version = "\([^"]*\)"/\1/p' ../pyproject.toml | head -n 1)

GIT_SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

REGISTRY_URL ?= docker.io

TAG_GROOT_LATEST := $(IMAGE_NAME_GROOT):latest
TAG_GROOT_VERSION := $(IMAGE_NAME_GROOT):v$(VERSION)
TAG_GROOT_SHA := $(IMAGE_NAME_GROOT):$(GIT_SHA)
LOCAL_TAG_GROOT := $(IMAGE_NAME_GROOT):local

help:
	@echo "gr00t Groot Docker Build System"
	@echo ""
	@echo "Configuration:"
	@echo "  Groot Image:   $(IMAGE_NAME_GROOT)"
	@echo "  Version:       $(VERSION)"
	@echo "  Git SHA:       $(GIT_SHA)"
	@echo "  Registry URL:  $(REGISTRY_URL)"
	@echo ""
	@echo "Targets:"
	@echo "  make build     Build the groot image"
	@echo "  make tag       Tag the groot image"
	@echo "  make push      Push groot tags to Docker Hub"
	@echo "  make clean     Remove local groot images"
	@echo "  make prune     Remove dangling/unused Docker images"
	@echo "  make help      Show this help message"
	@echo ""

build:
	@echo "Building $(IMAGE_NAME_GROOT) image..."
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: Could not extract version from pyproject.toml"; \
		exit 1; \
	fi
	docker build \
		-f Dockerfile \
		-t $(LOCAL_TAG_GROOT) ..

tag: build
	@echo "Tagging groot image with multiple tags..."
	docker tag $(LOCAL_TAG_GROOT) $(TAG_GROOT_LATEST)
	docker tag $(LOCAL_TAG_GROOT) $(TAG_GROOT_VERSION)
	docker tag $(LOCAL_TAG_GROOT) $(TAG_GROOT_SHA)
	@echo "Tagged with:"
	@echo "  - $(TAG_GROOT_LATEST)"
	@echo "  - $(TAG_GROOT_VERSION)"
	@echo "  - $(TAG_GROOT_SHA)"

push: tag
	@echo "Pushing groot images to Docker Hub..."
	docker push $(TAG_GROOT_LATEST)
	docker push $(TAG_GROOT_VERSION)
	docker push $(TAG_GROOT_SHA)
	@echo ""
	@echo "Successfully pushed groot images to Docker Hub!"
	@echo "To use on cloud instances, set:"
	@echo "  export IMAGE_REGISTRY=$(REGISTRY_URL)/"

all: push

clean:
	@echo "Removing local groot images..."
	-docker rmi $(LOCAL_TAG_GROOT)
	-docker rmi $(TAG_GROOT_LATEST)
	-docker rmi $(TAG_GROOT_VERSION)
	-docker rmi $(TAG_GROOT_SHA)
	@echo "Cleanup complete."

prune:
	@echo "Pruning dangling and unused Docker images..."
	docker image prune -f
	@echo "Prune complete."
