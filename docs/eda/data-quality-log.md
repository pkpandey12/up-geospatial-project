# Data-quality log

Every surprise in the data gets a row: what, where, how it affects the model, what we did.
IDs are permanent; reference them in notebooks, dbt tests and the confidence rating.

Severity: **high** = changes a ranking or breaks a load; **medium** = affects some districts
or needs a proxy; **low** = cosmetic or already handled.

| ID | Found | Source | Districts | Issue | Impact | Action | Severity | Status |
|---|---|---|---|---|---|---|---|---|
| DQ-001 | 2026-11-21 | `lgd` | Mirzapur (170) | `district_name_local` is 9 NUL bytes (`\x00`); probably Hindi in a font with no Unicode map. | PostgreSQL rejects NUL in text, so loading this column as-is would fail in Phase 2. | Spine drops the column; loader in Phase 2 must strip control characters from all text. | medium | handled in EDA 01 |
| DQ-002 | 2026-11-21 | `lgd` | all | "Local language" column holds upper-case English, not Hindi (Amethi, Kasganj in title case). | No Hindi names available from LGD for matching Hindi-language sources. | Add Devanagari aliases to `district_aliases.csv` when a Hindi source appears. | low | open |
| DQ-003 | 2026-11-21 | `lgd` (Census codes) | Amethi, Hapur, Sambhal, Shamli (+ Kasganj for 2001) | Census 2011 code is `000` (4 districts); Census 2001 code blank (5). These districts were created after those censuses. | Census-based variables (population, agriculture, …) have no direct value for them; their area is inside the parent's figures. | `district_lineage.csv` records parents; proxy rule to decide in EDA step 6. | high | open |
| DQ-004 | 2026-11-21 | `lgd` (Census codes) | Etah (138), Kasganj (633) | Etah's Census 2011 code is 201 (2001: 17), out of sequence; Kasganj is 202. | Joining Census 2001 to 2011 by code position would mis-assign Etah. | Always join Census tables via the spine's own code columns, never by position. | medium | handled in spine |
