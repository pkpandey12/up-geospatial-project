"""Quantities derived from a product profile at a chosen plant size (TPD).

Functions are TODO(sage). Tests: tests/test_profiles_derive.py (run `make todo`).
TPD = tonnes of OUTPUT per day.
"""

from up_siting.profiles.schema import LandRule, ProductProfile, RawMaterial, SizeClass


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
                Sums EVERY raw material: right for single-route products only; for
                alternatives (ethanol) use route_feedstock_tonnes.
    Practises: reuse (call annual_output_tonnes), dict comprehensions.
    """
    annual_output = annual_output_tonnes(profile, tpd)
    feedstock = {}
    for raw in profile.raw_materials:
        if raw.tonnes_per_tonne_output is None:
            raise ValueError(f"raw_material {raw.id} has tonnes_per_tonne_output = None")
        feedstock[raw.id] = annual_output * raw.tonnes_per_tonne_output
    return feedstock


def effective_input_ratio(raw_material: RawMaterial, district_quality: float | None) -> float:
    """Tonnes of input per tonne of output in a district, adjusted for its quality.

    Rule (decided 24 Nov 2026): effective = base / (district_quality / reference_quality).
    Better-than-reference quality (e.g. higher sugar recovery) needs LESS input.
    Inputs:  raw_material from a profile; district_quality, the district's value of
             raw_material.quality_measure (None when the district has no data).
    Returns: the effective ratio (float).
    Edge cases: tonnes_per_tonne_output is None -> ValueError naming the raw material;
                district_quality None, or quality_measure/reference_quality None -> factor 1.0
                (return the base ratio); district_quality <= 0 -> ValueError.
    Practises: guarding optional config, ratio arithmetic, documenting a modelling rule.
    """
    # 1. Reject a missing base ratio (name the raw material in the message).
    # 2. If there's nothing to compare (no measure, no reference or no district value),
    #    return the base ratio unchanged.
    # 3. Reject a non-positive district value.
    # 4. factor = district_quality / reference_quality; return base / factor.
    raise NotImplementedError("TODO(sage): implement effective_input_ratio")


def route_feedstock_tonnes(
    profile: ProductProfile, tpd: float, route: str | None = None
) -> dict[str, float]:
    """Tonnes per year of each raw material on ONE feedstock route, keyed by raw material id.

    Why: ethanol's raw materials are alternatives (C-heavy molasses OR maize OR rice), so
    annual_feedstock_tonnes (which sums every raw material) over-counts. Routes fix that.
    Inputs:  profile; tpd (tonnes of output per day); route, or None for default_route.
    Returns: {raw_material.id: annual_output_tonnes x tonnes_per_tonne_output} for the
             materials on that route only (all materials if the profile has no routes).
    Edge cases: unknown route -> ValueError (profile.route_materials raises it);
                a material on the route without a ratio -> ValueError naming it;
                an ineligible material (eligible: false) is still computed (the caller
                decides whether to show it), but its id must be in the result.
    Practises: reuse (annual_output_tonnes, profile.route_materials), filtering config.
    """
    # 1. annual = annual_output_tonnes(profile, tpd)
    # 2. materials = profile.route_materials(route)
    # 3. Same loop as annual_feedstock_tonnes, over `materials` only.
    raise NotImplementedError("TODO(sage): implement route_feedstock_tonnes")
