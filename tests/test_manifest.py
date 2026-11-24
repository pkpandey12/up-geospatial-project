"""Register CLI / manifest pattern (worked example): src/up_siting/extract/manifest.py."""

import json
from pathlib import Path

import pytest

from up_siting.extract.manifest import (
    licence_from_docs,
    main,
    read_manifest,
    register_file,
    sha256_of,
)

DOCS = """\
# Data sources

| source_id | Name | Licence (and where stated) | Status |
|---|---|---|---|
| `demo_src` | Demo | CC BY 4.0 (footer of the page) | planned |
| `other_src` | Other | Unknown | planned |
"""


@pytest.fixture
def repo(tmp_path: Path) -> dict[str, Path]:
    """A throwaway repo: docs/data-sources.md, data/raw/, and a 'Downloads' folder."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "data-sources.md").write_text(DOCS, encoding="utf-8")
    (tmp_path / "data" / "raw").mkdir(parents=True)
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    (downloads / "table.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    return {
        "root": tmp_path,
        "raw": tmp_path / "data" / "raw",
        "docs": tmp_path / "docs" / "data-sources.md",
        "download": downloads / "table.csv",
    }


def _register(repo: dict[str, Path], file: Path, **kwargs):  # type: ignore[no-untyped-def]
    return register_file(
        "demo_src",
        file,
        "https://example.org/table.csv",
        raw_dir=repo["raw"],
        data_sources_md=repo["docs"],
        repo_root=repo["root"],
        **kwargs,
    )


def test_licence_is_read_from_data_sources_md(repo: dict[str, Path]) -> None:
    assert licence_from_docs("demo_src", repo["docs"]) == "CC BY 4.0 (footer of the page)"
    with pytest.raises(KeyError, match="no row"):
        licence_from_docs("missing_src", repo["docs"])


def test_file_outside_raw_is_copied_in_and_registered(repo: dict[str, Path]) -> None:
    rec = _register(repo, repo["download"])
    copied = repo["root"] / rec.file
    assert copied.is_file() and repo["download"].is_file()  # original left in place
    assert copied.parent.name == f"ingest_date={rec.ingest_date}"
    assert rec.file.startswith("data/raw/demo_src/ingest_date=")
    assert rec.sha256 == sha256_of(repo["download"])
    assert rec.bytes == repo["download"].stat().st_size
    assert rec.licence == "CC BY 4.0 (footer of the page)"
    assert rec.fetched_by == "manual"
    lines = (repo["raw"] / "demo_src" / "_manifest.jsonl").read_text(encoding="utf-8")
    assert json.loads(lines.splitlines()[0])["sha256"] == rec.sha256


def test_file_already_in_ingest_folder_keeps_its_date(repo: dict[str, Path]) -> None:
    folder = repo["raw"] / "demo_src" / "ingest_date=2026-11-01"
    folder.mkdir(parents=True)
    f = folder / "x.csv"
    f.write_text("x\n1\n", encoding="utf-8")
    rec = _register(repo, f, fetched_by="extractor")
    assert rec.ingest_date == "2026-11-01"
    assert rec.file == "data/raw/demo_src/ingest_date=2026-11-01/x.csv"


def test_registering_twice_is_a_no_op(repo: dict[str, Path]) -> None:
    first = _register(repo, repo["download"])
    again = _register(repo, repo["root"] / first.file)
    assert again == first
    assert len(read_manifest("demo_src", repo["raw"])) == 1


def test_changed_raw_file_is_refused(repo: dict[str, Path]) -> None:
    rec = _register(repo, repo["download"])
    (repo["root"] / rec.file).write_text("a,b\n9,9\n", encoding="utf-8")
    with pytest.raises(ValueError, match="different sha256"):
        _register(repo, repo["root"] / rec.file)


def test_same_name_downloaded_again_same_day_is_refused(repo: dict[str, Path]) -> None:
    _register(repo, repo["download"])
    with pytest.raises(FileExistsError):
        _register(repo, repo["download"])


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [({"fetched_by": "robot"}, ValueError), ({"licence": None}, None)],
)
def test_bad_inputs(repo: dict[str, Path], kwargs: dict, error: type | None) -> None:
    if error:
        with pytest.raises(error):
            _register(repo, repo["download"], **kwargs)
    else:
        assert _register(repo, repo["download"], **kwargs).licence.startswith("CC BY")


def test_source_must_be_documented_first(repo: dict[str, Path]) -> None:
    with pytest.raises(KeyError):
        register_file(
            "undocumented",
            repo["download"],
            "https://example.org",
            raw_dir=repo["raw"],
            data_sources_md=repo["docs"],
            repo_root=repo["root"],
        )


def test_cli_reports_errors_with_exit_code_1(repo: dict[str, Path]) -> None:
    # The real CLI uses the real repo paths; a missing file fails before touching them.
    code = main(["--source", "demo_src", "--file", str(repo["root"] / "nope.csv"), "--url", "x"])
    assert code == 1
