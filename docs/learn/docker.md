# Docker and Docker Compose

**What it is.** Docker runs software in *containers*: isolated processes that start from an
*image* (a read-only filesystem plus metadata), sharing the host's Linux kernel. Compose
describes a set of containers, their config, ports and volumes in one YAML file.

**Why here.** PostGIS (Postgres + GEOS + PROJ + GDAL) is painful to install natively and must
match the managed version later. `docker compose up` gives everyone the same database in
seconds. Airflow joins the same Compose file in Phase 2.

## Concepts that matter

1. **Image vs container.** Image = template (`imresamu/postgis:17-3.6`). Container = a running
   instance. Many containers can run from one image.
2. **Tags and pinning.** `17-3.6` means Postgres 17, PostGIS 3.6. Never use `latest` for a
   database: an upgrade can change the on-disk format under your data.
   **Architecture** is part of the image too: the official `postgis/postgis` is amd64-only,
   so we use the multi-arch `imresamu/postgis` (amd64 + arm64), and Apple Silicon runs it natively.
   Check any image with `docker manifest inspect <image>`.
3. **Volumes** keep data outside the container's throwaway filesystem. `pgdata` survives
   `docker compose down`; `down -v` deletes it (`make db-reset`).
4. **Bind mounts** map a host file into the container: we mount `db/init/20_project.sql` and
   `db/smoke_test.sql`.
5. **Ports.** `127.0.0.1:5432:5432` = host loopback port → container port. Binding to
   127.0.0.1 keeps the DB off your LAN.
6. **Environment variables** configure the image (`POSTGRES_USER`, …). Compose reads `.env`
   automatically; `${VAR:-default}` falls back to a default (ours match `.env.example`), while
   `${VAR:?msg}` would fail fast instead.
7. **Init scripts** in `/docker-entrypoint-initdb.d/` run **only on first start with an empty
   volume**. Changing them later does nothing until you reset the volume.
8. **Healthchecks.** `pg_isready` tells Compose when the DB really accepts connections;
   `docker compose up --wait` blocks until then. We check over TCP (`-h 127.0.0.1`) because
   during first-time init Postgres listens only on a Unix socket, and a socket check would say
   "ready" before the init scripts have finished.

## Commands you'll run

```bash
make db-up / make db-down / make db-psql / make db-logs
docker compose ps                    # what's running, health status
docker compose logs -f db            # follow logs
docker compose exec db psql -U up_siting -d up_siting
docker volume ls                     # see up-siting_pgdata
docker system df                     # disk used by images/volumes
```

## Common mistakes

- Editing an init script and expecting it to re-run. It won't: `make db-reset` (deletes data).
- Port 5432 already taken by a local Postgres → change `POSTGRES_PORT` in `.env`.
- Running `docker` with `sudo` every time. Add yourself to the `docker` group (docs/SETUP.md).
  Note that group membership is effectively root on that machine.
- Assuming a container is "the same everywhere" without checking its architecture: an
  amd64-only image on an M-series Mac runs under emulation, slower and occasionally flaky.
- Mounting the whole `db/init/` folder over `/docker-entrypoint-initdb.d/` would hide the
  image's own `10_postgis.sh`. We mount single files.

## Interview questions

- *What's the difference between a container and a VM?* (Containers share the host kernel and
  isolate with namespaces/cgroups; VMs virtualise hardware and run their own kernel.)
- *Your Postgres container restarted and the data is gone. What went wrong?* (No volume, or it
  was started with a different project name, or someone ran `down -v`.)
