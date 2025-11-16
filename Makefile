# Ren Browser Makefile
.PHONY: help build poetry-build linux apk clean test lint format

# Default target
help:
	@echo "Ren Browser Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  build              - Build the project (alias for poetry-build)"
	@echo "  poetry-build       - Build project with Poetry"
	@echo "  linux              - Build Linux package"
	@echo "  apk                - Build Android APK"
	@echo "  test               - Run tests"
	@echo "  lint               - Run linter"
	@echo "  format             - Format code"
	@echo "  clean              - Clean build artifacts"
	@echo "  help               - Show this help"

# Main build target
build: poetry-build

# Poetry build
poetry-build:
	@echo "Building project with Poetry..."
	poetry build

# Linux package build
linux:
	@echo "Building Linux package..."
	poetry run flet build linux

# Android APK build
apk:
	@echo "Building Android APK..."
	poetry run flet build apk --cleanup-packages --exclude watchdog

# Development targets
test:
	@echo "Running tests..."
	poetry run pytest

lint:
	@echo "Running linter..."
	poetry run ruff check .

format:
	@echo "Formatting code..."
	poetry run ruff format .

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete