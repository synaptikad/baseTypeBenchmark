# =============================================================================
# BaseType Benchmark V3 - Makefile
# =============================================================================
# Target: OVH B3-256 (256GB RAM, Ubuntu 22.04)
# Usage: make help
# =============================================================================

.PHONY: help init install docker-up docker-down docker-logs clean \
        benchmark gradient load dry-run test check

# Configuration
SHELL := /bin/bash
PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
BTB := $(VENV)/bin/btb-runner
COMPOSE := docker compose -f docker/docker-compose.yml

# Data directories
DATA_DIR := /data/benchmark
EXPORT_DIR := $(DATA_DIR)/exports
RESULTS_DIR := $(DATA_DIR)/results

# Default RAM levels for gradient (GB)
RAM_LEVELS := 128,64,32,16,8

# =============================================================================
# HELP
# =============================================================================

help:
	@echo "BaseType Benchmark V3"
	@echo ""
	@echo "  make run           - Interactive menu (recommended)"
	@echo ""
	@echo "Setup:"
	@echo "  make init          - Full setup (system + docker + python)"
	@echo "  make install       - Install Python dependencies only"
	@echo "  make check         - Verify installation"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up     - Start all containers"
	@echo "  make docker-down   - Stop all containers"
	@echo "  make docker-logs   - Show container logs"
	@echo "  make docker-ps     - Show container status"
	@echo ""
	@echo "Benchmark:"
	@echo "  make dry-run       - Validate queries without execution"
	@echo "  make load-p1       - Load data into P1 (PostgreSQL)"
	@echo "  make load-m1       - Load data into M1 (Memgraph)"
	@echo "  make gradient-m1   - Quick RAM gradient test on M1"
	@echo "  make benchmark     - Run full benchmark (all paradigms)"
	@echo ""
	@echo "Data:"
	@echo "  make export-small  - Export small dataset"
	@echo "  make export-medium - Export medium dataset"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean         - Remove generated files"
	@echo "  make clean-docker  - Remove Docker volumes"
	@echo ""

# =============================================================================
# SETUP
# =============================================================================

init: init-system init-deps init-docker install
	@echo ""
	@echo "=========================================="
	@echo "Setup complete!"
	@echo "=========================================="
	@echo ""
	@echo "Next steps:"
	@echo "  make check         # Verify installation"
	@echo "  make dry-run       # Validate queries"
	@echo "  make benchmark     # Run full benchmark (runner manages containers)"
	@echo ""

init-system:
	@echo "=== System Setup ==="
	@# Verify cgroups v2
	@if [ -d /sys/fs/cgroup/system.slice ]; then \
		echo "cgroups v2: OK"; \
	else \
		echo "WARNING: cgroups v2 not detected"; \
	fi
	@# Check RAM
	@echo "RAM: $$(free -h | awk '/^Mem:/{print $$2}')"
	@echo "Kernel: $$(uname -r)"
	@echo "CPUs: $$(nproc)"

init-deps:
	@echo "=== Installing Dependencies ==="
	@# Docker
	@if command -v docker &> /dev/null; then \
		echo "Docker: $$(docker --version)"; \
	else \
		echo "Installing Docker..."; \
		curl -fsSL https://get.docker.com | sudo sh; \
		sudo usermod -aG docker $$USER; \
		echo "Docker installed. NOTE: You may need to re-login for group to apply."; \
	fi
	@# Python + venv
	@if command -v python3 &> /dev/null; then \
		echo "Python: $$(python3 --version)"; \
	fi
	@# Always ensure venv is installed (may be missing even if python3 exists)
	@sudo apt-get update -qq && sudo apt-get install -y -qq python3-venv python3-pip python3-dev
	@# Git (should be there but just in case)
	@if ! command -v git &> /dev/null; then \
		sudo apt-get install -y -qq git; \
	fi

init-docker:
	@echo "=== Docker Setup ==="
	@# Check if docker works (user in group)
	@if ! docker info &> /dev/null; then \
		echo "ERROR: Docker not accessible. Try: newgrp docker OR re-login"; \
		exit 1; \
	fi
	@# Pull images
	$(COMPOSE) pull
	@echo "Docker images ready"

install:
	@echo "=== Python Setup ==="
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	@echo "Python environment ready"
	@# Create .env from example if not exists
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env created from .env.example"; \
	fi
	@# Create data directories
	@mkdir -p $(DATA_DIR) $(EXPORT_DIR) $(RESULTS_DIR) 2>/dev/null || true

check:
	@echo "=== Verification ==="
	@echo -n "Python: " && $(VENV)/bin/python --version
	@echo -n "btb-runner: " && $(BTB) --help > /dev/null 2>&1 && echo "OK" || echo "NOT FOUND"
	@echo -n "Docker: " && docker --version
	@echo -n "Compose: " && docker compose version
	@echo ""
	@echo "Containers:"
	@$(COMPOSE) ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Not running"
	@echo ""
	@echo "cgroups v2:"
	@ls -la /sys/fs/cgroup/system.slice/docker-*.scope 2>/dev/null | head -3 || echo "No containers"

# =============================================================================
# DOCKER
# =============================================================================

docker-up:
	@echo "Starting containers..."
	$(COMPOSE) up -d
	@echo "Waiting for health checks..."
	@sleep 5
	$(COMPOSE) ps

docker-down:
	@echo "Stopping containers..."
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f --tail=100

docker-ps:
	$(COMPOSE) ps

docker-restart: docker-down docker-up

# =============================================================================
# DATA LOADING
# =============================================================================

load-p1:
	@echo "Loading data into P1 (PostgreSQL)..."
	$(BTB) load P1 -d $(EXPORT_DIR)/p1 --clear -w 16

load-p2:
	@echo "Loading data into P2 (PostgreSQL JSONB)..."
	$(BTB) load P2 -d $(EXPORT_DIR)/p2 --clear -w 16

load-m1:
	@echo "Loading data into M1 (Memgraph)..."
	$(BTB) load M1 -d $(EXPORT_DIR)/m1m2 --clear -w 8

load-m2:
	@echo "Loading data into M2 (Memgraph + TimescaleDB)..."
	$(BTB) load M2 -d $(EXPORT_DIR)/m1m2 --clear -w 16

load-o2:
	@echo "Loading data into O2 (Oxigraph + TimescaleDB)..."
	$(BTB) load O2 -d $(EXPORT_DIR)/o2 --clear -w 16

load-all: load-p1 load-p2 load-m1 load-m2 load-o2

# =============================================================================
# BENCHMARK
# =============================================================================

dry-run:
	$(BTB) dry-run --matrix

dry-run-verbose:
	$(BTB) dry-run --all --verbose

gradient-m1:
	@echo "RAM gradient test on M1..."
	$(BTB) gradient M1 -d $(EXPORT_DIR)/m1m2 --ram "$(RAM_LEVELS)"

gradient-p1:
	@echo "RAM gradient test on P1..."
	$(BTB) gradient P1 -d $(EXPORT_DIR)/p1 --ram "$(RAM_LEVELS)"

benchmark:
	@echo "Running full benchmark..."
	$(BTB) benchmark \
		-d $(EXPORT_DIR) \
		-o $(RESULTS_DIR)/results_$$(date +%Y%m%d_%H%M%S).json \
		--ram "$(RAM_LEVELS)"

benchmark-quick:
	@echo "Quick benchmark (P1, M1 only)..."
	$(BTB) benchmark \
		-d $(EXPORT_DIR) \
		-o $(RESULTS_DIR)/quick_$$(date +%Y%m%d_%H%M%S).json \
		-p P1,M1 \
		--ram "32,16,8" \
		--runs 3

benchmark-m:
	@echo "Memgraph benchmark (M1, M2)..."
	$(BTB) benchmark \
		-d $(EXPORT_DIR) \
		-o $(RESULTS_DIR)/memgraph_$$(date +%Y%m%d_%H%M%S).json \
		-p M1,M2 \
		--ram "$(RAM_LEVELS)"

# =============================================================================
# DATA EXPORT (requires dataset module)
# =============================================================================

export-small:
	@echo "Exporting small dataset..."
	@mkdir -p $(EXPORT_DIR)
	$(VENV)/bin/python -m basetype_benchmark.dataset.generator \
		--profile small --duration 1w \
		--output $(EXPORT_DIR)

export-medium:
	@echo "Exporting medium dataset..."
	@mkdir -p $(EXPORT_DIR)
	$(VENV)/bin/python -m basetype_benchmark.dataset.generator \
		--profile medium --duration 1m \
		--output $(EXPORT_DIR)

# =============================================================================
# UTILITIES
# =============================================================================

run:
	@$(VENV)/bin/python run.py

shell:
	@$(VENV)/bin/python

run-query:
	@echo "Usage: make run-query Q=Q1 P=P1"
	@echo "Example: make run-query Q=Q7 P=M1"
ifndef Q
	@exit 1
endif
ifndef P
	@exit 1
endif
	$(BTB) run-query $(Q) -p $(P)

# =============================================================================
# CLEANUP
# =============================================================================

clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-docker:
	@echo "Removing Docker volumes..."
	$(COMPOSE) down -v

clean-all: clean clean-docker
	@echo "Removing virtual environment..."
	rm -rf $(VENV)

# =============================================================================
# B3 SPECIFIC
# =============================================================================

b3-setup:
	@echo "=== OVH B3-256 Full Setup ==="
	@chmod +x deploy/ovh_setup.sh
	@./deploy/ovh_setup.sh

b3-info:
	@echo "=== B3 System Info ==="
	@echo "Hostname: $$(hostname)"
	@echo "RAM: $$(free -h | awk '/^Mem:/{print $$2}')"
	@echo "CPUs: $$(nproc)"
	@echo "Kernel: $$(uname -r)"
	@echo ""
	@echo "cgroups v2 memory files:"
	@cat /sys/fs/cgroup/memory.max 2>/dev/null || echo "N/A"
	@echo ""
	@echo "Docker containers:"
	@docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}" 2>/dev/null || echo "No containers"

b3-monitor:
	@echo "Monitoring containers (Ctrl+C to exit)..."
	@watch -n 1 'docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}"'

# =============================================================================
# CGROUPS DEBUG
# =============================================================================

cgroups-info:
	@echo "=== cgroups v2 Info ==="
	@echo "Mount point:"
	@mount | grep cgroup
	@echo ""
	@echo "Docker containers cgroups:"
	@ls -la /sys/fs/cgroup/system.slice/docker-*.scope 2>/dev/null || echo "No containers found"
	@echo ""
	@echo "Memory files (first container):"
	@CGROUP=$$(ls -d /sys/fs/cgroup/system.slice/docker-*.scope 2>/dev/null | head -1); \
	if [ -n "$$CGROUP" ]; then \
		echo "memory.current: $$(cat $$CGROUP/memory.current 2>/dev/null | numfmt --to=iec)"; \
		echo "memory.peak: $$(cat $$CGROUP/memory.peak 2>/dev/null | numfmt --to=iec)"; \
		echo "memory.max: $$(cat $$CGROUP/memory.max 2>/dev/null)"; \
	fi
