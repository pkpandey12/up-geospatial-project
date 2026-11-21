"""Schema for product profiles (config/product_profiles/<product_id>.yaml).

A product profile holds everything the cost model needs to know about one product: what it
consumes per tonne of output, how much land the plant needs, who buys the output.

Conventions
-----------
* TPD = tonnes of OUTPUT per day (confirmed by the partners, 22 Nov 2026).
  annual output = tpd x operating_days_per_year; feedstock = output x tonnes_per_tonne_output.
* Every field must be present in the YAML. A value the partners haven't given yet is written
  as `null  # TODO: partner`; the validator accepts it and lists it (make profiles).
* Unknown keys are rejected (extra="forbid"), so a typo like `kwh_per_tone` fails loudly.

Learn: docs/learn/pydantic.md
"""

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Reusable constrained types. `| None` + no default = "key required, value may be null".
NonNegative = Annotated[float, Field(ge=0)]
Positive = Annotated[float, Field(gt=0)]
Fraction = Annotated[float, Field(gt=0, le=1)]
SnakeId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SizeClass(StrEnum):
    """Plot size classes used by the partners (1 acre = 4,046.86 sq m).

    Boundaries are half-open, lower bound included: Micro [0, 1), Small [1, 2),
    Medium [2, 5), Large [5, inf). The partners still have to confirm which side
    a plot of exactly 2 or 5 acres falls on.
    """

    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class RawMaterial(_Strict):
    id: SnakeId
    description: str | None = None
    tonnes_per_tonne_output: Positive | None = Field(
        description="Tonnes of this input per tonne of output."
    )
    quality_factor: Fraction | None = Field(
        description="0-1 adjustment for usable quality. Meaning still to be confirmed "
        "with the partners (see Decisions needed)."
    )


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

    @model_validator(mode="after")
    def _min_not_above_max(self) -> Self:
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError(f"tpd_range.min ({self.min}) is greater than max ({self.max})")
        return self


class ProductProfile(_Strict):
    schema_version: Literal[1]
    product_id: SnakeId
    product_name: str
    raw_materials: list[RawMaterial] = Field(min_length=1)
    kwh_per_tonne_output: NonNegative | None
    kl_water_per_tonne_output: NonNegative | None
    water_quality: WaterQuality
    buyers: list[Buyer]
    max_sourcing_distance_km: Positive | None
    land: LandRule
    tpd_range: TpdRange
    operating_days_per_year: Annotated[int, Field(ge=1, le=366)] | None
    project_life_years: Annotated[int, Field(ge=1, le=60)] | None
    notes: str | None = None

    @model_validator(mode="after")
    def _raw_material_ids_unique(self) -> Self:
        ids = [rm.id for rm in self.raw_materials]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"duplicate raw_materials ids: {dupes}")
        return self
