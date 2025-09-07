


# Rover Operations Monorepo - Makefile
#
# This Makefile provides common build, test, and deployment targets for the entire project.
#

# Shell options
SHELL := /bin/bash

# Project directories
PROJECT_ROOT := $(shell pwd)
SDK_PYTHON := $(PROJECT_ROOT)/sdk/python
SDK_TYPESCRIPT := $(PROJECT_ROOT)/sdk/typescript
WEB_CONSOLE := $(PROJECT_ROOT)/web/console
EDGE_AGENT := $(PROJECT_ROOT)/edge/agent
SIM_TRACTOR := $(PROJECT_ROOT)/sim/tractor-sim

# Docker Compose configuration
DOCKER_COMPOSE_FILE := docker-compose.yml

# Common Go build flags
GO_BUILD_FLAGS := -v --ldflags="-s -w"

# Help target
help:
	@echo "Rover Operations Makefile"
	@echo ""
	@echo "Common targets:"
	@echo "  help                Show this help message"
	@echo ""
	@echo "Development environment setup:"
	@echo "  dev-up              Start all development services with docker-compose"
	@echo "  dev-down            Stop and remove development containers"
	@echo "  dev-logs            View logs from running development services"
	@echo ""
	@echo "Service-specific targets:"
	@echo "  build-sim           Build the tractor simulation service"
	@echo "  run-sim             Start the tractor simulation service"
	@echo "  build-edge          Build the edge agent"
	@echo "  run-edge            Start the edge agent with hello-tractor driver"
	@echo "  build-web           Build the web console"
	@echo "  run-web             Start the web console"
	@echo ""
	@echo "Testing:"
	@echo "  test                Run all tests in the project"
	@echo "  lint                Run linters for code quality checks"

.PHONY: help dev-up dev-down dev-logs build-sim run-sim build-edge run-edge build-web run-web test lint

# Development environment targets
dev-up:
	docker-compose -f $(DOCKER_COMPOSE_FILE) up --detach

dev-down:
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

dev-logs:
	docker-compose -f $(DOCKER_COMPOSE_FILE) logs -f

# Service build and run targets
build-sim: go-build SIM_TRACTOR
	cd $(SIM_TRACTOR) && docker build -t rover-operations/tractor-sim .

run-sim: dev-up
	docker-compose -f $(DOCKER_COMPOSE_FILE) exec tractor-sim ./tractor-sim

build-edge:
	cd $(EDGE_AGENT) && docker build -t rover-operations/edge-agent .

run-edge: dev-up
	docker-compose -f $(DOCKER_COMPOSE_FILE) exec edge-agent ./edge-agent --config /app/config.yaml

build-web:
	cd $(WEB_CONSOLE) && yarn install && yarn build

run-web: dev-up
	docker-compose -f $(DOCKER_COMPOSE_FILE) exec web-console yarn start

# Testing targets
test:
	@echo "Running tests..."
	$(MAKE) test-python
	$(MAKE) test-typescript
	$(MAKE) test-go

lint:
	@echo "Running linters..."
	$(MAKE) lint-python
	$(MAKE) lint-typescript
	$(MAKE) lint-go

# Python-specific targets
test-python:
	cd $(SDK_PYTHON) && python -m pytest tests/

lint-python:
	cd $(SDK_PYTHON) && flake8 .

# TypeScript-specific targets
test-typescript:
	cd $(SDK_TYPESCRIPT) && yarn test

lint-typescript:
	cd $(SDK_TYPESCRIPT) && yarn lint

# Go-specific targets (generic)
go-build: go-mod-tidy
	@echo "Building Go services..."
	$(MAKE) build-sim
	$(MAKE) build-edge
	$(MAKE) build-control-broker
	$(MAKE) build-signaling
	$(MAKE) build-telemetry
	$(MAKE) build-policy-engine
	$(MAKE) build-billing
	$(MAKE) build-replay
	$(MAKE) build-api-gateway

go-mod-tidy:
	@echo "Tidying Go modules..."
	for dir in $(PROJECT_ROOT)/services/* $(PROJECT_ROOT)/edge/agent $(PROJECT_ROOT)/sim/tractor-sim; do \
		if [ -f "$$dir/go.mod" ]; then cd $$dir && go mod tidy; fi \
	done

build-control-broker:
	cd $(PROJECT_ROOT)/services/control-broker && docker build -t rover-operations/control-broker .

build-signaling:
	cd $(PROJECT_ROOT)/services/signaling && docker build -t rover-operations/signaling-server .

build-telemetry:
	cd $(PROJECT_ROOT)/services/telemetry && docker build -t rover-operations/telemetry-service .

build-policy-engine:
	cd $(PROJECT_ROOT)/services/policy-engine && docker build -t rover-operations/policy-engine .

build-billing:
	cd $(PROJECT_ROOT)/services/billing && docker build -t rover-operations/billing-service .

build-replay:
	cd $(PROJECT_ROOT)/services/replay && docker build -t rover-operations/replay-service .

build-api-gateway:
	cd $(PROJECT_ROOT)/services/api-gateway && docker build -t rover-operations/api-gateway .

