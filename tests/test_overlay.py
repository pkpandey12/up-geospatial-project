"""Private overlay (worked example): src/up_siting/profiles/overlay.py.

Uses only the committed .example.yaml shape files and synthetic values, never partner data.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from up_siting.common.paths import PRODUCT_PROFILES_DIR, REPO_ROOT
from up_siting.profiles.overlay import apply_overlay
from up_siting.profiles.schema import ProductProfile
from up_siting.profiles.validate import load_profile, main

PRIVATE_DIR = PRODUCT_PROFILES_DIR / "private"


def _yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture
def public() -> dict[str, Any]:
    return _yaml(PRODUCT_PROFILES_DIR / "ethanol.yaml")


def test_overlay_values_win_and_are_tagged_partner(public: dict[str, Any]) -> None:
    merged = apply_overlay(public, {"kwh_per_tonne_output": 123, "land": {"fixed_acres": 4}})
    profile = ProductProfile.model_validate(merged)
    assert profile.kwh_per_tonne_output == 123
    assert profile.land.fixed_acres == 4
    assert profile.land.acres_per_tpd is None  # untouched sibling stays public
    assert profile.provenance["kwh_per_tonne_output"].source == "partner"
    assert profile.provenance["kwh_per_tonne_output"].confidence == "strong"
    # public provenance survives for values the overlay didn't touch
    assert "NITI" in profile.provenance["raw_materials.maize.tonnes_per_tonne_output"].source


def test_raw_materials_merge_by_id(public: dict[str, Any]) -> None:
    overlay = {
        "raw_materials": [
            {"id": "maize", "price_inr_per_tonne": 22000},
            {
                "id": "sorghum",
                "route": "sorghum",
                "tonnes_per_tonne_output": 3.5,
                "price_inr_per_tonne": None,
                "quality_measure": None,
                "reference_quality": None,
                "availability": None,
            },
        ]
    }
    profile = ProductProfile.model_validate(apply_overlay(public, overlay))
    by_id = {rm.id: rm for rm in profile.raw_materials}
    assert by_id["maize"].price_inr_per_tonne == 22000
    assert by_id["maize"].tonnes_per_tonne_output == 3.34  # public value kept
    assert "sorghum" in by_id and [rm.id for rm in profile.raw_materials][:4] == [
        "c_heavy_molasses",
        "maize",
        "rice",
        "cane_juice",
    ]
    assert profile.provenance["raw_materials.sorghum.tonnes_per_tonne_output"].source == "partner"


def test_overlay_can_set_confidence_and_note_but_not_another_source(
    public: dict[str, Any],
) -> None:
    ok = apply_overlay(
        public,
        {
            "operating_days_per_year": 330,
            "provenance": {"operating_days_per_year": {"confidence": "moderate", "note": "est."}},
        },
    )
    prov = ProductProfile.model_validate(ok).provenance["operating_days_per_year"]
    assert (prov.source, prov.confidence, prov.note) == ("partner", "moderate", "est.")
    with pytest.raises(ValueError, match="must have source: partner"):
        apply_overlay(public, {"provenance": {"x": {"source": "a website"}}})


def test_overlay_does_not_modify_its_inputs(public: dict[str, Any]) -> None:
    overlay = {"land": {"fixed_acres": 4}}
    before_public, before_overlay = yaml.safe_dump(public), yaml.safe_dump(overlay)
    apply_overlay(public, overlay)
    assert yaml.safe_dump(public) == before_public
    assert yaml.safe_dump(overlay) == before_overlay


def test_example_files_are_valid_overlays(tmp_path: Path) -> None:
    # Copy the public profile and the example (renamed to the real name) into a temp folder.
    shutil.copy(PRODUCT_PROFILES_DIR / "ethanol.yaml", tmp_path / "ethanol.yaml")
    (tmp_path / "private").mkdir()
    shutil.copy(PRIVATE_DIR / "ethanol.example.yaml", tmp_path / "private" / "ethanol.yaml")
    profile = load_profile(tmp_path / "ethanol.yaml", tmp_path / "private")
    assert profile.default_route == "maize"
    assert profile.provenance["raw_materials.maize.price_inr_per_tonne"].source == "partner"
    assert main([str(tmp_path), "--private"]) == 0
    sealed = _yaml(PRIVATE_DIR / "ethanol.districts.example.yaml")
    assert {"good", "avoid", "product_id", "sealed"} <= set(sealed)


def test_without_private_dir_only_public_values_load() -> None:
    profile = load_profile(PRODUCT_PROFILES_DIR / "ethanol.yaml")
    assert all(p.source != "partner" for p in profile.provenance.values())


def test_no_private_file_is_tracked_by_git() -> None:
    """CI's safety net: only *.example.yaml may live in a committed private/ folder."""
    if shutil.which("git") is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("not a git checkout")
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    leaked = [f for f in tracked if "/private/" in f and not f.endswith(".example.yaml")]
    assert not leaked, f"confidential files are tracked: {leaked}"


def test_gitignore_hides_private_files_but_not_examples() -> None:
    if shutil.which("git") is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("not a git checkout")

    def ignored(rel: str) -> bool:
        res = subprocess.run(["git", "check-ignore", "-q", rel], cwd=REPO_ROOT, check=False)
        return res.returncode == 0

    assert ignored("config/product_profiles/private/ethanol.yaml")
    assert ignored("config/product_profiles/private/ethanol.districts.yaml")
    assert not ignored("config/product_profiles/private/ethanol.example.yaml")
