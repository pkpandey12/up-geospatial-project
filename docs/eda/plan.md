# EDA plan (Phase 1, to 1 Jan 2027)

*Follows the design doc's eight-step EDA plan (`docs/design/design-doc-2026-11-24.md`, "EDA
plan"). Ethanol first, then CBG. District-level, no geography. Question: do the public
sources join cleanly at district level and give an ethanol ranking someone could act on?*

## The eight steps → notebooks

| Step | What | Notebook / file | Who | Status |
|---|---|---|---|---|
| 1 | LGD spine (75 districts) + name map | `01_spine.ipynb` | Claude (worked example) | ✅ 22 Nov |
| 2 | Coverage audit: every source × 75 districts, years, gaps, licence | `02_coverage.ipynb` | Sage | Skeleton updated (session 2) |
| — | Source loaders: one tidy table per source at its own grain, LGD-mapped | `10_apy_crop_production`, `11_hq_climate`, then `12_…` per manual download | Claude | APY, HQ climate ✅; rest after downloads |
| 3 | Product profiles with source + confidence; partner figures in the private overlay | `config/product_profiles/{ethanol,cbg}.yaml`; `private/` | Claude (public), partner (private) | Public v2 ✅; overlay by 15 Dec |
| 4 | Each variable alone: distribution, spread between districts, outliers, trend | one section per variable in `04_variables.ipynb` (to create) | Sage | — |
| 5 | Join into one district table: 75 rows, one per LGD code, coverage per column | `03_district_table.ipynb` | Sage | Skeleton (session 2) |
| 6 | Correlations and redundancy (don't count one effect twice) | `03_district_table.ipynb` §6 | Sage | — |
| 7 | Check against the ground: partner's **sealed** good/avoid list; deal prices vs circle rates | `07_ground_truth.ipynb` (to create) | Sage | Waiting on partner (15 Dec) |
| 8 | Prototype cost model + naive baseline + go/pivot | `08_cost_model.ipynb` (to create) | Sage | — |

## Variables for ethanol (and how each reaches the district without a map)

| Variable | Source | Grain → district | Notes |
|---|---|---|---|
| Cane production, 3-year mean, and CV over 10+ years | `apy_idp` (EDA 10) | District, LGD code | 45 districts from 2020-21 (DQ-007); don't compute CV across the break |
| Maize, rice production (grain routes) | `apy_idp` | District | 2024-25 provisional (DQ-006) |
| **Feedstock indicator** per route | profile `availability` × district variable | District | C-heavy molasses ≈ cane crushed × 0.045 (cane production until S-1 a); maize = production |
| Existing use (distillery capacity) | `dfpd_distilleries` | Plant → district | Subtract from the indicator; approved ≠ built |
| Quality factor | profile `quality_measure` | District | 1.0 everywhere for Phase 1 (S-1 b) |
| Input price | cane SAP (constant); maize from `agmarknet_ceda`; FCI rice (constant) | Market → Census 2011 district | Regulated prices can't rank; maize may |
| Groundwater stress (hard filter) | `cgwb_gw` | Block listed under district | Share of over-exploited + critical blocks |
| Land price | `igrs_circle_rates` (sample), `industrial_land` | Sub-registrar / park → district | Calibrate with the partner's deal prices |
| Climate flags | `nasa_power` at `wikidata_hq` points (EDA 11) | HQ point | Heat days, rainfall CV; GHI barely varies (×1.1) |
| Power | `uperc_tariff` | State | Constant: sets the level, not the order |

**Keep rule** (design doc): ≥ 70 of 75 districts, data ≤ 3 years old (or age shown),
varies enough to change a ranking, licence allows the use.

## Cost model prototype (step 8)

```
Overhead[d, p, s] = C_raw[d, p, s] + C_land[d, p, s] + C_water[d, p, s] + C_power[p]   (₹/t)
```

* **Hard filters first:** feedstock indicator (minus existing use) < annual need at the
  chosen TPD (`route_feedstock_tonnes`); for a water-heavy route, share of
  over-exploited + critical blocks above a threshold.
* **Raw material:** effective input ratio (`effective_input_ratio`) × price, per route;
  haulage within the district only.
* **Land:** ₹/sq m × plot (land rule) spread over project life ÷ annual output.
* **Water:** kL/t × (supply + treatment) cost; **power:** kWh/t × tariff (constant).

### Ranges, confidence, rank ranges

* Rerun the model with each major assumption at −20% and +20% (feedstock price and ratio,
  land price, water cost, haulage), one at a time and all-low / all-high.
* Per district: **₹/t range** (min–max across runs), **rank range** (best–worst rank), and
  a **confidence rating**: strong / moderate / weak from the weakest input's provenance
  confidence and the district's data coverage (e.g. "no recent cane data" → weak).
* A district that stays near the top across runs is a robust pick.

### The naive baseline and the comparison

* **Baseline:** districts sorted by raw-material volume alone (cane production for the cane
  routes; maize production for the maize route).
* **Compare:** Spearman rank correlation between model and baseline; list every district
  that moves ≥ 10 places with a **written reason** (e.g. "over-exploited groundwater",
  "land 3× cheaper").
* The model earns its keep only where it disagrees for a reason.

## Viability bars (go / pivot by 1 Jan 2027)

1. **Agrees with the partner:** the ranking broadly matches his good/avoid districts
   (e.g. Lakhimpur Kheri as good for ethanol). Measure: how many of his "good" districts
   are in the model's top quartile (by rank range), and none of his "avoid" are.
2. **Beats the naive baseline somewhere that matters**, with a written reason.

If both fail, keep the pipeline and point it at a question the data does answer.

## The partner's sealed list (placeholder)

`config/product_profiles/private/<product>.districts.yaml` (git-ignored; shape in
`ethanol.districts.example.yaml`): his good and avoid districts **given before he sees any
output**, by LGD code, with a reason each. Opened only in step 7, after the prototype
ranking exists. Never printed in a committed notebook output; compare with aggregate
measures (counts, overlap), not the list itself.
