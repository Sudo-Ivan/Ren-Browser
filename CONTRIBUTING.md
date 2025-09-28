# Contributing to Ren Browser

I welcome all contributions to the project.

## Places to help out

- Styling/Design (I am bad at this)
- Documentation
- Micron Renderer/Parser
- Android and Flet (config/permissions/etc)

## Project Structure

Last Updated: 2025-09-28

```
Ren-Browser/
├── ren_browser/                   # Main Python application package
│   ├── announces/                 # Reticulum network announce handling
│   │   ├── announces.py
│   ├── app.py                     # Main application entry point
│   ├── controls/                  # UI controls and interactions
│   │   ├── shortcuts.py          # Keyboard shortcuts handling
│   ├── logs.py                    # Centralized logging system
│   ├── pages/                     # Page fetching and request handling
│   │   ├── page_request.py
│   ├── profiler/                  # Performance profiling (placeholder)
│   ├── renderer/                  # Content rendering system
│   │   ├── micron.py             # Micron markup renderer (WIP)
│   │   └── plaintext.py          # Plaintext fallback renderer
│   ├── storage/                   # Cross-platform storage management
│   │   ├── storage.py
│   ├── tabs/                      # Tab management system
│   │   ├── tabs.py
│   ├── ui/                        # User interface components
│   │   ├── settings.py           # Settings interface
│   │   └── ui.py                 # Main UI construction
├── tests/                         # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── conftest.py               # Test configuration
```

## Rules

1. Be nice to each other.

## Generative AI Usage

You are allowed to use generative AI tools to help learn and contribute. You do not need to disclose you used a AI tool, although that would help me scrutinize the PR more for bugs, errors or security flaws. 

## Linting, Security and Tests

You are not required to run the linting, security and tests before submitting the PR as those will be run by the CI/CD pipeline.

## Testing

To run the tests, use the following command:

```bash
poetry run pytest
```