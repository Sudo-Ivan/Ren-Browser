# Ren Browser Basic Test Suite

## To-Do

- Security tests
- Performance tests
- Proper RNS support and testing
- Micron Renderer tests (when implemented)

This directory contains comprehensive tests for the Ren Browser application.

## Test Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for component interactions
- `conftest.py` - Shared test fixtures and configuration

## Running Tests

### All Tests
```bash
poetry run pytest
```

### Unit Tests Only
```bash
poetry run pytest tests/unit/
```

### Integration Tests Only
```bash
poetry run pytest tests/integration/
```

### Specific Test File
```bash
poetry run pytest tests/unit/test_app.py
```

### With Coverage
```bash
poetry run pytest --cov=ren_browser --cov-report=html
```