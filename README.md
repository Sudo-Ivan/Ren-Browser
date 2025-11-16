# Ren Browser

A browser for the [Reticulum Network](https://reticulum.network/).

> [!WARNING]  
> This is a work-in-progress.

Target platforms: Web, Linux, Windows, MacOS, Android, iOS.

Built using [Flet](https://flet.dev/).

## Renderers

- Micron (default) (WIP)
- Plaintext (fallback and .mu source viewer)

## Development

**Requirements**

- Python 3.13+
- Flet
- Reticulum 1.0.0+
- UV or Poetry

**Setup**

Using UV:
```bash
uv sync
```

Or using Poetry:
```bash
poetry install
```

### Desktop

Using UV:
```bash
# From local development
uv run ren-browser
```

Using Poetry:
```bash
poetry run ren-browser
```

### Web

Using UV:
```bash
# From local development
uv run ren-browser-web
```

Using Poetry:
```bash
poetry run ren-browser-web
```

### Mobile

**Android**

Using UV:
```bash
# From local development
uv run ren-browser-android
```

Using Poetry:
```bash
poetry run ren-browser-android
```

**iOS**

Using UV:
```bash
# From local development
uv run ren-browser-ios
```

Using Poetry:
```bash
poetry run ren-browser-ios
```

To run directly from the GitHub repository without cloning:

```bash
# Using uvx (temporary environment)
uvx --from git+https://github.com/Sudo-Ivan/Ren-Browser.git ren-browser-web

# Or clone and run locally
git clone https://github.com/Sudo-Ivan/Ren-Browser.git
cd Ren-Browser
uv sync
uv run ren-browser-web
```

## Building

### Linux

Using UV:
```bash
uv run flet build linux
```

Using Poetry:
```bash
poetry run flet build linux
```

### Android

Using UV:
```bash
uv run flet build android
```

Using Poetry:
```bash
poetry run flet build android
```