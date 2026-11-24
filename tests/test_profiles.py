"""Product-profile schema and validator (written in full)."""

import copy
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from up_siting.common.paths import PRODUCT_PROFILES_DIR
from up_siting.profiles.schema import ProductProfile
from up_siting.profiles.validate import (
    JSON_SCHEMA_FILE,
    json_schema,
    load_profile,
    main,
    missing_fields,
)

ALL_PROFILES = sorted(PRODUCT_PROFILES_DIR.glob("*.yaml"))


@pytest.fixture
def cbg_dict() -> dict[str, Any]:
    return yaml.safe_load((PRODUCT_PROFILES_DIR / "cbg.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", ALL_PROFILES, ids=lambda p: p.name)
def test_every_committed_profile_is_valid(path: Path) -> None:
    load_profile(path)


def test_cbg_land_rule_from_brief() -> None:
    cbg = load_profile(PRODUCT_PROFILES_DIR / "cbg.yaml")
    assert cbg.land.fixed_acres == 2
    assert cbg.land.acres_per_tpd == 1


def test_missing_fields_lists_partner_todos() -> None:
    missing = missing_fields(load_profile(PRODUCT_PROFILES_DIR / "cbg.yaml"))
    assert "kwh_per_tonne_output" in missing
    assert "raw_materials.paddy_straw.tonnes_per_tonne_output" in missing  # by id, not index
    assert "land.fixed_acres" not in missing
    assert "notes" not in missing  # free text is never "missing"


def test_ethanol_profile_follows_esy_2026_27_rule() -> None:
    eth = load_profile(PRODUCT_PROFILES_DIR / "ethanol.yaml")
    by_id = {rm.id: rm for rm in eth.raw_materials}
    assert {"c_heavy_molasses", "maize", "rice", "cane_juice"} <= set(by_id)
    assert by_id["cane_juice"].eligible is False
    assert "NOT ELIGIBLE ESY 2026-27" in (by_id["cane_juice"].eligibility_note or "")
    assert all(by_id[i].eligible for i in ["c_heavy_molasses", "maize", "rice"])
    assert eth.route_materials()[0].id == "c_heavy_molasses"  # default route
    assert [rm.id for rm in eth.route_materials("maize")] == ["maize"]


@pytest.mark.parametrize("path", ALL_PROFILES, ids=lambda p: p.name)
def test_every_public_value_has_a_source_and_confidence(path: Path) -> None:
    profile = load_profile(path)
    for prov in profile.provenance.values():
        assert prov.source.strip() and prov.confidence
        assert prov.source != "partner", "partner values belong in the private overlay"


@pytest.mark.parametrize(
    ("mutate", "error_fragment"),
    [
        (lambda d: d.update(kwh_per_tone=1), "Extra inputs are not permitted"),
        (lambda d: d.pop("kwh_per_tonne_output"), "Field required"),
        (lambda d: d["land"].update(fixed_acres=-1), "greater than or equal to 0"),
        (lambda d: d["tpd_range"].update(min=10, max=5), "greater than max"),
        (lambda d: d["raw_materials"][0].update(quality_factor=0.5), "Extra inputs"),
        (lambda d: d.update(kwh_per_tonne_output=5), "values without provenance"),
        (lambda d: d["provenance"].update(x={"source": "x", "confidence": "weak"}), "don't exist"),
        (lambda d: d["provenance"]["land.fixed_acres"].update(confidence="sure"), "Input should"),
        (lambda d: d.update(default_route="biogas"), "not one of"),
        (lambda d: d["tpd_range"].update(min=1, max=5, default=9), "outside"),
        (lambda d: d.update(raw_materials=[]), "at least 1 item"),
        (lambda d: d.update(operating_days_per_year=400), "less than or equal to 366"),
        (lambda d: d.update(product_id="CBG gas"), "String should match pattern"),
        (lambda d: d["raw_materials"].append(d["raw_materials"][0]), "duplicate raw_materials"),
    ],
)
def test_schema_rejects_bad_profiles(cbg_dict: dict[str, Any], mutate, error_fragment) -> None:
    data = copy.deepcopy(cbg_dict)
    mutate(data)
    with pytest.raises(ValidationError, match=error_fragment):
        ProductProfile.model_validate(data)


def test_product_id_must_match_file_name(tmp_path: Path, cbg_dict: dict[str, Any]) -> None:
    path = tmp_path / "not_cbg.yaml"
    path.write_text(yaml.safe_dump(cbg_dict), encoding="utf-8")
    with pytest.raises(ValueError, match="must match the file name"):
        load_profile(path)


def test_cli_exit_codes(tmp_path: Path, cbg_dict: dict[str, Any]) -> None:
    assert main([str(PRODUCT_PROFILES_DIR)]) == 0
    assert main([str(PRODUCT_PROFILES_DIR), "--strict"]) == 1  # profiles still have nulls

    bad = copy.deepcopy(cbg_dict)
    bad["land"]["acres_per_tpd"] = "lots"
    (tmp_path / "cbg.yaml").write_text(yaml.safe_dump(bad), encoding="utf-8")
    assert main([str(tmp_path)]) == 1


def test_committed_json_schema_is_up_to_date() -> None:
    committed = (PRODUCT_PROFILES_DIR / JSON_SCHEMA_FILE).read_text(encoding="utf-8")
    assert committed == json_schema(), (
        "Schema changed: run `uv run validate-profiles config/product_profiles --write-schema`"
    )
