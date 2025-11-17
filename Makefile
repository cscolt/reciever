# Makefile for Desktop Casting Receiver
# Cross-platform build automation

.PHONY: help install dev clean build build-linux build-windows test run run-headless docker-build docker-run

# Default target
help:
	@echo "Desktop Casting Receiver - Build Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install        - Install dependencies"
	@echo "  make dev            - Setup development environment"
	@echo "  make run            - Run application (GUI)"
	@echo "  make run-headless   - Run application (headless)"
	@echo "  make test           - Run diagnostics"
	@echo ""
	@echo "Building:"
	@echo "  make build          - Build for current platform"
	@echo "  make build-linux    - Build Linux executable"
	@echo "  make build-windows  - Build Windows executable"
	@echo "  make clean          - Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run in Docker container"

# Python detection
PYTHON := $(shell command -v python3 2> /dev/null || command -v python 2> /dev/null)
PIP := $(shell command -v pip3 2> /dev/null || command -v pip 2> /dev/null)

# Check if we're on Windows
ifeq ($(OS),Windows_NT)
	PLATFORM := Windows
	VENV_BIN := venv/Scripts
	PYTHON := python
	PIP := pip
else
	PLATFORM := $(shell uname -s)
	VENV_BIN := venv/bin
endif

# Install dependencies
install:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Setup development environment
dev:
	@echo "Setting up development environment..."
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv venv; \
	fi
	@echo "Activating virtual environment and installing dependencies..."
	@. $(VENV_BIN)/activate && $(MAKE) install
	@echo ""
	@echo "✓ Development environment ready!"
	@echo ""
	@echo "Activate with:"
	@echo "  source $(VENV_BIN)/activate  (Linux/Mac)"
	@echo "  $(VENV_BIN)\\activate.bat    (Windows)"

# Run application
run:
	@echo "Starting Desktop Casting Receiver..."
	$(PYTHON) run.py

# Run headless (no GUI)
run-headless:
	@echo "Starting Desktop Casting Receiver (headless mode)..."
	$(PYTHON) run.py --headless

# Run diagnostics
test:
	@echo "Running diagnostics..."
	$(PYTHON) tests/test_diagnostics.py

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.spec
	rm -rf src/__pycache__ src/*/__pycache__
	rm -rf *.pyc src/*.pyc src/*/*.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Clean complete"

# Build for current platform
build:
ifeq ($(PLATFORM),Windows)
	@$(MAKE) build-windows
else
	@$(MAKE) build-linux
endif

# Build Linux executable
build-linux:
	@echo "Building for Linux..."
	@cd build/linux && bash build.sh

# Build Windows executable
build-windows:
	@echo "Building for Windows..."
	@cd build/windows && cmd /c build.bat

# Docker build
docker-build:
	@echo "Building Docker image..."
	docker build -t desktop-casting-receiver:latest .

# Docker run
docker-run:
	@echo "Running in Docker..."
	docker run -it --rm \
		-p 8080:8080 \
		-p 7000:7000 \
		-p 7100:7100 \
		--name desktop-casting-receiver \
		desktop-casting-receiver:latest

# Format code (optional, if black/autopep8 installed)
format:
	@echo "Formatting code..."
	@command -v black >/dev/null 2>&1 && black src/ || echo "black not installed (pip install black)"

# Lint code (optional, if pylint/flake8 installed)
lint:
	@echo "Linting code..."
	@command -v pylint >/dev/null 2>&1 && pylint src/ || echo "pylint not installed (pip install pylint)"
