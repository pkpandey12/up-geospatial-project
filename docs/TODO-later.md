# Deferred work (not now)

Items decided but parked for a later phase. Don't start them early; move an item into the
session scope only when its phase begins.

## Phase 2 (January 2027)

| Item | Why | Notes |
|---|---|---|
| Pin `imresamu/postgis` to an exact tag or digest | Reproducible builds; a moving `17-3.6` tag can change under us | `docker-compose.yml` and `.devcontainer/`; record the digest in `docs/learn/docker.md` |
| CI: Linux on every push; macOS, Windows and Dev Container jobs only on PRs to `main` and weekly (`schedule`) | Cut CI minutes and wait time; the cross-platform risk is low once setup is stable | `.github/workflows/ci.yml`; `on: push` + `pull_request: branches: [main]` + `schedule` |
| LGD from the data.gov.in API (`lgd_ogd`) replaces the manual PDF | Monthly updates without a manual download | Free API key → environment secret, never in `.env.example` values |
| Move the notebook fetchers (EDA 10, 11) into `src/up_siting/extract/` as the HTTP extractor worked example | Phase 2's first extractor pattern | Same manifest (`register_file(..., fetched_by="extractor")`) |
| Strip control characters in loaders (DQ-001) | Postgres rejects NUL bytes | All text columns |

## Geography stage (after the MVP)

District boundaries (geopandas), OpenStreetMap, road density, market-access distances,
substation filter (CEA lists), block-level drill-down.
