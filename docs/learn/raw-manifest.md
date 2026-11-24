# The raw layer's manifest (`make register`)

**What it is.** A file per source, `data/raw/<source>/_manifest.jsonl`, with one JSON line per
raw file: path, sha256, size, source URL, when and by whom it was fetched, and the licence.
JSON Lines = one JSON object per line, so appending never rewrites the file and any tool can
stream it.

**Why here.** In Phase 1 Sage downloads government files by hand; in Phase 2 Airflow
extractors fetch them. Both write the *same* record, so "where did this file come from, and
may we use it?" always has an answer, and the Phase 2 loaders can trust (and verify) what's
in `raw/`.

Code: `src/up_siting/extract/manifest.py` (worked example). Tests: `tests/test_manifest.py`.

## Concepts that matter

1. **Raw is immutable.** A file in `data/raw/<source>/ingest_date=YYYY-MM-DD/` is never
   edited. A new version is a new download under a new `ingest_date`.
2. **Content hash (sha256)** proves (1): re-registering a changed file fails loudly.
3. **Idempotency.** Registering the same file twice is a no-op, so a retried Airflow task
   or a repeated `make register` can't create duplicate lines.
4. **Hive-style partitions** (`ingest_date=...`): DuckDB, Spark and Snowflake read the date
   from the folder name without opening files.
5. **Licence gate.** `register` copies the licence from `docs/data-sources.md` and refuses a
   source that isn't listed there. Provenance and licence are captured at the moment of
   ingest, not reconstructed later.
6. **Manual vs extractor** (`fetched_by`): same pattern, different actor. Phase 2 extractors
   call `register_file(..., fetched_by="extractor")`.
7. **Append-only log, not a database.** It's tiny, diff-able and needs no service. When it
   outgrows that, it loads into `raw._manifest` as-is.

## Commands you'll run

```bash
make register SRC=cgwb_gw FILE=~/Downloads/UP_GWRA_2024.pdf URL=https://cgwb.gov.in/... \
     NOTES="block annexure on pp. 120-160"
uv run register-raw --help
```

```sql
-- every raw file, every source, in DuckDB:
select source, file, bytes, fetched_at, licence
from read_json('data/raw/*/_manifest.jsonl') order by fetched_at;
```

A file outside `data/raw/` (e.g. in Downloads) is **copied** into today's
`ingest_date=` folder first (IST date); the original stays where it was.

## Common mistakes

- Editing a raw CSV "just to fix a header". Fix it in the notebook or the staging model.
- Registering before adding the source's row to `docs/data-sources.md` (it will refuse).
- Downloading a new version under the same name on the same day: it refuses to overwrite.
  Rename the file (`..._v2`) or wait for the next ingest date.

## Interview questions

- *How do you make a data lake auditable?* (Immutable raw zone, content hashes, a manifest
  with source/time/actor/licence, idempotent ingestion, partitions by ingest date.)
- *Why sha256 instead of file size or modified time?* (Size and mtime change for reasons
  unrelated to content and can collide; a cryptographic hash identifies the content.)
