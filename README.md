# Ren Browser

A browser for the [Reticulum Network](https://reticulum.network/). Work-in-progress.

Target platforms: Web, Linux, Windows, MacOS, Android, iOS.

Built using [Flet](https://flet.dev/).

> [!WARNING]  
> Android and Linux builds are currently broken due to a Dart language version compatibility issue in Flet 0.28.3. The webview_flutter_android dependency requires Dart 3.9, but Flutter 3.29.2 only supports up to Dart 3.7. This will be resolved when Flet updates to a newer Flutter version.

Currently, you can find `Linux` and `Android` builds in action artifacts in the [GitHub Actions](https://github.com/Sudo-Ivan/Ren-Browser/actions/workflows/build.yml) page, click on the latest workflow run. More platforms will be added in the future.

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