# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
# not intended for use outside of vscode. Arm64-support needs testing.
ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT} AS base

LABEL org.opencontainers.image.source=https://github.com/dotkom/onlineweb4
LABEL org.opencontainers.image.authors=dotkom

WORKDIR /workspace
ENV PYTHONUNBUFFERED=1 POETRY_VIRTUALENVS_IN_PROJECT=true

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

RUN pipx install poetry==1.1.13 \
    && apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        libjpeg-dev \
        git

FROM base AS with-dependencies

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root --no-ansi

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile --non-interactive
