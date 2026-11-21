# Data sources

One row per source. A source must be listed here **before** a notebook uses it (notebook 02
checks). `source_id` is the folder name under `data/raw/` and the prefix of its dbt models later.

Licence column: the licence's name **and** where you read it. "Unknown" is a valid
answer while exploring, but a source can't be *kept* (EDA step 6) until it's resolved,
because the repo may go public and the tool may be used commercially.

| source_id | Name | Publisher | URL | Format | Geography / key | Period | Licence (and where stated) | Status |
|---|---|---|---|---|---|---|---|---|
| `lgd` | Local Government Directory: Districts of Uttar Pradesh | Ministry of Panchayati Raj, GoI | https://lgdirectory.gov.in/ (Download Directory → Districts of a State) | PDF (also offered as other formats) | District; **LGD district code** (the project's key) | Snapshot, downloaded 2026-11-21 | **Unknown, to check.** Look for terms on lgdirectory.gov.in; Government of India open data on data.gov.in is usually under GODL-India. A copy is committed as a test fixture, so this matters before the repo goes public. | In use (EDA 01) |

## How to download a source (Phase 1 convention)

1. Save the original file, unchanged, to `data/raw/<source_id>/ingest_date=<YYYY-MM-DD>/`
   using the date you downloaded it. Never edit a file in `raw/`.
2. Add a row above. Note the exact page/menu path you used in the URL column.
3. Note anything odd (captchas, partial years, units) in the Status column or the data-quality log.

The `ingest_date=` folder name is "Hive-style" partitioning: DuckDB, Spark and Snowflake can
filter on it without opening files. Phase 2 will formalise this with a manifest
(see *Decisions needed* in the session report).

## Download notes

- **LGD**: the site wasn't reachable from the cloud dev container (network policy) and the
  download form may show a captcha, so Sage downloads by hand. The PDF export works with
  `src/up_siting/extract/lgd.py`. If you ever export CSV/XLS instead, prefer it, but keep
  the PDF parser for the test.
