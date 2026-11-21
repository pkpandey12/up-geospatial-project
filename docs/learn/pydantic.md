# pydantic (product-profile schema)

**What it is.** A data-validation library: you declare a class with type hints and
constraints; `Model.model_validate(data)` parses a dict (from YAML/JSON/API) into a typed
object or raises a `ValidationError` listing every problem with its location.

**Why here.** Product profiles are hand-edited YAML that drives the cost model. A typo or a
negative acreage must fail at `make lint`, not three steps later as a wrong ranking.
(Choosing pydantic over JSON Schema is a *Decision needed*; pydantic is the placeholder, and
it also *exports* a JSON Schema for editor autocomplete.)

## Concepts that matter

1. **Models are classes**: `class LandRule(BaseModel): fixed_acres: float | None`.
2. **Required but nullable.** `x: float | None` *with no default* means the key must be
   present but may be `null`. That's how `null  # TODO: partner` works: a forgotten key is an
   error, an admitted unknown is fine.
3. **Constraints** via `Annotated[float, Field(ge=0)]`, `gt`, `le`, `pattern=`,
   `min_length=`. Reused as `NonNegative`, `Positive`, `Fraction`, `SnakeId`.
4. **`extra="forbid"`** rejects unknown keys (catches `kwh_per_tone`).
5. **`frozen=True`** makes instances immutable: config shouldn't change mid-run.
6. **Model validators** (`@model_validator(mode="after")`) check rules across fields
   (`tpd_range.min <= max`, unique raw-material ids).
7. **`Literal[...]` and enums** restrict to known values (`grade`, `SizeClass`).
8. **`model_json_schema()`** exports JSON Schema → `profile.schema.json`, referenced by the
   `# yaml-language-server:` comment so VS Code autocompletes and underlines errors.
   A test fails if the committed schema is stale.

## Commands you'll run

```bash
make profiles                                   # validate + list partner TODO fields
uv run validate-profiles config/product_profiles --strict          # require no nulls
uv run validate-profiles config/product_profiles --write-schema    # after changing schema.py
```

## Common mistakes

- Giving a field a default of `None` when it should be required: then a missing key passes.
- Validating with `yaml.load` (unsafe) instead of `yaml.safe_load`.
- Putting computed values (plot acres, size class) in the YAML where they can disagree with
  the inputs. Derive them in code (`derive.py`).

## Interview question

- *Why validate config at load time instead of where it's used?* (Fail fast, with every error
  at once, at a single boundary; the rest of the code can trust the types.)
