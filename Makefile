# Fake Trading Price Simulator - Makefile

# Variables
PYTHON = python3
PYTEST = pytest
COVERAGE = coverage
BLACK = black
FLAKE8 = flake8
MYPY = mypy

# Directories
SRC_DIR = .
TEST_DIR = .

# Files
MAIN_FILE = faketrading.py
TEST_FILE = test_faketrading.py
DATA_FILE = data.json

# Default target
.PHONY: all
all: test lint format

# Run the simulator
.PHONY: run
run:
	@echo "Running Fake Trading Price Simulator..."
	$(PYTHON) $(MAIN_FILE)

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	$(PYTHON) -m pytest $(TEST_FILE) -v

# Run tests with coverage
.PHONY: test-cov
test-cov:
	@echo "Running tests with coverage..."
	$(PYTHON) -m pytest $(TEST_FILE) --cov=$(SRC_DIR) --cov-report=html --cov-report=term

# Lint code
.PHONY: lint
lint:
	@echo "Linting code..."
	$(FLAKE8) $(MAIN_FILE) $(TEST_FILE)

# Format code
.PHONY: format
format:
	@echo "Formatting code..."
	$(BLACK) $(MAIN_FILE) $(TEST_FILE)

# Type checking
.PHONY: typecheck
typecheck:
	@echo "Running type checks..."
	$(MYPY) $(MAIN_FILE) $(TEST_FILE)

# Security checks
.PHONY: security
security:
	@echo "Running security checks..."
	@echo "Checking for common security issues..."
	@grep -n "eval\|exec\|input\|raw_input" $(MAIN_FILE) || echo "No obvious security issues found"
	@echo "Checking file permissions..."
	@ls -la $(MAIN_FILE) $(DATA_FILE)

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning generated files..."
	rm -f simulation_results.json
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage

# Install development dependencies
.PHONY: install-dev
install-dev:
	@echo "Installing development dependencies..."
	pip install pytest pytest-cov black flake8 mypy

# Validate data file
.PHONY: validate-data
validate-data:
	@echo "Validating data.json..."
	$(PYTHON) -c "import json; data=json.load(open('$(DATA_FILE)')); print('Data file is valid JSON')"
	$(PYTHON) -c "from faketrading import PriceSimulator; s=PriceSimulator(); s.load_market_data(); print('Market data validation passed')"

# Quick validation
.PHONY: validate
validate: validate-data lint typecheck

# Help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  run          - Run the simulator"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Lint code with flake8"
	@echo "  format       - Format code with black"
	@echo "  typecheck    - Run type checking with mypy"
	@echo "  security     - Run security checks"
	@echo "  clean        - Clean generated files"
	@echo "  install-dev  - Install development dependencies"
	@echo "  validate     - Validate data and code"
	@echo "  help         - Show this help message"
