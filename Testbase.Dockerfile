FROM python:3.9.5
LABEL maintainer="Dotkom <dotkom@online.ntnu.no>"

ENV POETRY_VIRTUALENVS_CREATE=false

# Install deps
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - && \
    apt-get update && \
    apt-get remove -y curl && \
    apt-get install -y --no-install-recommends \
    nodejs libjpeg-dev ghostscript && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/* && \
    npm install -g less && \
    npm install -g yarn && \
    pip install poetry
