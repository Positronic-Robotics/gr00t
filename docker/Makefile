.PHONY: all build tag push clean prune help

# Image configuration
IMAGE_NAME_GROOT := positronic-groot
IMAGE_NAME_BASE := positronic-base

# Extract version from pyproject.toml (first literal version entry)
VERSION := $(shell sed -n 's/^version = "\([^"]*\)"/\1/p' ../pyproject.toml | head -n 1)

# Get git commit SHA (short)
GIT_SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Get Nebius configuration from CLI
# Extract registry info from JSON format
REGISTRY_INFO := $(shell nebius registry list --format json 2>/dev/null | jq -r '.items[] | select(.metadata.name=="positronic") | .metadata.id + " " + .status.registry_fqdn' || echo "")
NB_REGISTRY_PATH := $(shell echo "$(REGISTRY_INFO)" | cut -d' ' -f1 | cut -d- -f2)
NB_REGISTRY_FQDN := $(shell echo "$(REGISTRY_INFO)" | cut -d' ' -f2)

# Full registry URL
REGISTRY_URL := $(NB_REGISTRY_FQDN)/$(NB_REGISTRY_PATH)

# Image tags for groot
TAG_GROOT_LATEST := $(REGISTRY_URL)/$(IMAGE_NAME_GROOT):latest
TAG_GROOT_VERSION := $(REGISTRY_URL)/$(IMAGE_NAME_GROOT):v$(VERSION)
TAG_GROOT_SHA := $(REGISTRY_URL)/$(IMAGE_NAME_GROOT):$(GIT_SHA)
LOCAL_TAG_GROOT := $(IMAGE_NAME_GROOT):local

# Base image to consume (default to registry latest, overridable via BASE_IMAGE=)
BASE_IMAGE_DEFAULT := $(if $(REGISTRY_URL),$(REGISTRY_URL)/$(IMAGE_NAME_BASE):latest,$(IMAGE_NAME_BASE):latest)
BASE_IMAGE ?= $(BASE_IMAGE_DEFAULT)

help:
	@echo "gr00t Groot Docker Build System"
	@echo ""
	@echo "Configuration:"
	@echo "  Groot Image:   $(IMAGE_NAME_GROOT)"
	@echo "  Base Image:    $(BASE_IMAGE)"
	@echo "  Version:       $(VERSION)"
	@echo "  Git SHA:       $(GIT_SHA)"
	@echo "  Registry URL:  $(REGISTRY_URL)"
	@echo ""
	@echo "Targets:"
	@echo "  make build     Build the groot image (depends on registry base)"
	@echo "  make tag       Tag the groot image"
	@echo "  make push      Push groot tags to Nebius"
	@echo "  make clean     Remove local groot images"
	@echo "  make prune     Remove dangling/unused Docker images"
	@echo "  make help      Show this help message"
	@echo ""
	@echo "Override BASE_IMAGE to pin to a specific base (e.g. BASE_IMAGE=\$$TAG_BASE_VERSION)."

build:
	@echo "Building $(IMAGE_NAME_GROOT) image from $(BASE_IMAGE)..."
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: Could not extract version from pyproject.toml"; \
		exit 1; \
	fi
	docker build --platform linux/amd64 \
		--build-arg BASE_IMAGE=$(BASE_IMAGE) \
		-f Dockerfile.groot \
		-t $(LOCAL_TAG_GROOT) ..

tag: build
	@echo "Tagging groot image with multiple tags..."
	@if [ -z "$(NB_REGISTRY_FQDN)" ] || [ -z "$(NB_REGISTRY_PATH)" ]; then \
		echo "Error: Nebius configuration not found. Please ensure:"; \
		echo "  1. Nebius CLI is configured (run: nebius config list)"; \
		echo "  2. Registry 'positronic' exists (run: nebius registry list)"; \
		exit 1; \
	fi
	docker tag $(LOCAL_TAG_GROOT) $(TAG_GROOT_LATEST)
	docker tag $(LOCAL_TAG_GROOT) $(TAG_GROOT_VERSION)
	docker tag $(LOCAL_TAG_GROOT) $(TAG_GROOT_SHA)
	@echo "Tagged with:"
	@echo "  - $(TAG_GROOT_LATEST)"
	@echo "  - $(TAG_GROOT_VERSION)"
	@echo "  - $(TAG_GROOT_SHA)"

push: tag
	@echo "Pushing groot images to Nebius Container Registry..."
	docker push $(TAG_GROOT_LATEST)
	docker push $(TAG_GROOT_VERSION)
	docker push $(TAG_GROOT_SHA)
	@echo ""
	@echo "Successfully pushed groot images to Nebius Container Registry!"
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
