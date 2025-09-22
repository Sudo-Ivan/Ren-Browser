# Ren Browser Makefile
.PHONY: help build poetry-build linux apk docker-build docker-build-multi docker-run docker-stop clean test lint format

# Default target
help:
	@echo "Ren Browser Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  build              - Build the project (alias for poetry-build)"
	@echo "  poetry-build       - Build project with Poetry"
	@echo "  linux              - Build Linux package"
	@echo "  apk                - Build Android APK"
	@echo "  docker-build       - Build Docker image with Buildx"
	@echo "  docker-build-multi - Build multi-platform Docker image"
	@echo "  docker-run         - Run Docker container"
	@echo "  docker-stop        - Stop Docker container"
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
	poetry run flet build apk

# Docker targets
docker-build:
	@echo "Building Docker image with Buildx..."
	docker buildx build -t ren-browser --load .

docker-build-multi:
	@echo "Building multi-platform Docker image..."
	docker buildx build -t ren-browser-multi --platform linux/amd64,linux/arm64 --push .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8550:8550 --name ren-browser-container ren-browser

docker-stop:
	@echo "Stopping Docker container..."
	docker stop ren-browser-container || true
	docker rm ren-browser-container || true

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
	docker rmi ren-browser || true
