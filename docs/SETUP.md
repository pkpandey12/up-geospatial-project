# Setting up your machine (Linux)

You have git. You need **Docker Engine with the Compose plugin**, **uv** and **make**.
The steps below are for Ubuntu/Debian; for Fedora, Arch and others follow the linked docs.

## 1. make

```bash
sudo apt-get update && sudo apt-get install -y make
```

## 2. Docker Engine + Compose plugin

Official steps: https://docs.docker.com/engine/install/ubuntu/ (Debian: replace `ubuntu`
with `debian` in the URLs). In short:

```bash
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Let your user run docker without `sudo`, then **log out and back in** (or run `newgrp docker`):

```bash
sudo usermod -aG docker "$USER"
```

Check (should print "Hello from Docker!" and a Compose v2 version):

```bash
docker run --rm hello-world && docker compose version
```

> Don't install the old `docker-compose` (v1, with a hyphen) package; the Makefile uses
> `docker compose` (v2, a plugin).

## 3. uv

Official: https://docs.astral.sh/uv/getting-started/installation/

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open a new terminal, then check with `uv --version`. You don't need to install Python yourself:
uv downloads the version pinned in `.python-version` (3.12) on first `uv sync`.

## 4. The project

```bash
git clone https://github.com/pkpandey12/up-geospatial-project.git
cd up-geospatial-project
make setup     # checks tools, creates .env, installs Python + packages, installs git hooks
make test      # unit + notebook tests (your TODOs show as "x" = expected fail)
make lint      # ruff + profile validation
make db-up     # starts PostGIS, waits until healthy, runs the smoke test
```

If `make db-up` says port 5432 is already in use, you have a local Postgres running.
Either stop it (`sudo systemctl stop postgresql`) or set `POSTGRES_PORT=5433` in `.env`.

## 5. Your data files

Downloads live under `data/raw/<source_id>/ingest_date=YYYY-MM-DD/` (git-ignored). For EDA 01,
put the LGD PDF you downloaded at:

```
data/raw/lgd/ingest_date=2026-11-21/Districts_of_Uttar_Pradesh_State.pdf
```

(A copy is also committed as a test fixture in `tests/fixtures/lgd/`.)
