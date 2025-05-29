# Ren Browser

A browser for the [Reticulum Network](https://reticulum.network/). Work-in-progress.

Target platforms: Web, Linux, Windows, MacOS, Android, iOS.

Built using [Flet](https://flet.dev/).

## Development

**Requirements**

- Python 3.13+
- Flet
- Reticulum 0.9.6+

**Setup**

```bash
poetry install
```

### Desktop

```bash
poetry run ren-browser-dev
```

### Web

```bash
poetry run ren-browser-web-dev
```

### Mobile

**Android**

```bash
poetry run ren-browser-android-dev
```

**iOS**

```bash
poetry run ren-browser-ios-dev
```

### Docker/Podman

```bash
docker build -t ren-browser .
docker run -p 8550:8550 ren-browser
```

## Building

