# Sage's TODO list

Everything here is yours to implement. Each item has the test that checks it.
`make todo` runs only these tests as honest pass/fail; `make test` shows them as `x`
(expected failure) until you implement them, so the main suite stays green.

Rules: read the docstring and pseudocode first, then the test. Ask for a **hint** before
asking for the answer. When an item passes, tick it and note anything you'd say about it
in an interview.

Difficulty: 1 = warm-up, 2 = needs thought, 3 = design work.

## Phase 1: EDA

| ✓ | Item | File | Checked by | Practises | Diff. |
|---|---|---|---|---|---|
| ☐ | `plot_acres(land, tpd)` | `src/up_siting/profiles/derive.py` | `tests/test_profiles_derive.py::test_plot_acres_*` | guarding missing config, linear rule | 1 |
| ☐ | `size_class(acres)` | `src/up_siting/profiles/derive.py` | `tests/test_profiles_derive.py::test_size_class_*` | boundary conditions, enums | 1 |
| ☐ | `annual_output_tonnes(profile, tpd)` | `src/up_siting/profiles/derive.py` | `tests/test_profiles_derive.py::test_annual_output_*` | nested config, units in names | 1 |
| ☐ | `annual_feedstock_tonnes(profile, tpd)` | `src/up_siting/profiles/derive.py` | `tests/test_profiles_derive.py::test_annual_feedstock_*` | reuse, dict comprehensions | 1 |
| ☐ | `map_to_lgd(df, name_col, name_map)` | `src/up_siting/common/names.py` | `tests/test_names.py::test_map_to_lgd_*` | left/anti joins, row-count invariants, `validate=` | 2 |
| ☐ | EDA step 2: coverage audit | `notebooks/eda/02_coverage.ipynb` | the `assert` cell at the end of each section | registry of sources, cross join, pivot, gap analysis | 2 |
| ☐ | Add each source you download | `docs/data-sources.md` | notebook 02, section 1 assert | provenance, licences | 1 |
| ☐ | Log every gap/surprise | `docs/eda/data-quality-log.md` | review | data-quality discipline | 1 |

Suggested order: the four `derive.py` functions (≈30 min), then `map_to_lgd`, then download
sources and do notebook 02.

## Done

*(move rows here when they pass)*
