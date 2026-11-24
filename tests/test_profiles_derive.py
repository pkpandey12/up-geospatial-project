"""Derived quantities from a profile. All TODO(sage): see src/up_siting/profiles/derive.py."""

from typing import Any

import pytest

from up_siting.profiles.derive import (
    annual_feedstock_tonnes,
    annual_output_tonnes,
    effective_input_ratio,
    plot_acres,
    route_feedstock_tonnes,
    size_class,
)
from up_siting.profiles.schema import (
    LandRule,
    ProductProfile,
    RawMaterial,
    SizeClass,
    value_paths,
)


def _profile(**overrides: Any) -> ProductProfile:
    base: dict[str, Any] = {
        "schema_version": 2,
        "product_id": "widget",
        "product_name": "Widget",
        "raw_materials": [
            _rm("ore", 2.5),
            _rm("flux", 0.1),
        ],
        "default_route": None,
        "kwh_per_tonne_output": None,
        "kl_water_per_tonne_output": None,
        "water_quality": {"grade": None, "max_tds_mg_per_l": None},
        "buyers": [],
        "max_sourcing_distance_km": None,
        "land": {"fixed_acres": 2, "acres_per_tpd": 1},
        "tpd_range": {"min": None, "max": None, "default": None},
        "operating_days_per_year": 300,
        "project_life_years": None,
    }
    base.update(overrides)
    # Test profiles don't carry citations: give every non-null value a dummy provenance.
    base["provenance"] = {
        path: {"source": "test fixture", "confidence": "weak"}
        for path, value in value_paths(base).items()
        if value is not None
    }
    return ProductProfile.model_validate(base)


def _rm(rid: str, ratio: float | None, route: str | None = None, **extra: Any) -> dict[str, Any]:
    return {
        "id": rid,
        "route": route,
        "tonnes_per_tonne_output": ratio,
        "price_inr_per_tonne": None,
        "quality_measure": None,
        "reference_quality": None,
        "availability": None,
        **extra,
    }


# ---------------------------------------------------------------- plot_acres
@pytest.mark.parametrize(("tpd", "acres"), [(1, 3.0), (10, 12.0), (0.5, 2.5)])
def test_plot_acres_cbg_rule(tpd: float, acres: float) -> None:
    assert plot_acres(LandRule(fixed_acres=2, acres_per_tpd=1), tpd) == pytest.approx(acres)


@pytest.mark.parametrize("tpd", [0, -1])
def test_plot_acres_rejects_non_positive_tpd(tpd: float) -> None:
    with pytest.raises(ValueError):
        plot_acres(LandRule(fixed_acres=2, acres_per_tpd=1), tpd)


def test_plot_acres_names_the_missing_field() -> None:
    with pytest.raises(ValueError, match="acres_per_tpd"):
        plot_acres(LandRule(fixed_acres=2, acres_per_tpd=None), 5)


# ---------------------------------------------------------------- size_class
@pytest.mark.parametrize(
    ("acres", "expected"),
    [
        (0, SizeClass.MICRO),
        (0.99, SizeClass.MICRO),
        (1, SizeClass.SMALL),  # boundaries go to the higher class
        (1.5, SizeClass.SMALL),
        (2, SizeClass.MEDIUM),
        (4.999, SizeClass.MEDIUM),
        (5, SizeClass.LARGE),
        (120, SizeClass.LARGE),
    ],
)
def test_size_class_boundaries(acres: float, expected: SizeClass) -> None:
    assert size_class(acres) is expected


def test_size_class_rejects_negative() -> None:
    with pytest.raises(ValueError):
        size_class(-0.1)


# ---------------------------------------------------------------- annual quantities
def test_annual_output_tonnes() -> None:
    assert annual_output_tonnes(_profile(), tpd=10) == pytest.approx(3000)


def test_annual_output_needs_operating_days() -> None:
    with pytest.raises(ValueError, match="operating_days_per_year"):
        annual_output_tonnes(_profile(operating_days_per_year=None), tpd=10)


def test_annual_feedstock_tonnes() -> None:
    assert annual_feedstock_tonnes(_profile(), tpd=10) == pytest.approx(
        {"ore": 7500.0, "flux": 300.0}
    )


def test_annual_feedstock_names_the_missing_raw_material() -> None:
    profile = _profile(raw_materials=[_rm("ore", None)])
    with pytest.raises(ValueError, match="ore"):
        annual_feedstock_tonnes(profile, tpd=10)


# ---------------------------------------------------------------- quality factor (TODO)
def _quality_rm(**kw: Any) -> RawMaterial:
    base = _rm("cane", 18.0, quality_measure="sugar_recovery_pct", reference_quality=9.5)
    base.update(kw)
    return RawMaterial.model_validate(base)


@pytest.mark.todo
@pytest.mark.parametrize(
    ("district_quality", "expected"),
    [(9.5, 18.0), (10.45, 18.0 / 1.1), (8.55, 18.0 / 0.9), (None, 18.0)],
)
def test_effective_input_ratio(district_quality: float | None, expected: float) -> None:
    # Higher recovery than the 9.5% reference -> less cane per tonne of ethanol.
    assert effective_input_ratio(_quality_rm(), district_quality) == pytest.approx(expected)


@pytest.mark.todo
def test_effective_input_ratio_is_1_without_a_reference() -> None:
    rm = _quality_rm(reference_quality=None)
    assert effective_input_ratio(rm, 11.0) == pytest.approx(18.0)


@pytest.mark.todo
def test_effective_input_ratio_errors() -> None:
    with pytest.raises(ValueError, match="cane"):
        effective_input_ratio(_quality_rm(tonnes_per_tonne_output=None), 9.5)
    with pytest.raises(ValueError):
        effective_input_ratio(_quality_rm(), 0)


# ---------------------------------------------------------------- routes (TODO)
def _routed_profile() -> ProductProfile:
    return _profile(
        raw_materials=[
            _rm("molasses", 5.0, route="molasses"),
            _rm("maize", 3.0, route="maize"),
            _rm("enzyme", 0.01, route="maize"),
            _rm("juice", 18.0, route="juice", eligible=False),
        ],
        default_route="molasses",
    )


@pytest.mark.todo
def test_route_feedstock_uses_the_default_route() -> None:
    assert route_feedstock_tonnes(_routed_profile(), tpd=10) == pytest.approx({"molasses": 15000.0})


@pytest.mark.todo
def test_route_feedstock_named_route_and_ineligible() -> None:
    p = _routed_profile()
    assert route_feedstock_tonnes(p, 10, "maize") == pytest.approx(
        {"maize": 9000.0, "enzyme": 30.0}
    )
    assert route_feedstock_tonnes(p, 10, "juice") == pytest.approx({"juice": 54000.0})


@pytest.mark.todo
def test_route_feedstock_unknown_route_and_no_routes() -> None:
    with pytest.raises(ValueError, match="biogas"):
        route_feedstock_tonnes(_routed_profile(), 10, "biogas")
    # A profile without routes: every raw material, like annual_feedstock_tonnes.
    assert route_feedstock_tonnes(_profile(), 10) == pytest.approx({"ore": 7500.0, "flux": 300.0})
