# Setting up your machine (Windows, macOS, Linux)

There are two ways to work on this project. Both use the same `make` commands and the same
PostGIS container, and CI tests both on every push.

| | **A. Dev Container** | **B. On your host** |
|---|---|---|
| What runs where | Python, uv, make, psql run in a Linux container your editor opens; PostGIS runs beside it | Python, uv, make run on your machine; PostGIS runs in Docker |
| You install | Docker + VS Code (or Cursor / a JetBrains IDE) | Docker + uv + make (+ git) |
| Identical on every OS? | **Yes**: same Linux image everywhere | Nearly: macOS and Linux natively, Windows through WSL2 |
| Best for | "No compatibility surprises", new collaborators | Speed, any editor, simplest debugging |

You can switch between them at any time: the git hooks and `.env` work in both.

> **Why not "just install the Linux steps on a Mac"?** macOS is Unix but not Linux: it has
> no `apt-get`, and Docker can't run natively there. Docker Desktop runs a small Linux VM.
> Windows needs WSL2 (a real Linux kernel) for the same reason.

---

## 1. Docker (both paths)

| OS | Install | Check |
|---|---|---|
| **macOS** (Apple Silicon or Intel) | [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/) (OrbStack or Colima also work) | `docker run --rm hello-world && docker compose version` |
| **Windows 10/11** | First WSL2: in PowerShell (admin) run `wsl --install`, reboot, finish the Ubuntu setup. Then [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) with the **WSL 2 backend**; in *Settings → Resources → WSL integration* enable your Ubuntu distro | in the **Ubuntu** terminal: `docker run --rm hello-world` |
| **Linux** (Ubuntu/Debian) | Docker Engine + Compose plugin, below | `docker run --rm hello-world && docker compose version` |

Linux (Ubuntu shown; for Debian replace `ubuntu` with `debian` in the URLs; other distros:
https://docs.docker.com/engine/install/):

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"   # then log out and back in
```

Both PostGIS (`imresamu/postgis`) and the Dev Container image are multi-arch, so they run
natively on Apple Silicon and on Intel/AMD.

---

## 2A. Dev Container path

*Pick **either** 2A **or** 2B. With 2A you skip 2B entirely: everything below runs inside the
container, and `make setup` runs there automatically.*

1. Install [VS Code](https://code.visualstudio.com/) and its **Dev Containers** extension
   (`ms-vscode-remote.remote-containers`). Cursor has it built in; JetBrains IDEs: *Remote
   Development → Dev Containers*.
2. Clone the repo. **Windows:** clone inside WSL (`\\wsl$\Ubuntu\home\<you>\…`, i.e. from the
   Ubuntu terminal), not under `C:\`: files under `C:\` are slow through Docker and pick up
   CRLF line endings.
   ```bash
   git clone https://github.com/pkpandey12/up-geospatial-project.git
   code up-geospatial-project
   ```
3. VS Code offers **Reopen in Container**; accept (or Command Palette → *Dev Containers:
   Reopen in Container*). The first build takes a few minutes; it then runs `make setup`.
4. In the editor's terminal (you're now inside Linux):
   ```bash
   make test
   make lint
   make db-up
   ```
   The editor starts and stops PostGIS for you, so `make db-down`, `db-reset` and `db-logs`
   are host-only (run them from a host terminal if needed).
5. Notebooks: open the `.ipynb` in VS Code and pick the kernel
   `/home/vscode/.venv-up-siting/bin/python`, or run `make lab` and open the forwarded port 8888.

---

## 2B. Host path

*Everything here runs directly in your machine's terminal, not in a container. Docker (step 1)
must work in that same terminal, because `make db-up` uses it to start PostGIS. `make setup`
only warns if Docker is missing, so tests, lint and notebooks work in the meantime.*

Install **git, make and uv** (Docker from step 1):

| OS | git + make | uv |
|---|---|---|
| **macOS** | `xcode-select --install` (Apple's command-line tools include both) | `curl -LsSf https://astral.sh/uv/install.sh \| sh` or `brew install uv` |
| **Windows** | in the **Ubuntu (WSL2)** terminal: `sudo apt-get update && sudo apt-get install -y git make` | in the Ubuntu terminal: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Linux** | `sudo apt-get install -y git make` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

On Windows, do **everything** in the Ubuntu terminal and keep the repo in the Linux home
folder (`~/…`), not under `/mnt/c/…`. Native PowerShell/cmd isn't supported: no `make`, and
bash recipes.

Open a new terminal, check `uv --version`, then:

```bash
git clone https://github.com/pkpandey12/up-geospatial-project.git
cd up-geospatial-project
make setup     # checks tools, creates .env, installs Python 3.12 + packages, enables git hooks
make test      # unit + notebook tests (your TODOs show as "x" = expected fail)
make lint      # ruff + profile validation
make db-up     # starts PostGIS, waits until healthy, runs the smoke test
```

uv downloads Python 3.12 itself; you don't need to install Python.

---

## 3. Troubleshooting

- **`port 5432 already in use` / `address already in use`**: something on your machine already
  listens on Postgres's port (Homebrew/Postgres.app/apt Postgres, or another container).
  - *Dev Container*: fixed since 2026-11-22: the container no longer publishes 5432 on your
    machine. Pull the latest branch, then *Dev Containers: Rebuild Container*. For a GUI tool on
    your host, use the port VS Code shows in its **Ports** tab for `db:5432`.
  - *Host path*: set `POSTGRES_PORT=5433` in `.env` (then `make db-up`), or stop the other one.
  - See who holds the port: macOS `lsof -nP -iTCP:5432 -sTCP:LISTEN`; Linux
    `sudo ss -ltnp 'sport = :5432'`; Docker `docker ps --filter publish=5432`.
- **`permission denied ... docker.sock`** on Linux: you skipped `usermod -aG docker` or didn't log out/in.
- **Scripts fail with `$'\r': command not found`** (Windows): the repo was cloned with CRLF endings.
  `.gitattributes` prevents this for new clones; re-clone inside WSL.
- **Commit says `uv: command not found`**: the git hook runs `uv`; install uv on the side you
  commit from (it's preinstalled in the Dev Container).

## 4. Your data files

Downloads live under `data/raw/<source_id>/ingest_date=YYYY-MM-DD/` (git-ignored). For EDA 01,
put the LGD PDF at:

```
data/raw/lgd/ingest_date=2026-11-21/Districts_of_Uttar_Pradesh_State.pdf
```

(A copy is also committed as a test fixture in `tests/fixtures/lgd/`.)
