"""Unit constants. Every conversion in the project uses these, so a typo can only happen once."""

SQM_PER_ACRE = 4046.86
SQM_PER_HECTARE = 10_000.0
SQM_PER_SQFT = 0.092903

ACRES_PER_HECTARE = SQM_PER_HECTARE / SQM_PER_ACRE  # about 2.471


def acres_to_sqm(acres: float) -> float:
    """Convert acres to square metres (1 acre = 4,046.86 sq m)."""
    return acres * SQM_PER_ACRE
