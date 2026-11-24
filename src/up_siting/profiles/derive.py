"""Quantities derived from a product profile at a chosen plant size (TPD).

All four functions are TODO(sage). Tests: tests/test_profiles_derive.py (run `make todo`).
TPD = tonnes of OUTPUT per day.
"""

from up_siting.profiles.schema import LandRule, ProductProfile, SizeClass


def plot_acres(land: LandRule, tpd: float) -> float:
    """Plot size in acres for a plant of `tpd` tonnes of output per day.

    Inputs:  land, the profile's LandRule; tpd, tonnes of output per day.
    Returns: fixed_acres + acres_per_tpd x tpd.
    Edge cases: tpd <= 0 -> ValueError; fixed_acres or acres_per_tpd is None (partner hasn't
                told us yet) -> ValueError whose message names the missing field.
    """
    # 1. Reject tpd <= 0.
    # 2. Reject a None in either land field, naming which one.
    # 3. Return the linear rule.
    if tpd <= 0:
        raise ValueError(f"tpd must be > 0, got {tpd}")
    if land.fixed_acres is None:
        raise ValueError("fixed_acres is None")
    if land.acres_per_tpd is None:
        raise ValueError("acres_per_tpd is None")
    return land.fixed_acres + land.acres_per_tpd * tpd


def size_class(acres: float) -> SizeClass:
    """Partners' size class for a plot of `acres` acres.

    Inputs:  acres >= 0.
    Returns: SizeClass.MICRO for [0, 1), SMALL for [1, 2), MEDIUM for [2, 5), LARGE for 5+.
    Edge cases: negative acres -> ValueError. Exactly 1, 2 and 5 go to the HIGHER class.
    Practises: boundary conditions (the classic off-by-one interview topic), enums.
    """
    # 1. Reject negative input.
    # 2. Walk the thresholds from smallest to largest, return the first class that fits.
    if acres < 0:
        raise ValueError(f"acres must be >= 0, got {acres}")
    if acres < 1:
        return SizeClass.MICRO
    elif acres < 2:
        return SizeClass.SMALL
    elif acres < 5:
        return SizeClass.MEDIUM
    else:
        return SizeClass.LARGE


def annual_output_tonnes(profile: ProductProfile, tpd: float) -> float:
    """Tonnes of output per year = tpd x operating_days_per_year.

    Edge cases: tpd <= 0 -> ValueError; operating_days_per_year is None -> ValueError.
    Practises: reading nested config, explicit units in names.
    """
    if tpd <= 0:
        raise ValueError(f"tpd must be > 0, got {tpd}")
    if profile.operating_days_per_year is None:
        raise ValueError("operating_days_per_year is None")
    return tpd * profile.operating_days_per_year


def annual_feedstock_tonnes(profile: ProductProfile, tpd: float) -> dict[str, float]:
    """Tonnes per year of each raw material, keyed by raw material id.

    Returns: {raw_material.id: annual_output_tonnes x tonnes_per_tonne_output}.
    Edge cases: any tonnes_per_tonne_output is None -> ValueError naming the raw material.
                Do NOT apply quality_factor yet: what it multiplies is a "Decision needed".
    Practises: reuse (call annual_output_tonnes), dict comprehensions.
    """
    annual_output = annual_output_tonnes(profile, tpd)
    feedstock = {}
    for raw in profile.raw_materials:
        if raw.tonnes_per_tonne_output is None:
            raise ValueError(f"raw_material {raw.id} has tonnes_per_tonne_output = None")
        feedstock[raw.id] = annual_output * raw.tonnes_per_tonne_output
    return feedstock
