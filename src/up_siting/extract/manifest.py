"""Register raw files in a per-source manifest: data/raw/<source>/_manifest.jsonl.

WORKED EXAMPLE: the manifest pattern. Every file that lands in data/raw/ gets one JSON line
saying what it is, where it came from, when, who fetched it and under which licence:

    {"file": "data/raw/cgwb_gw/ingest_date=2026-12-02/UP_2024.pdf", "source": "cgwb_gw",
     "ingest_date": "2026-12-02", "sha256": "9f2c...", "bytes": 4183022,
     "source_url": "https://...", "fetched_at": "2026-12-02T10:14:03+05:30",
     "fetched_by": "manual", "licence": "Unknown (not stated on the page)", "notes": null}

Why bother (and why it's worth explaining in an interview):
* Provenance. Six weeks from now "where did this PDF come from?" has an answer.
* Integrity. The sha256 proves a raw file hasn't been edited; raw files are immutable.
* Idempotency. Registering the same file twice is a no-op; a *different* file under the
  same name is an error, because it would silently change history.
* One format for people and machines. Sage registers manual downloads with
  `make register`; Phase 2 extractors call `register_file(..., fetched_by="extractor")`.
  DuckDB reads the result directly: `select * from read_json('data/raw/*/_manifest.jsonl')`.
* Licence gate. A source must have a row in docs/data-sources.md before a file can be
  registered, and its licence is copied from there, so nothing enters raw/ unlicensed
  without someone saying so.

Usage (see also `make register`):
    uv run register-raw --source apy_des --file ~/Downloads/apy.xlsx \\
        --url https://data.desagri.gov.in/website/crops-apy-report-web

A file outside data/raw/<source>/ingest_date=YYYY-MM-DD/ is COPIED into today's folder
(IST date) first; the original is left where it was.

Learn: docs/learn/raw-manifest.md
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from up_siting.common.paths import DOCS_DIR, RAW_DIR, REPO_ROOT

IST = ZoneInfo("Asia/Kolkata")
MANIFEST_NAME = "_manifest.jsonl"
FETCHED_BY = ("manual", "extractor")
_SOURCE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
_INGEST_DIR = re.compile(r"^ingest_date=(\d{4}-\d{2}-\d{2})$")


@dataclass(frozen=True)
class ManifestRecord:
    file: str  # path relative to the repo root, forward slashes (same on every OS)
    source: str
    ingest_date: str  # YYYY-MM-DD, from the folder name
    sha256: str
    bytes: int
    source_url: str
    fetched_at: str  # ISO 8601 with offset
    fetched_by: str  # "manual" | "extractor"
    licence: str
    notes: str | None = None


def sha256_of(path: Path, chunk_size: int = 1 << 20) -> str:
    """Hash in chunks, so a 60 MB CSV never has to fit in memory at once."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def licence_from_docs(source: str, data_sources_md: Path) -> str:
    """The Licence cell of `source`'s row in docs/data-sources.md.

    Raises KeyError if the source has no row: add the row (with its licence) first.
    """
    header: list[str] | None = None
    for line in data_sources_md.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            header = None  # a new table starts after any non-table line
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if cells and cells[0] == f"`{source}`":
            col = next((i for i, h in enumerate(header) if h.startswith("licence")), None)
            if col is None or col >= len(cells):
                raise KeyError(f"no Licence column in the table that lists `{source}`")
            return cells[col].replace("**", "").strip()  # drop markdown bold
    raise KeyError(
        f"source `{source}` has no row in {data_sources_md}; add it (with its licence) first"
    )


def _place_in_raw(file: Path, source: str, raw_dir: Path, today: str) -> tuple[Path, str]:
    """Return (path inside raw/, ingest_date), copying the file in if it isn't there yet."""
    source_dir = (raw_dir / source).resolve()
    parent = file.resolve().parent
    match = _INGEST_DIR.match(parent.name)
    if match and parent.parent == source_dir:
        return file.resolve(), match.group(1)
    target_dir = source_dir / f"ingest_date={today}"
    target = target_dir / file.name
    if target.exists():
        raise FileExistsError(
            f"{target} already exists; raw files are never overwritten. "
            "Register that file instead, or rename the new one."
        )
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, target)  # copy2 keeps the modification time
    print(f"copied {file} -> {target}")
    return target, today


def read_manifest(source: str, raw_dir: Path = RAW_DIR) -> list[ManifestRecord]:
    path = raw_dir / source / MANIFEST_NAME
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [ManifestRecord(**json.loads(line)) for line in lines if line.strip()]


def register_file(
    source: str,
    file: Path,
    url: str,
    *,
    fetched_by: str = "manual",
    licence: str | None = None,
    notes: str | None = None,
    fetched_at: datetime | None = None,
    raw_dir: Path = RAW_DIR,
    data_sources_md: Path = DOCS_DIR / "data-sources.md",
    repo_root: Path = REPO_ROOT,
) -> ManifestRecord:
    """Append one record for `file` to data/raw/<source>/_manifest.jsonl and return it.

    Idempotent: the same file with the same hash returns the existing record.
    Raises ValueError for a bad source id / fetched_by / a changed file, KeyError if the
    source isn't in docs/data-sources.md, FileNotFoundError if the file is missing.
    """
    if not _SOURCE_ID.match(source):
        raise ValueError(f"source must be snake_case (a-z, 0-9, _), got {source!r}")
    if fetched_by not in FETCHED_BY:
        raise ValueError(f"fetched_by must be one of {FETCHED_BY}, got {fetched_by!r}")
    if not file.is_file():
        raise FileNotFoundError(file)
    licence = licence or licence_from_docs(source, data_sources_md)

    now = datetime.now(IST)
    raw_path, ingest_date = _place_in_raw(file, source, raw_dir, now.date().isoformat())
    rel = raw_path.relative_to(repo_root.resolve()).as_posix()
    digest = sha256_of(raw_path)

    for existing in read_manifest(source, raw_dir):
        if existing.file == rel:
            if existing.sha256 == digest:
                print(f"already registered: {rel}")
                return existing
            raise ValueError(
                f"{rel} is registered with a different sha256: a raw file was changed. "
                "Raw files are immutable; save the new version under a new ingest_date."
            )

    record = ManifestRecord(
        file=rel,
        source=source,
        ingest_date=ingest_date,
        sha256=digest,
        bytes=raw_path.stat().st_size,
        source_url=url,
        fetched_at=(fetched_at or now).isoformat(timespec="seconds"),
        fetched_by=fetched_by,
        licence=licence,
        notes=notes,
    )
    manifest = raw_dir / source / MANIFEST_NAME
    with manifest.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    print(f"registered {rel} ({record.bytes:,} bytes, sha256 {digest[:12]}...)")
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Register a raw file in its source manifest.")
    parser.add_argument("--source", required=True, help="source_id, e.g. cgwb_gw")
    parser.add_argument("--file", required=True, type=Path, help="the downloaded file")
    parser.add_argument("--url", required=True, help="page or file URL it came from")
    parser.add_argument("--fetched-by", default="manual", choices=FETCHED_BY)
    parser.add_argument("--licence", help="override the licence in docs/data-sources.md")
    parser.add_argument("--notes", help="anything odd: filters chosen, captcha, partial years")
    args = parser.parse_args(argv)
    try:
        register_file(
            args.source,
            args.file.expanduser(),
            args.url,
            fetched_by=args.fetched_by,
            licence=args.licence,
            notes=args.notes,
        )
    except (KeyError, ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
