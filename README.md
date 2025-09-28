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
- Poetry

**Setup**

```bash
poetry install
```

### Desktop

```bash
poetry run ren-browser
```

### Web

```bash
poetry run ren-browser-web
```

### Mobile

**Android**

```bash
poetry run ren-browser-android
```

**iOS**

```bash
poetry run ren-browser-ios
```

### Docker/Podman

```bash
docker build -t ren-browser .
docker run -p 8550:8550 -v ./config:/app/config ren-browser
```

## Building

### Linux

```bash
poetry run flet build linux
```

### Android

```bash
poetry run flet build android
```