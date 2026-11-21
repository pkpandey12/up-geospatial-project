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
    Practises: guarding against missing config, linear rules.
    """
    # 1. Reject tpd <= 0.
    # 2. Reject a None in either land field, naming which one.
    # 3. Return the linear rule.
    raise NotImplementedError("TODO(sage): implement plot_acres")


def size_class(acres: float) -> SizeClass:
    """Partners' size class for a plot of `acres` acres.

    Inputs:  acres >= 0.
    Returns: SizeClass.MICRO for [0, 1), SMALL for [1, 2), MEDIUM for [2, 5), LARGE for 5+.
    Edge cases: negative acres -> ValueError. Exactly 1, 2 and 5 go to the HIGHER class.
    Practises: boundary conditions (the classic off-by-one interview topic), enums.
    """
    # 1. Reject negative input.
    # 2. Walk the thresholds from smallest to largest, return the first class that fits.
    raise NotImplementedError("TODO(sage): implement size_class")


def annual_output_tonnes(profile: ProductProfile, tpd: float) -> float:
    """Tonnes of output per year = tpd x operating_days_per_year.

    Edge cases: tpd <= 0 -> ValueError; operating_days_per_year is None -> ValueError.
    Practises: reading nested config, explicit units in names.
    """
    raise NotImplementedError("TODO(sage): implement annual_output_tonnes")


def annual_feedstock_tonnes(profile: ProductProfile, tpd: float) -> dict[str, float]:
    """Tonnes per year of each raw material, keyed by raw material id.

    Returns: {raw_material.id: annual_output_tonnes x tonnes_per_tonne_output}.
    Edge cases: any tonnes_per_tonne_output is None -> ValueError naming the raw material.
                Do NOT apply quality_factor yet: what it multiplies is a "Decision needed".
    Practises: reuse (call annual_output_tonnes), dict comprehensions.
    """
    raise NotImplementedError("TODO(sage): implement annual_feedstock_tonnes")
