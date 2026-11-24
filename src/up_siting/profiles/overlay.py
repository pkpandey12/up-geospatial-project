"""Private overlay: the partner's real figures on top of the public profile, field by field.

WORKED EXAMPLE: the config-overlay pattern. The public profile (committed) holds values from
public sources, each with a citation. The partner's real plant figures are confidential, so
they live in a git-ignored file with the same shape:

    config/product_profiles/cbg.yaml            public, committed, CI uses this
    config/product_profiles/private/cbg.yaml    partner values, NEVER committed

`apply_overlay(public, private)` returns a merged dict in which:
* nested mappings merge key by key (an overlay sets `land.acres_per_tpd` without restating
  `land.fixed_acres`);
* `raw_materials` merge **by id**: an overlay entry with an existing id updates that
  material's fields; a new id is appended (the partner may use a feedstock we didn't list);
* every value the overlay sets gets `provenance[path] = {source: partner, confidence: ...}`
  automatically, so the output shows which numbers are the partner's;
* the overlay may add `provenance` entries only to give confidence/notes for its own
  values, and their source must be `partner`.

Guards against leaks: `.gitignore` ignores `**/private/*` (except `*.example.yaml`), and a
pre-commit hook refuses any staged file under a `private/` folder. Tests and CI never pass a
private directory, so they run on public values only.

Learn: docs/learn/config-overlays.md
"""

import copy
from pathlib import Path
from typing import Any

import yaml

from up_siting.profiles.schema import value_paths

PARTNER = "partner"
DEFAULT_PARTNER_CONFIDENCE = "strong"


def _merge(base: Any, over: Any) -> Any:
    if isinstance(base, dict) and isinstance(over, dict):
        out = dict(base)
        for key, value in over.items():
            out[key] = _merge(base.get(key), value) if key in base else copy.deepcopy(value)
        return out
    if isinstance(base, list) and isinstance(over, list) and all("id" in i for i in base + over):
        merged = {item["id"]: dict(item) for item in base}
        for item in over:
            merged[item["id"]] = _merge(merged.get(item["id"], {}), item)
        return list(merged.values())
    return copy.deepcopy(over)


def apply_overlay(public: dict[str, Any], private: dict[str, Any]) -> dict[str, Any]:
    """Merge `private` over `public` and tag every overlaid value's provenance as partner."""
    private = copy.deepcopy(private)
    private_prov: dict[str, dict[str, Any]] = private.pop("provenance", None) or {}
    for path, prov in private_prov.items():
        if prov.get("source", PARTNER) != PARTNER:
            raise ValueError(f"private provenance for {path} must have source: {PARTNER}")

    merged = _merge(public, private)
    # Paths the overlay set: compute them on the overlay alone (raw materials need ids).
    overlaid = value_paths(private)
    provenance = dict(merged.get("provenance") or {})
    for path in overlaid:
        given = private_prov.get(path, {})
        provenance[path] = {
            "source": PARTNER,
            "confidence": given.get("confidence", DEFAULT_PARTNER_CONFIDENCE),
            "note": given.get("note"),
        }
    merged["provenance"] = provenance
    return merged


def read_overlay(private_dir: Path, product_id: str) -> dict[str, Any] | None:
    """The private overlay for `product_id`, or None if there isn't one."""
    path = private_dir / f"{product_id}.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping at the top level")
    return data
