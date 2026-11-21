"""Validate product profiles: `uv run validate-profiles config/product_profiles [--show-missing]`.

Exit code 0 when every file is valid, 1 otherwise, so it works in make, pre-commit and CI.
Null values are allowed (they mark data still waiting on the partners); pass --strict to
treat them as errors once the profile is meant to be complete.
"""

import argparse
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from up_siting.profiles.schema import ProductProfile

JSON_SCHEMA_FILE = "profile.schema.json"


def load_profile(path: Path) -> ProductProfile:
    """Parse one YAML file into a validated ProductProfile (raises ValidationError / ValueError)."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the top level")
    profile = ProductProfile.model_validate(data)
    if profile.product_id != path.stem:
        raise ValueError(
            f"{path}: product_id '{profile.product_id}' must match the file name '{path.stem}'"
        )
    return profile


def missing_fields(profile: ProductProfile) -> list[str]:
    """Dotted paths of every field that is null, e.g. 'raw_materials[0].quality_factor'."""

    def walk(value: Any, prefix: str) -> Iterator[str]:
        if value is None:
            yield prefix
        elif isinstance(value, dict):
            for key, sub in value.items():
                yield from walk(sub, f"{prefix}.{key}" if prefix else key)
        elif isinstance(value, list):
            for i, sub in enumerate(value):
                yield from walk(sub, f"{prefix}[{i}]")

    optional_text = {"notes", "description"}  # free text: null is fine, not "missing"
    return [p for p in walk(profile.model_dump(), "") if p.rsplit(".", 1)[-1] not in optional_text]


def json_schema() -> str:
    """The JSON Schema for editors (VS Code YAML extension); kept in sync by a test."""
    return json.dumps(ProductProfile.model_json_schema(), indent=2) + "\n"


def _profile_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        files.extend(sorted(p.glob("*.y*ml")) if p.is_dir() else [p])
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", type=Path, help="YAML files or folders")
    parser.add_argument("--show-missing", action="store_true", help="list null fields")
    parser.add_argument("--strict", action="store_true", help="fail if any field is null")
    parser.add_argument(
        "--write-schema", action="store_true", help=f"(re)write {JSON_SCHEMA_FILE} in each folder"
    )
    args = parser.parse_args(argv)

    if args.write_schema:
        for folder in {p if p.is_dir() else p.parent for p in args.paths}:
            (folder / JSON_SCHEMA_FILE).write_text(json_schema(), encoding="utf-8")
            print(f"wrote {folder / JSON_SCHEMA_FILE}")

    files = _profile_files(args.paths)
    if not files:
        print("no profile files found", file=sys.stderr)
        return 1

    failed = False
    for path in files:
        try:
            profile = load_profile(path)
        except ValidationError as exc:
            failed = True
            print(f"FAIL {path}")
            for err in exc.errors():
                loc = ".".join(str(part) for part in err["loc"])
                print(f"  {loc}: {err['msg']}")
            continue
        except (ValueError, yaml.YAMLError) as exc:
            failed = True
            print(f"FAIL {exc}")
            continue

        missing = missing_fields(profile)
        if args.strict and missing:
            failed = True
        status = "FAIL" if args.strict and missing else "ok  "
        print(f"{status} {path} ({len(missing)} fields waiting on partners)")
        if args.show_missing or args.strict:
            for field in missing:
                print(f"  - {field}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
