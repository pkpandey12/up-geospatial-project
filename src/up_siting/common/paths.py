"""Well-known folders, so notebooks and scripts never hard-code absolute paths.

The package is installed in editable mode by `uv sync`, so this file lives at
<repo>/src/up_siting/common/paths.py and the repo root is three folders up.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"  # downloaded originals: data/raw/<source>/ingest_date=YYYY-MM-DD/
INTERIM_DIR = DATA_DIR / "interim"  # EDA outputs (Parquet), safe to delete and rebuild

CONFIG_DIR = REPO_ROOT / "config"
PRODUCT_PROFILES_DIR = CONFIG_DIR / "product_profiles"

SEEDS_DIR = REPO_ROOT / "dbt" / "seeds"  # small, committed reference tables (CSV)
DOCS_DIR = REPO_ROOT / "docs"
