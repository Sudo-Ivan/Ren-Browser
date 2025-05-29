FROM python:3.13-alpine

# Install build dependencies for cryptography
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

# Upgrade pip and install application dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir "flet>=0.28.3,<0.29.0" "rns>=0.9.6,<0.10.0"

# Copy application source
WORKDIR /app
COPY . /app

# Expose the web port
EXPOSE 8550

# Run the web version of Ren Browser
CMD ["python3", "-u", "-m", "ren_browser.app", "--web", "--port", "8550"] 