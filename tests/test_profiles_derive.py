"""Derived quantities from a profile. All TODO(sage): see src/up_siting/profiles/derive.py."""

from typing import Any

import pytest

from up_siting.profiles.derive import (
    annual_feedstock_tonnes,
    annual_output_tonnes,
    plot_acres,
    size_class,
)
from up_siting.profiles.schema import LandRule, ProductProfile, SizeClass

pytestmark = pytest.mark.todo


def _profile(**overrides: Any) -> ProductProfile:
    base: dict[str, Any] = {
        "schema_version": 1,
        "product_id": "widget",
        "product_name": "Widget",
        "raw_materials": [
            {"id": "ore", "tonnes_per_tonne_output": 2.5, "quality_factor": None},
            {"id": "flux", "tonnes_per_tonne_output": 0.1, "quality_factor": None},
        ],
        "kwh_per_tonne_output": None,
        "kl_water_per_tonne_output": None,
        "water_quality": {"grade": None, "max_tds_mg_per_l": None},
        "buyers": [],
        "max_sourcing_distance_km": None,
        "land": {"fixed_acres": 2, "acres_per_tpd": 1},
        "tpd_range": {"min": None, "max": None},
        "operating_days_per_year": 300,
        "project_life_years": None,
    }
    base.update(overrides)
    return ProductProfile.model_validate(base)


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
    profile = _profile(
        raw_materials=[{"id": "ore", "tonnes_per_tonne_output": None, "quality_factor": None}]
    )
    with pytest.raises(ValueError, match="ore"):
        annual_feedstock_tonnes(profile, tpd=10)
