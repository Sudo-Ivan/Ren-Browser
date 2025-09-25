# Contributing to Ren Browser

I welcome all contributions to the project.

## Places to help out

- Styling/Design (I am bad at this)
- Documentation
- Micron Renderer/Parser
- Android and Flet (config/permissions/etc)

## Project Structure

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
2. If you use an AI tool that generates the code, such as a LLM, please indicate that in the PR.
3. Add or update docstrings and tests if necessary.
4. Make sure you run the tests before submitting the PR.

## Testing

To run the tests, use the following command:

```bash
poetry run pytest
```