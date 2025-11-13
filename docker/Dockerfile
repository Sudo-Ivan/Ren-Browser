ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-alpine

LABEL org.opencontainers.image.source="https://github.com/Sudo-Ivan/Ren-Browser"
LABEL org.opencontainers.image.description="A browser for the Reticulum Network."
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Sudo-Ivan"

WORKDIR /app

RUN apk add --no-cache gcc python3-dev musl-dev linux-headers libffi-dev openssl-dev

RUN pip install --no-cache poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

COPY pyproject.toml poetry.lock* ./
COPY README.md ./
COPY ren_browser ./ren_browser

RUN poetry install --no-interaction --no-ansi --no-cache

RUN chown -R 1000:1000 /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
ENV FLET_WEB_PORT=8550
ENV FLET_WEB_HOST=0.0.0.0
ENV DISPLAY=:99

EXPOSE 8550

ENTRYPOINT ["poetry", "run", "ren-browser-web"] 