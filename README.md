# Ren Browser

A Reticulum Page Browser that can render .mu markup files on nodes and also HTML+CSS files on nodes. 

Uses Iced GUI (Rust) and FastAPI backend (Python).

## Requirements
```
Python 3.13
Rust 1.83.0
```

## Running

```bash
./run.sh
```
or

API:

```bash
pip install -r requirements.txt # or poetry install
python ren-api.py # or poetry run python ren-api.py
```

Iced GUI:

```bash
cargo run
```

## Debugging

```bash
./run.sh -d
```

```bash
cargo run -- --debug
```

```bash
python ren-api.py --debug # or poetry run python ren-api.py --debug
```

### Libraries Used

Python:
```
- rns 0.8.8 (MIT)
- lxmf 0.5.8 (MIT)
- uvicorn 0.34.0 (BSD-3-Clause)
- fastapi 0.115.6 (MIT)
- pydantic 2.10.4 (MIT)
- msgpack 1.1.0 (Apache 2.0)
```

Rust:
```
- Iced 0.10.0 (MIT)
- reqwest 0.11 (Apache 2.0)
- serde 1.0 (Apache 2.0 / MIT)
- serde_json 1.0 (Apache 2.0 / MIT)
- tokio 1.0 (MIT)
- chrono 0.4 (MIT / Apache 2.0)
- log 0.4 (Apache 2.0)
- simple_logger 4.2 (MIT)
```