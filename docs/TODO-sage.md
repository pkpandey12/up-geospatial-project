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
| ☐ | **Review follow-up:** `map_to_lgd` must not modify `name_map`, and must keep the input's index; replace `drop(..., inplace=True)` (deprecated in pandas 3) | `src/up_siting/common/names.py` | `tests/test_names.py::test_map_to_lgd_does_not_modify_name_map`, `::test_map_to_lgd_keeps_input_index` (strict xfail: delete the `xfail` line once they pass) | side effects, index alignment, pandas deprecations | 1 |
| ⏸ | EDA step 2: coverage audit (**on hold**: design doc updated; re-scoped in session 2) | `notebooks/eda/02_coverage.ipynb` | the `assert` cell at the end of each section | registry of sources, cross join, pivot, gap analysis | 2 |
| ☐ | Add each source you download | `docs/data-sources.md` | notebook 02, section 1 assert | provenance, licences | 1 |
| ☐ | Log every gap/surprise | `docs/eda/data-quality-log.md` | review | data-quality discipline | 1 |

## Done

| ✓ | Item | Done | Review notes |
|---|---|---|---|
| ☑ | `plot_acres(land, tpd)` | 2026-11-24 | Correct; error names the missing field. |
| ☑ | `size_class(acres)` | 2026-11-24 | Correct, half-open boundaries. Interview angle: why `<` not `<=` at each threshold. |
| ☑ | `annual_output_tonnes(profile, tpd)` | 2026-11-24 | Correct. |
| ☑ | `annual_feedstock_tonnes(profile, tpd)` | 2026-11-24 | Correct; reuses `annual_output_tonnes`. A loop is the right call here (it has to raise with the material's name). |
| ☑ | `map_to_lgd(df, name_col, name_map)` | 2026-11-24 | Passes; good use of `validate="many_to_one"` plus an explicit row-count check. Three follow-ups found in review (row above). |
