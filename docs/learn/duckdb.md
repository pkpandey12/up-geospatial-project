# DuckDB

**What it is.** An in-process analytical (OLAP) SQL database: a library, like SQLite, but
columnar and vectorised for aggregations. It reads CSV, Parquet, JSON and Excel files
directly and queries pandas DataFrames in place.

**Why here.** EDA over downloaded files without loading them anywhere: `select … from
read_parquet('data/interim/…')`. SQL you write here is close to what becomes dbt models later.

## Concepts that matter

1. **In-process.** No server. `duckdb.sql(...)` uses a default in-memory database;
   `duckdb.connect("file.duckdb")` persists.
2. **Replacement scans.** A pandas DataFrame named `raw` in Python scope can be queried as a
   table: `duckdb.sql("select count(*) from raw")`. (Used throughout notebook 01.)
3. **File functions.** `read_csv(path, all_varchar=true, header=true)`, `read_parquet('dir/*/*.parquet',
   hive_partitioning=true)`. Globs + Hive partitions (`ingest_date=…`) become columns.
4. **Relations are lazy.** `duckdb.sql(q)` returns a relation; `.df()`, `.fetchall()` or
   `.show()` executes it. **DuckDB 2.0:** relations no longer have `fetchone()`, because each
   call re-runs the query. Use `.fetchall()` (as notebook 01 does) or `duckdb.execute(q).fetchone()`.
5. **Friendly SQL.** `select * exclude (col)`, `columns(*)`, `group by all`, `UNPIVOT`
   (notebook 01 profiles every column in one query), `list()`, `count(*) filter (where …)`.
6. **Read as text first.** `all_varchar=true`, then cast deliberately: sniffers drop leading
   zeros (`'06'`) and guess dates wrong.
7. **Parquet** is the interchange format: columnar, typed, compressed. Raw lands as Parquet in
   Phase 2 (portability rule 3).

## Commands you'll run

```python
import duckdb

duckdb.sql(
    "select * from read_csv('data/raw/x/ingest_date=2026-11-25/f.csv', all_varchar=true) limit 5"
).df()
duckdb.sql("describe select * from read_parquet('data/interim/lgd/up_district_spine.parquet')")
duckdb.sql("copy (select * from df) to 'out.parquet' (format parquet)")
```

## Common mistakes

- Building SQL with f-strings from untrusted input. Fine for your own paths in EDA; use
  parameters (`duckdb.execute(q, [value])`) elsewhere.
- Forgetting it's case-insensitive for identifiers but case-sensitive for string values.
- Treating DuckDB as the app database. It's single-writer and embedded; PostGIS serves the app.

## Interview questions

- *Row store vs column store: why is DuckDB fast for `group by` over 10 columns of a 100-column table?*
  (It reads only those columns, in compressed vectors, with SIMD-friendly execution.)
- *When would you use DuckDB instead of Spark?* (Data fits on one machine, which is most data:
  no cluster, no JVM, and the same SQL.)
