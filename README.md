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
- UV

**Setup**

```bash
uv sync
```

### Desktop

```bash
# From local development
uv run ren-browser
```

### Web

```bash
# From local development
uv run ren-browser-web
```

### Mobile

**Android**

```bash
# From local development
uv run ren-browser-android
```

**iOS**

```bash
# From local development
uv run ren-browser-ios
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

### Docker/Podman

```bash
docker build -t ren-browser .
docker run -p 8550:8550 -v ./config:/app/config ren-browser
```

## Building

### Linux

```bash
uv run flet build linux
```

### Android

```bash
uv run flet build android
```