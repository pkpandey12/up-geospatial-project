# data/ (git-ignored except this file)

```
data/raw/<source_id>/ingest_date=YYYY-MM-DD/<original file>   # downloads, never edited
data/interim/<topic>/*.parquet                                # EDA outputs, safe to delete
```

See `docs/data-sources.md` for what goes where and `docs/SETUP.md` §5 for the LGD file.
