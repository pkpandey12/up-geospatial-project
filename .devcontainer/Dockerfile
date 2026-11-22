# Dev Container image: the same Linux toolchain on Windows, macOS and Linux hosts.
# Multi-arch base (amd64 + arm64), so Apple Silicon runs it natively. Debian 13 (trixie),
# the same release the PostGIS image is built on.
# Learn: docs/learn/devcontainers.md
FROM mcr.microsoft.com/devcontainers/python:3-3.12-trixie

# psql + pg_isready for `make db-up` / `make db-psql`. Debian 13's client is PostgreSQL 17,
# matching the server. (make is already in the base image.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# uv from PyPI, pinned, so every container gets the same version.
ARG UV_VERSION=0.13.9
RUN pip install --no-cache-dir "uv==${UV_VERSION}"

# UP_SITING_DEVCONTAINER switches the Makefile to "inside the container" mode.
# The virtualenv lives OUTSIDE the bind-mounted repo, so it never collides with a .venv
# created on the host (a macOS or Windows .venv holds binaries Linux can't run).
ENV UP_SITING_DEVCONTAINER=1 \
    UV_PROJECT_ENVIRONMENT=/home/vscode/.venv-up-siting \
    UV_LINK_MODE=copy

# Pre-create the uv cache dir owned by vscode, so the named volume mounted there is writable.
RUN mkdir -p /home/vscode/.cache/uv && chown -R vscode:vscode /home/vscode/.cache
