"""Run EDA notebooks end to end against fixtures, writing to a temp folder.

Notebook 01 must (a) run without a failing assert cell and (b) regenerate exactly the
seeds committed in dbt/seeds/, so the committed files can't drift from the code.
Notebook 02 is Sage's TODO and is not executed here; it runs on your real downloads.
"""

from pathlib import Path

import nbformat
import pandas as pd
import pytest
from nbclient import NotebookClient

from up_siting.common.paths import REPO_ROOT, SEEDS_DIR

pytestmark = pytest.mark.notebook
NB_DIR = REPO_ROOT / "notebooks" / "eda"


def run_notebook(path: Path, env: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in env.items():
        monkeypatch.setenv(key, value)  # the kernel process inherits our environment
    nb = nbformat.read(path, as_version=4)
    NotebookClient(
        nb, timeout=180, kernel_name="python3", resources={"metadata": {"path": path.parent}}
    ).execute()


def test_01_spine_regenerates_committed_seeds(
    lgd_pdf: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_notebook(
        NB_DIR / "01_spine.ipynb",
        {
            "UP_SITING_LGD_PDF": str(lgd_pdf),
            "UP_SITING_OUT_DIR": str(tmp_path / "interim"),
            "UP_SITING_SEED_OUT_DIR": str(tmp_path / "seeds"),
        },
        monkeypatch,
    )
    assert (tmp_path / "interim" / "up_district_spine.parquet").is_file()

    for name, ignore in [
        ("district_name_map.csv", []),
        ("lgd_district_spine.csv", ["_ingest_date"]),
    ]:
        fresh = pd.read_csv(tmp_path / "seeds" / name, dtype=str).drop(columns=ignore)
        committed = pd.read_csv(SEEDS_DIR / name, dtype=str).drop(columns=ignore)
        pd.testing.assert_frame_equal(fresh, committed, obj=name)


def test_every_eda_notebook_is_valid_json() -> None:
    for path in sorted(NB_DIR.glob("*.ipynb")):
        nbformat.validate(nbformat.read(path, as_version=4))
