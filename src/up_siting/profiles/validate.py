"""Validate product profiles: `uv run validate-profiles config/product_profiles [--show-missing]`.

Exit code 0 when every file is valid, 1 otherwise, so it works in make, pre-commit and CI.
Null values are allowed (they mark data still missing); pass --strict to treat them as
errors once the profile is meant to be complete. Pass --private to validate each profile
WITH its private overlay (config/product_profiles/private/<id>.yaml) applied: local only,
never in CI.
"""

import argparse
import json
import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from up_siting.profiles.overlay import apply_overlay, read_overlay
from up_siting.profiles.schema import ProductProfile, value_paths

JSON_SCHEMA_FILE = "profile.schema.json"
PRIVATE_SUBDIR = "private"


def load_profile(path: Path, private_dir: Path | None = None) -> ProductProfile:
    """Parse one YAML file into a validated ProductProfile (raises ValidationError / ValueError).

    private_dir: if given and it holds <product_id>.yaml, that overlay is applied first
    (partner values, tagged `source: partner`). Tests and CI never pass it.
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the top level")
    if private_dir is not None:
        overlay = read_overlay(private_dir, path.stem)
        if overlay is not None:
            data = apply_overlay(data, overlay)
    profile = ProductProfile.model_validate(data)
    if profile.product_id != path.stem:
        raise ValueError(
            f"{path}: product_id '{profile.product_id}' must match the file name '{path.stem}'"
        )
    return profile


def missing_fields(profile: ProductProfile) -> list[str]:
    """Paths of every value that is null, e.g. 'raw_materials.maize.price_inr_per_tonne'.

    Free text (notes, descriptions) is never "missing". Raw materials are addressed by id.
    """
    return [p for p, v in value_paths(profile.model_dump(mode="json")).items() if v is None]


def provenance_summary(profile: ProductProfile) -> dict[str, int]:
    """How many values come from each confidence level, plus how many are the partner's."""
    counts: dict[str, int] = {"strong": 0, "moderate": 0, "weak": 0, "partner": 0}
    for prov in profile.provenance.values():
        counts[prov.confidence.value] += 1
        counts["partner"] += prov.source == "partner"
    return counts


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
        "--private", action="store_true", help=f"apply overlays from <folder>/{PRIVATE_SUBDIR}/"
    )
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
        private_dir = path.parent / PRIVATE_SUBDIR if args.private else None
        try:
            profile = load_profile(path, private_dir)
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
        prov = provenance_summary(profile)
        overlay = (
            " + private overlay" if private_dir and (private_dir / path.name).is_file() else ""
        )
        print(
            f"{status} {path}{overlay} ({len(missing)} null; sourced: {prov['strong']} strong, "
            f"{prov['moderate']} moderate, {prov['weak']} weak; {prov['partner']} from partner)"
        )
        if args.show_missing or args.strict:
            for field in missing:
                print(f"  - {field}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
