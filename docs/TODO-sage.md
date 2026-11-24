# Sage's TODO list

Everything here is yours to implement. Each item has the test that checks it.
`make todo` runs only these tests as honest pass/fail; `make test` shows them as `x`
(expected failure) until you implement them, so the main suite stays green.

Rules: read the docstring and pseudocode first, then the test. Ask for a **hint** before
asking for the answer. When an item passes, tick it and note anything you'd say about it
in an interview.

Difficulty: 1 = warm-up, 2 = needs thought, 3 = design work.

## Phase 1: EDA

Phase 1 split: Claude loads each source into a tidy, LGD-keyed table (loader notebooks
10, 11, …); you build the joins, the analysis and the cost model. Order below = suggested
order (ethanol first).

| ✓ | Item | File | Checked by | Practises | Diff. |
|---|---|---|---|---|---|
| ☐ | **Manual downloads**, priorities 1–6 first (`make register` for each) | `docs/eda/downloads.md` checklist | the manifest; EDA 02 §1 assert | provenance, licences | 1 |
| ☐ | **Review follow-up:** `map_to_lgd` must not modify `name_map`, must keep the input's index; replace `drop(..., inplace=True)` (deprecated in pandas 3) | `src/up_siting/common/names.py` | `tests/test_names.py::test_map_to_lgd_does_not_modify_name_map`, `::test_map_to_lgd_keeps_input_index` (strict xfail: delete the `xfail` line once they pass) | side effects, index alignment, pandas deprecations | 1 |
| ☐ | `effective_input_ratio(raw_material, district_quality)`: the relative quality factor | `src/up_siting/profiles/derive.py` | `tests/test_profiles_derive.py::test_effective_input_ratio*` | guarding optional config, a modelling rule in code | 1 |
| ☐ | `route_feedstock_tonnes(profile, tpd, route)`: feedstock for one ethanol route | `src/up_siting/profiles/derive.py` | `tests/test_profiles_derive.py::test_route_feedstock_*` | reuse, filtering config | 1 |
| ☐ | EDA step 2: coverage audit (re-scoped: reads manifests + loader outputs) | `notebooks/eda/02_coverage.ipynb` | the `assert` cell at the end of each section | DuckDB over JSONL and Parquet, cross join, pivot, gap analysis | 2 |
| ☐ | EDA steps 5–6: the district table (ethanol), coverage per column, redundancy | `notebooks/eda/03_district_table.ipynb` | assert cells (75 rows, unique LGD, coverage) | left joins onto a spine, `validate=`, Spearman | 2 |
| ☐ | Log every gap/surprise | `docs/eda/data-quality-log.md` | review | data-quality discipline | 1 |
| ☐ | Stretch: make `size_class` table-driven (one constant of thresholds; decided 24 Nov) | `src/up_siting/profiles/derive.py` | existing `test_size_class_*` | data over code | 1 |

## Done

| ✓ | Item | Done | Review notes |
|---|---|---|---|
| ☑ | `plot_acres(land, tpd)` | 2026-11-24 | Correct; error names the missing field. |
| ☑ | `size_class(acres)` | 2026-11-24 | Correct, half-open boundaries. Interview angle: why `<` not `<=` at each threshold. |
| ☑ | `annual_output_tonnes(profile, tpd)` | 2026-11-24 | Correct. |
| ☑ | `annual_feedstock_tonnes(profile, tpd)` | 2026-11-24 | Correct; reuses `annual_output_tonnes`. A loop is the right call here (it has to raise with the material's name). |
| ☑ | `map_to_lgd(df, name_col, name_map)` | 2026-11-24 | Passes; good use of `validate="many_to_one"` plus an explicit row-count check. Three follow-ups found in review (row above). |
