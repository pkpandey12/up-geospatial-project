"""Schema for product profiles (config/product_profiles/<product_id>.yaml), version 2.

A product profile holds everything the cost model needs to know about one product: what it
consumes per tonne of output, how much land the plant needs, who buys the output.

Conventions
-----------
* TPD = tonnes of OUTPUT per day (confirmed by the partners, 22 Nov 2026), chosen at run
  time within `tpd_range` (`default` is what a notebook uses unless told otherwise).
  annual output = tpd x operating_days_per_year; feedstock = output x tonnes_per_tonne_output.
* Every field must be present in the YAML. A value nobody has given yet is written as
  `null`; the validator accepts it and lists it (make profiles).
* **Provenance.** Every non-null value needs an entry in `provenance`, keyed by its path
  (`kwh_per_tonne_output`, `land.fixed_acres`, `raw_materials.maize.tonnes_per_tonne_output`)
  with a `source` and a `confidence` (strong / moderate / weak). Values from the partner come
  from the private overlay and carry `source: partner` (see overlay.py).
* **Routes.** Raw materials with the same `route` are used together; different routes are
  alternatives (ethanol from C-heavy molasses OR maize OR rice). `default_route` says which
  one a run uses unless told otherwise. A product with one route can leave `route` null.
* **Quality** is relative and district-specific: effective input ratio = base ratio /
  (district quality / `reference_quality`). The profile names the measure and its reference;
  districts without data use a factor of 1.0.
* Unknown keys are rejected (extra="forbid"), so a typo like `kwh_per_tone` fails loudly.

Learn: docs/learn/pydantic.md, docs/learn/config-overlays.md
"""

from enum import StrEnum
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Reusable constrained types. `| None` + no default = "key required, value may be null".
NonNegative = Annotated[float, Field(ge=0)]
Positive = Annotated[float, Field(gt=0)]
SnakeId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SizeClass(StrEnum):
    """Plot size classes used by the partners (1 acre = 4,046.86 sq m).

    Boundaries are half-open, lower bound included: Micro [0, 1), Small [1, 2),
    Medium [2, 5), Large [5, inf). Decided 24 Nov 2026 (being confirmed with the partner).
    """

    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Confidence(StrEnum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


class Provenance(_Strict):
    source: str = Field(min_length=1, description="Citation, or 'partner' for private values.")
    confidence: Confidence
    note: str | None = None


class Availability(_Strict):
    """How district supply of this input is estimated from another district variable.

    e.g. C-heavy molasses = cane crushed x 0.045; paddy straw = rice production x 1.5.
    """

    from_variable: SnakeId = Field(description="District variable, e.g. 'sugarcane' production.")
    ratio: Positive | None = Field(description="Tonnes of this input per tonne of from_variable.")
    basis: str | None = None


class RawMaterial(_Strict):
    id: SnakeId
    description: str | None = None
    route: SnakeId | None = Field(
        description="Inputs sharing a route are used together; routes are alternatives."
    )
    tonnes_per_tonne_output: Positive | None = Field(
        description="Tonnes of this input per tonne of output, at reference quality."
    )
    price_inr_per_tonne: NonNegative | None = Field(
        description="Statewide price if regulated (e.g. cane SAP); null if it varies by district."
    )
    quality_measure: str | None = Field(
        description="District quality variable, e.g. 'sugar_recovery_pct'; null = factor 1.0."
    )
    reference_quality: Positive | None = Field(
        description="Value of quality_measure at which tonnes_per_tonne_output applies."
    )
    availability: Availability | None
    eligible: bool = True
    eligibility_note: str | None = None


class WaterQuality(_Strict):
    grade: Literal["any", "raw", "treated", "potable"] | None
    max_tds_mg_per_l: Positive | None = Field(description="Maximum total dissolved solids.")
    notes: str | None = None


class Buyer(_Strict):
    id: SnakeId
    description: str | None = None


class LandRule(_Strict):
    """Partners' land rule: plot_acres = fixed_acres + acres_per_tpd x tpd."""

    fixed_acres: NonNegative | None
    acres_per_tpd: NonNegative | None


class TpdRange(_Strict):
    min: Positive | None
    max: Positive | None
    default: Positive | None

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"tpd_range.min ({self.min}) is greater than max ({self.max})")
        if self.default is not None:
            lo = self.min if self.min is not None else self.default
            hi = self.max if self.max is not None else self.default
            if not lo <= self.default <= hi:
                raise ValueError(f"tpd_range.default ({self.default}) is outside [min, max]")
        return self


def value_paths(data: dict[str, Any]) -> dict[str, Any]:
    """Every provenance-able leaf of a profile dict: {path: value}.

    Raw materials are addressed by id, not position, so a path survives reordering:
    'raw_materials.maize.tonnes_per_tonne_output'. Free text, ids, labels (routes, the name
    of a quality measure), booleans, buyers, provenance itself and schema_version are not
    values that need a source.
    """
    skip = {"schema_version", "product_id", "product_name", "output_unit_note", "default_route",
            "notes", "provenance", "buyers"}  # fmt: skip
    # Names and labels, not measured values:
    text = {"id", "description", "basis", "notes", "eligibility_note", "from_variable", "route",
            "quality_measure"}  # fmt: skip
    out: dict[str, Any] = {}

    def walk(value: Any, prefix: str) -> None:
        if isinstance(value, dict):
            for key, sub in value.items():
                if key in text or (not prefix and key in skip):
                    continue
                walk(sub, f"{prefix}.{key}" if prefix else key)
        elif isinstance(value, list):
            for item in value:
                walk(item, f"{prefix}.{item['id']}")
        elif not isinstance(value, bool):
            out[prefix] = value

    walk(data, "")
    return out


class ProductProfile(_Strict):
    schema_version: Literal[2]
    product_id: SnakeId
    product_name: str
    output_unit_note: str | None = None
    raw_materials: list[RawMaterial] = Field(min_length=1)
    default_route: SnakeId | None
    kwh_per_tonne_output: NonNegative | None
    kl_water_per_tonne_output: NonNegative | None
    water_quality: WaterQuality
    buyers: list[Buyer]
    max_sourcing_distance_km: Positive | None
    land: LandRule
    tpd_range: TpdRange
    operating_days_per_year: Annotated[int, Field(ge=1, le=366)] | None
    project_life_years: Annotated[int, Field(ge=1, le=60)] | None
    provenance: dict[str, Provenance] = Field(default_factory=dict)
    notes: str | None = None

    @model_validator(mode="after")
    def _raw_material_ids_unique(self) -> Self:
        ids = [rm.id for rm in self.raw_materials]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"duplicate raw_materials ids: {dupes}")
        return self

    @model_validator(mode="after")
    def _default_route_exists(self) -> Self:
        routes = {rm.route for rm in self.raw_materials if rm.route}
        if self.default_route is not None and self.default_route not in routes:
            raise ValueError(f"default_route '{self.default_route}' is not one of {sorted(routes)}")
        return self

    @model_validator(mode="after")
    def _every_value_has_provenance(self) -> Self:
        values = value_paths(self.model_dump(mode="json"))
        unknown = sorted(set(self.provenance) - set(values))
        if unknown:
            raise ValueError(f"provenance for paths that don't exist: {unknown}")
        unsourced = sorted(
            p for p, v in values.items() if v is not None and p not in self.provenance
        )
        if unsourced:
            raise ValueError(f"values without provenance (add source + confidence): {unsourced}")
        return self

    def route_materials(self, route: str | None = None) -> list[RawMaterial]:
        """Raw materials used together on `route` (default_route if None; all if no routes)."""
        route = route or self.default_route
        if route is None:
            return list(self.raw_materials)
        chosen = [rm for rm in self.raw_materials if rm.route == route]
        if not chosen:
            raise ValueError(f"no raw materials on route '{route}'")
        return chosen
