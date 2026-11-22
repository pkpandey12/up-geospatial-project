# Dev Containers

**What it is.** An open spec ([containers.dev](https://containers.dev)) for describing a
*development environment* as a container: `.devcontainer/devcontainer.json` says which image or
compose services to start, which user to run as, what to run after creation, and which editor
extensions and settings to use. VS Code, Cursor, JetBrains IDEs, GitHub Codespaces and the
`devcontainer` CLI all read it.

**Why here.** You want Windows, macOS and Linux to behave identically. Docker already made the
*database* identical; the Dev Container does the same for the *toolchain* (Python 3.12, uv,
make, psql), so "works on my machine" means "works in this image".

## How this repo's container is put together

```
docker-compose.yml           db   (PostGIS; also used on the host path)
.devcontainer/compose.yaml   dev  (layered on top: image, bind mount, env, depends_on db healthy)
.devcontainer/Dockerfile     Python 3.12 (Debian 13) + psql 17 + uv, multi-arch
.devcontainer/devcontainer.json   which compose files, service, user, postCreateCommand, extensions
```

## Concepts that matter

1. **Image vs Dev Container.** The Dockerfile builds an image; `devcontainer.json` adds how the
   *editor* uses it: workspace folder, `remoteUser: vscode`, lifecycle commands, ports.
2. **Compose-based.** `dockerComposeFile` lists both compose files; `service: dev` is where the
   editor attaches; `runServices` also starts `db`. In the container, the database is host
   `db`, port 5432 (service DNS on the compose network), not `localhost`.
3. **Relative paths in multi-file compose** resolve from the *first* file's folder (repo root),
   which is why `.devcontainer/compose.yaml` bind-mounts `.` (the repo root).
4. **Bind mount + separate venv.** The repo is bind-mounted at `/workspaces/up-geospatial-project`;
   the virtualenv lives at `/home/vscode/.venv-up-siting` (`UV_PROJECT_ENVIRONMENT`). A `.venv`
   built on macOS or Windows holds binaries Linux can't run, so the two must never share a folder.
5. **Lifecycle commands.** `initializeCommand` runs on the *host* first: ours builds the image
   with a plain `docker build`. (Letting compose build it broke on GitHub's runner: newer
   compose builds through "bake", which blocks the temporary Dockerfile the Dev Container tooling
   writes to `/tmp`.) `postCreateCommand: make setup` runs once per new container.
   (There are also `onCreate`, `postStart`, `postAttach`.)
6. **No host port for the database.** `.devcontainer/compose.yaml` removes `db`'s published
   port (`ports: !reset []`): the dev container reaches it as `db:5432` on the compose network,
   so a Postgres already on your machine can't block startup. `forwardPorts: ["db:5432"]` lets
   VS Code expose it on a free local port for GUI tools.
7. **Mode switch.** The image sets `UP_SITING_DEVCONTAINER=1`; the Makefile uses it to talk to
   `db` over the network and to refuse host-only targets (`db-down`, …).
8. **UID mapping.** On Linux the CLI remaps the container user's UID to yours, so files you
   create in the container aren't owned by someone else on the host.
9. **Git hooks across both worlds.** `pre-commit install` writes a hook with one absolute Python
   path, which breaks commits made from the other side. We use `git config core.hooksPath
   .githooks` with a script that runs `uv run pre-commit run`, which works on both.
10. **Multi-arch images** (amd64 + arm64) avoid emulation on Apple Silicon. Check with
   `docker manifest inspect <image>`.

## Commands you'll run

```bash
# Editor: "Dev Containers: Reopen in Container" / "Rebuild Container" (after Dockerfile changes)
npm install -g @devcontainers/cli        # optional, the CLI CI uses
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . make test
```

## Common mistakes

- Editing the Dockerfile and not choosing *Rebuild Container*.
- Cloning to `C:\` on Windows: slow file access and CRLF line endings. Clone inside WSL.
- Using `localhost` for the database from inside the container (it's `db`).
- Publishing a fixed host port for a service only containers need: it collides with whatever
  the developer already runs (this repo's first Dev Container did, with a local Postgres).
- Putting secrets in `devcontainer.json`: it's committed. Use `.env` (git-ignored).

## Interview questions

- *How do you guarantee a reproducible dev environment across a team on different OSes?*
  (Lockfile for packages; pinned, multi-arch container image for the toolchain; services
  in compose; CI that builds the same container and runs the same commands.)
- *Dev Container vs just a Dockerfile for the app?* (The app image is for running in
  production: minimal, no dev tools. The dev container is for building: tools, editor
  integration, bind-mounted source. Different goals, often different images.)
