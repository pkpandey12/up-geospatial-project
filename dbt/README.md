# dbt (Phase 3)

The dbt project (`dbt_project.yml`, `models/{staging,intermediate/spatial,marts}`, `macros/spatial`,
`tests/`) arrives in Phase 3. Only `seeds/` exists now, because EDA 01 produces reference tables:

| Seed | Made by | Notes |
|---|---|---|
| `district_aliases.csv` | hand-curated | former names, spelling variants; `evidence` column says why |
| `district_lineage.csv` | hand-curated | districts split since Census 2001 and their parents |
| `lgd_district_spine.csv` | `notebooks/eda/01_spine.ipynb` | regenerate, don't edit; a test checks it matches |
| `district_name_map.csv` | `notebooks/eda/01_spine.ipynb` | regenerate, don't edit; a test checks it matches |

When dbt arrives, set `column_types` for the census code columns to text in `dbt_project.yml`:
otherwise the seed loader infers integers and drops leading zeros (`'06'`).
