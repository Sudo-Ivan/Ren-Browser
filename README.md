# Ren Browser

![Build and Publish Docker Image](https://github.com/Sudo-Ivan/Ren-Browser/actions/workflows/docker.yml/badge.svg)
![Build APK and Linux](https://github.com/Sudo-Ivan/Ren-Browser/actions/workflows/build.yml/badge.svg)

A browser for the [Reticulum Network](https://reticulum.network/). Work-in-progress.

Target platforms: Web, Linux, Windows, MacOS, Android, iOS.

Built using [Flet](https://flet.dev/).

## Renderers

- Micron (default) (WIP)
- Plaintext (fallback and .mu source viewer)

## Development

**Requirements**

- Python 3.13+
- Flet
- Reticulum 0.9.6+
- Poetry

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
