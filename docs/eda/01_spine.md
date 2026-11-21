# EDA 01: LGD district spine and name map (write-up)

**Notebook:** `notebooks/eda/01_spine.ipynb` · **Status:** done (worked example) · **Data:** LGD PDF downloaded 2026-11-21

## Question
What is the authoritative list of UP's districts, what is each one's permanent key, and how
do we turn the names other sources print into that key?

## Answer
- **75 districts**, keyed by the **LGD district code** (unique, numeric, present for all).
  → `dbt/seeds/lgd_district_spine.csv` (+ `data/interim/lgd/up_district_spine.parquet`).
- **Name map** of 107 aliases (75 official LGD names + 32 hand-curated former names,
  spelling variants and alternate names), each pointing at exactly one district.
  → `dbt/seeds/district_name_map.csv`, built from `dbt/seeds/district_aliases.csv`.
- **Lineage** of the 5 districts created since Census 2001 (Kasganj 2008; Amethi 2010; Hapur,
  Shamli, Sambhal 2011) and their parents → `dbt/seeds/district_lineage.csv`. LGD's census
  codes independently confirm the set of children.

## Method
1. Parsed the PDF with a column-boundary + text-row + stitch approach (pdfplumber's default
   table finder drops every other row because of zebra striping).
2. Profiled every column with one DuckDB `UNPIVOT` query.
3. Cleaned: `''`/`'000'` → missing census code; dropped the local-name column (DQ-001/002).
4. Checked name uniqueness after normalisation, validated the hand-curated aliases against
   LGD (code **and** name), built the map, asserted one-key-one-district.

## Findings
See the notebook's section 9 and DQ-001 to DQ-004 in the data-quality log. Most important for
the model: **Census-based data has no direct values for 4–5 districts** (DQ-003).

## Open items
- 29 of 32 aliases rest on general knowledge, not a cited source (`evidence` column).
  Check renames against LGD's "View History" per district when convenient.
- Sambhal's second parent (Budaun) is unverified.
