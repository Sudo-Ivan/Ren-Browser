# Ren Browser

A browser for the [Reticulum Network](https://reticulum.network/). Work-in-progress.

Target platforms: Web, Linux, Windows, MacOS, Android, iOS.

Built using [Flet](https://flet.dev/).

Currently, you can find `Linux` and `Android` builds in action artifacts in the [GitHub Actions](https://github.com/Sudo-Ivan/ren-browser/actions) page, click on the latest workflow run. More platforms will be added in the future.

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