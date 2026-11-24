# Download cards (Phase 1)

*Session 2, 24 Nov 2026. One card per source Sage downloads by hand (government sites can't
be reached from the cloud session). Sources the session could reach are already loaded and
have no card: `apy_idp` (EDA 10), `wikidata_hq` and `nasa_power` (EDA 11). Source details and
link checks: `docs/eda/sources-register.md`. Licences: `docs/data-sources.md`.*

**The government links on these cards could not be opened from the cloud session.** They come
from the PM's register (opened on 24 Nov by the PM chat). Confirm each one as you download;
if a page has moved, follow the card's *If it moved* line and note the new URL in `NOTES`.

## Checklist (ethanol first)

Tick as you go. "Size" is an estimate unless marked ✓.

| ✓ | Priority | Card | source_id | What to get | Format, size (est.) | Why now |
|---|---|---|---|---|---|---|
| ☐ | 1 | [D-E6](#d-e6-groundwater-block-categories-cgwb) | `cgwb_gw` | UP groundwater assessment, block table (2025 via INGRES, else 2024 PDF) | XLSX/CSV <1 MB, or PDF 5–30 MB | Ethanol's water filter |
| ☐ | 2 | [D-E2](#d-e2-lok-sabha-q-324-cane-yield-and-mills) | `sansad_cane` | LS Q 324 (2 Dec 2025) PDF with Annex I and II | PDF ~1 MB | Fills the 2020+ cane gap (30 districts) |
| ☐ | 3 | [D-E9b](#d-e9b-mandi-prices-for-maize-and-rice-ceda-agmarknet) | `agmarknet_ceda` | Monthly maize, paddy, rice, broken rice prices, UP, all districts | CSV 1–10 MB per commodity | Grain ethanol inputs (S-4) |
| ☐ | 4 | [D-E5](#d-e5-distilleries-and-ethanol-capacity) | `dfpd_distilleries` | DFPD approved-projects annexure (+ Dataful CSV if easy) | PDF 1–3 MB | Existing feedstock use |
| ☐ | 5 | [D-E7b](#d-e7b-industrial-area-rates-upeida-upsida) | `industrial_land` | UPEIDA EOI brochure; any UPSIDA rate list | PDF 2–10 MB | Land: the cheap-land alternative |
| ☐ | 6 | [D-E7a](#d-e7a-circle-rates-sample-of-1015-districts) | `igrs_circle_rates` | Circle-rate PDFs for 10–15 districts (S-2) | PDF 0.5–5 MB each | Land: rural ₹/sq m |
| ☐ | 7 | [D-E4](#d-e4-sugar-mills-list-for-later-s-1) | `sugar_mills` | Cane department's mill list (if it exists as a table) | PDF/HTML <2 MB | S-1 (a) later; quick look only |
| ☐ | 8 | [D-C1](#d-c1-livestock-census) | `livestock_census` | 20th census UP district table (or 21st if out) | CSV/XLSX <1 MB | CBG dung |
| ☐ | 9 | [D-C2](#d-c2-residue-to-crop-ratios) | `residue_ratios` | MNRE/ASCI biomass study PDF | PDF 2–10 MB | CBG residue ratios |
| ☐ | 10 | [D-C3](#d-c3-existing-cbg-plants) | `cbg_plants` | GOBARdhan plant list export (UP); CSE UP report | CSV <1 MB; PDF 2–5 MB | CBG existing use |
| ☐ | 11 | [D-E10](#d-e10-tariff-order-citation-only) | `uperc_tariff` | UPERC FY 2026-27 tariff order PDF | PDF 5–20 MB | Citation for a constant |
| ☐ | 12 | [D-E11](#d-e11-odop-reference) | `sansad_odop` | LS Q 493 (28 Nov 2024) PDF | PDF ~1 MB | Reference check |
| ☐ | 13 | [D-E1b](#d-e1b-des-apy-official-optional) | `apy_des` | DES APY UP export for 2024-25 | XLSX/CSV 1–5 MB | Only if DQ-006 needs it |
| ☐ | 14 | [D-E3](#d-e3-icrisat-district-level-database-low) | `icrisat_dld` | ICRISAT-TCI apportioned crop file | CSV/XLSX 5–50 MB | History only; skip unless needed |

**About 1–2 hours** for priorities 1–6 if the sites behave; circle rates are the slow one.

## How every card works

1. Download into any folder (e.g. `~/Downloads`). Don't rename or edit the file.
2. From the repo root:
   ```bash
   make register SRC=<source_id> FILE=~/Downloads/<file> URL="<page or file URL>" NOTES="<filters chosen, years, anything odd>"
   ```
   It copies the file into `data/raw/<source_id>/ingest_date=<today>/`, records sha256, size,
   URL, time and licence in `data/raw/<source_id>/_manifest.jsonl`, and refuses a source
   that isn't in `docs/data-sources.md`.
3. Something odd (captcha, missing years, a different file than described)? Put it in
   `NOTES` and add a row to `docs/eda/data-quality-log.md`.

---

## Ethanol

### D-E6. Groundwater block categories (CGWB)

| | |
|---|---|
| **What** | Each assessment unit (block) in UP classified Safe / Semi-critical / Critical / Over-exploited (and Saline) by stage of groundwater extraction |
| **Publisher** | Central Ground Water Board (CGWB), Ministry of Jal Shakti |
| **Grain → district** | Block, **listed under its district** in the tables: no map needed. Output: share of over-exploited + critical blocks per district |
| **Years / cadence** | 2024 report in hand; 2025 assessment complete (PIB, 29 Jan 2026). Assessed every year recently |
| **Licence** | ⚠ Not stated |
| **Coverage** | 836 units under 75 districts expected. Watch for district names from older boundaries |
| **Quality** | Block counts weight a tiny block like a large one; urban units may be listed separately; categories are about extraction, not water quality |
| **Alternative** | INGRES (free) is itself the better format |

**Get it (S-3: 2025 if available, else 2024).**
1. **Try 2025 first** at https://ingres.iith.ac.in/ → *Assessment* / *Reports* → State: Uttar
   Pradesh, Year: 2025 (or "2024-25"), level: Block / Assessment Unit → export to Excel/CSV.
   Want: district, block, stage of extraction (%), category.
2. Else 2024: https://cgwb.gov.in/cgwbpnm/publication-detail/1534 → download the UP report
   PDF. The block table is an annexure (district → block → category). Also take the fact
   sheet: https://www.cgwb.gov.in/cgwbpnm/public/uploads/documents/1742294844551285154file.pdf
3. Register (one call per file):
   ```bash
   make register SRC=cgwb_gw FILE=~/Downloads/<file> URL="<url>" NOTES="2025 INGRES export, block level"
   ```
- **If it moved:** search cgwb.gov.in for "Dynamic Ground Water Resources Uttar Pradesh";
  the national report ("Dynamic Ground Water Resources of India 2024/2025") also has a
  block annexure for every state.
- **Next:** a PDF annexure means a PDF-table parser with a fixture test (a Sage TODO).

### D-E2. Lok Sabha Q 324: cane yield and mills

| | |
|---|---|
| **What** | Unstarred Question 324 (2 Dec 2025). Annex I: district-wise sugarcane yield (kg/ha), 2012-13 to 2023-24. Annex II: 26 mills with their districts |
| **Publisher** | Lok Sabha Secretariat (answer by the Ministry of Agriculture) |
| **Grain → district** | District name → LGD via `map_to_lgd`; mill → its district |
| **Years / cadence** | 2012-13 to 2023-24, gaps in recent years (PM); one-off |
| **Licence** | ⚠ Not stated (public parliamentary record) |
| **Coverage** | 75 districts expected in Annex I |
| **Quality** | Yields only (not production); recent-year gaps; names may use old spellings |
| **Alternative** | Cane department district reports, if found (D-E4) |

**Get it.**
1. https://eparlib.sansad.in/bitstream/123456789/3015866/1/AU324_dfOACC.pdf
2. `make register SRC=sansad_cane FILE=~/Downloads/AU324_dfOACC.pdf URL="https://eparlib.sansad.in/bitstream/123456789/3015866/1/AU324_dfOACC.pdf"`
- **If it moved:** https://sansad.in/ls/questions → search "sugarcane" with date 02.12.2025,
  question 324; or eparlib's search for "AU324".

### D-E9b. Mandi prices for maize and rice (CEDA Agmarknet)

| | |
|---|---|
| **What** | Agmarknet modal / min / max prices and arrivals by market, cleaned by CEDA (Ashoka University) |
| **Publisher** | DMI, Ministry of Agriculture; mirror by CEDA |
| **Grain → district** | Market → **Census 2011 district id** (71 UP districts). Map with `spine.census_2011_code`; Amethi, Hapur, Sambhal, Shamli have no id (use the parent via `district_lineage.csv`) |
| **Years / cadence** | 2001 onward, refreshed monthly |
| **Licence** | ⚠ Unknown: read https://ceda.ashoka.edu.in/republish-policy/ when you log in; record what it says |
| **Coverage** | Only districts with reporting mandis for each crop |
| **Quality** | Arrivals are partial; maize is traded mostly in the west; FCI procurement isn't in mandi prices |
| **Alternative** | agmarknet.gov.in directly (same data, harder to export) |

**Get it.** The old `README.html` link is dead (404): use the portal.
1. https://agmarknet.ceda.ashoka.edu.in/ → *Data Portal* → Commodity: **Maize** (id 4) →
   State: Uttar Pradesh → Districts: All → Calculation: **Monthly** → Start 01/01/2015,
   End: latest → *Download Data*. It asks for your email and an OTP.
2. Repeat for **Paddy(Dhan)(Common)** (2), **Rice** (3), **Broken Rice** (293), **Wheat** (1).
3. One register call per file:
   ```bash
   make register SRC=agmarknet_ceda FILE=~/Downloads/<file>.csv URL="https://agmarknet.ceda.ashoka.edu.in/" NOTES="Maize, UP, all districts, monthly, 2015-01 to 2026-10"
   ```
- **If it moved:** https://ceda.ashoka.edu.in/ → Data → Agri-market data.

### D-E5. Distilleries and ethanol capacity

| | |
|---|---|
| **What** | DFPD's list of ethanol projects approved for interest subvention 2018–22: unit name (often with district), feedstock, capacity (KLPD) |
| **Publisher** | Department of Food & Public Distribution |
| **Grain → district** | Plant → district (from the unit name/address; some need a lookup) |
| **Years** | Approvals 2018–22; state has 97 distilleries (Oct 2025) |
| **Licence** | ⚠ Not stated (DFPD); Dataful: free account, commercial terms not stated |
| **Coverage** | Approved projects only, not all installed capacity |
| **Quality** | Approved ≠ built; molasses vs grain capacity mixed; no 2023+ approvals |
| **Alternative** | OMC ethanol tender allocation lists (plant-wise, free); Dataful structured copy |

**Get it.**
1. https://dfpd.gov.in/WriteReadData/Other/annexure-dir-sug-I.pdf
2. Optional: https://dataful.in/datasets/24160/ (free account) → CSV.
3. `make register SRC=dfpd_distilleries FILE=~/Downloads/annexure-dir-sug-I.pdf URL="https://dfpd.gov.in/WriteReadData/Other/annexure-dir-sug-I.pdf"`
- **If it moved:** dfpd.gov.in → Sugar → Ethanol / Interest subvention scheme lists.
- **Lead:** IOCL/BPCL/HPCL "ethanol EOI allocation" PDFs for ESY 2025-26 or 2026-27 list
  allocated quantity by plant and feedstock. Download one if you find it (same source_id,
  `NOTES="OMC allocation list"`).

### D-E7b. Industrial-area rates (UPEIDA, UPSIDA)

| | |
|---|---|
| **What** | Tentative allotment rates (₹/sq m) in government industrial parks |
| **Publisher** | UPEIDA (expressway nodes), UPSIDA (industrial areas) |
| **Grain → district** | Park/node → district |
| **Years** | 2025 |
| **Licence** | ⚠ Not stated |
| **Coverage** | A handful of districts (e.g. Jhansi ₹529, Meerut ₹9,760 per PM) |
| **Quality** | Tentative EOI rates; plots come with infrastructure, so not comparable 1:1 with farmland |
| **Alternative** | — (it is the official rate) |

**Get it.**
1. https://invest.up.gov.in/wp-content/uploads/2025/07/UPEIDA-16x25-1.pdf
2. UPSIDA: https://www.upsida.co.in/ → look for *Land Bank* / *Rate list* / *Allotment*
   (PDF or table). Save what exists.
3. `make register SRC=industrial_land FILE=~/Downloads/UPEIDA-16x25-1.pdf URL="https://invest.up.gov.in/wp-content/uploads/2025/07/UPEIDA-16x25-1.pdf"`
- **If it moved:** invest.up.gov.in → Land bank / UPEIDA; Nivesh Mitra land bank.

### D-E7a. Circle rates: sample of 10–15 districts

| | |
|---|---|
| **What** | DM circle rates (*mulyankan suchi*): the minimum value for stamp duty, per sub-registrar area, agricultural and non-agricultural |
| **Publisher** | Stamps & Registration Department, UP (IGRS UP) |
| **Grain → district** | Sub-registrar office → its district (known from the selection you make) |
| **Years** | Revised per district at different dates; note each PDF's effective date |
| **Licence** | ⚠ Not stated |
| **Coverage** | S-2 (a): 10–15 districts only |
| **Quality** | Below market by unknown, varying amounts; Hindi PDFs, many layouts; units vary (₹/hectare for farmland, ₹/sq m for plots) |
| **Alternative** | Landeed / 2bigha.ai quote (S-2 b) |

**Which districts.** Manvendra's districts first (his deal prices due 15 Dec are the
calibration), then a spread: Lakhimpur Kheri, Sitapur, Bareilly, Shahjahanpur,
Muzaffarnagar, Saharanpur (cane belt); Gorakhpur, Kushinagar (east); Jhansi, Lalitpur
(Bundelkhand, cheap land); Lucknow, Kanpur Nagar (urban check). In each district, one
**rural** sub-registrar office (tehsil HQ outside the city) and the **city** office.

**Get it.**
1. https://igrsup.gov.in/igrsup/getUploadedRateList → District → Sub-registrar office →
   captcha → PDF.
2. Name nothing; register each with the office in `NOTES`:
   ```bash
   make register SRC=igrs_circle_rates FILE=~/Downloads/<file>.pdf URL="https://igrsup.gov.in/igrsup/getUploadedRateList" NOTES="Kheri / Mohammadi SRO, effective 2025-08-01, rural"
   ```
- **If it moved:** igrsup.gov.in → *Circle Rate* / *Mulyankan Suchi*; some districts post
  them on `<district>.nic.in`.
- **Next:** a PDF-table parser (`parse_circle_rate_pdf`, Sage's TODO; the brief's example).

### D-E4. Sugar mills list (for later, S-1)

| | |
|---|---|
| **What** | UP's ~122 operating sugar mills with district, crushing capacity (TCD), cane crushed, recovery %, molasses |
| **Publisher** | UP Cane Development Department / Sugar Commissioner; mill annual reports |
| **Grain → district** | Mill → its district |
| **Years** | 2024-25 season (122 mills) |
| **Licence** | ⚠ Varies by document |
| **Coverage** | No single official table found (PM). S-1 (b): state-level recovery, quality factor 1.0 for Phase 1 |
| **Quality** | Recovery varies by mill and season; molasses split B/C-heavy rarely published |
| **Alternative** | ChiniMandi / ISMA directories (quote); listed companies' annual reports (Balrampur, Triveni, Dhampur, DCM Shriram, Bajaj Hindusthan …) |

**Get it (10 minutes, look only).** https://upcane.gov.in/ (or caneup.in) → look for
*Mill-wise crushing / recovery* or a *Sugar mills list*. If there's a table or PDF,
download it: `make register SRC=sugar_mills FILE=... URL="..."`. If not, note what you saw
in the data-quality log; the hand-built list is session 3+.

### D-E10. Tariff order (citation only)

HV-2 average billing rate ₹7.97/unit, FY 2026-27 (PM). Only the PDF for the citation:
https://pvvnl.org/public/en/20/53/Tariff-Order → FY 2026-27 order.
`make register SRC=uperc_tariff FILE=... URL="https://pvvnl.org/public/en/20/53/Tariff-Order"`.
If moved: uperc.org → Tariff orders. **Licence:** public regulatory order.

### D-E11. ODOP (reference)

https://eparlib.sansad.in/bitstream/123456789/3002968/1/AU493_IWvd2Q.pdf (Annex II: food ODOP
for the 75 districts). `make register SRC=sansad_odop FILE=... URL="..."`. If moved:
sansad.in question search, 28.11.2024, Q 493; or odopup.in.

### D-E1b. DES APY official (optional)

Only if DQ-006 (UPAG 2024-25 looks different) needs an official check.
https://data.desagri.gov.in/website/crops-apy-report-web → State: Uttar Pradesh, Crops:
Sugarcane, Rice, Maize, Wheat, Years: 2022-23 to 2024-25, district level → Excel.
`make register SRC=apy_des FILE=... URL="..."`.

### D-E3. ICRISAT District Level Database (low)

Skip unless the EDA needs pre-1997 history: DES on India Data Portal already gives 1997-98
onward with LGD codes. https://tci.cornell.edu/data → ICRISAT-TCI DLD → apportioned crop
area/production (registration may be required; record the terms you accept in `NOTES`).

---

## CBG (download with the ethanol files)

### D-C1. Livestock census

| | |
|---|---|
| **What** | District-wise livestock population (cattle, buffalo; dung is estimated from head counts) |
| **Publisher** | DAHD; UP table on AIKosh |
| **Grain → district** | District name → LGD |
| **Years** | 20th census, 2019. 21st (counted Oct 2024 – mid-2025): check whether results are out |
| **Licence** | ⚠ PM says OGL-India; confirm on the page |
| **Coverage** | 2019 has 75 districts |
| **Quality** | 7 years old (fails the ≤ 3-year rule unless the age is shown); stray cattle not on farms |
| **Alternative** | None better at district level |

**Get it.** First https://dahd.gov.in/schemes/programmes/animal-husbandry-statistics → is
there a *21st Livestock Census* district table? If yes, take it. Else:
https://aikosh.indiaai.gov.in/home/datasets/details/uttar_pradesh_district_wise_livestock_population_details_20th_livestock_census_2019.html
→ download (login may be needed). `make register SRC=livestock_census FILE=... URL="..." NOTES="20th census 2019"`.

### D-C2. Residue-to-crop ratios

https://samarth.powermin.gov.in/content/policies/8233f67e-8817-4a95-813b-abda2b3052fa.pdf
(MNRE/ASCI biomass power evaluation study). `make register SRC=residue_ratios FILE=... URL="..."`.
Also note the IIT Bombay paper's DOI (J. Environmental Management 341, 118055, 2023) in the
CBG profile; download the PDF only if open access. **Use:** ratios for paddy straw, wheat
straw, maize stalks/cobs, cane trash/tops, and surplus fractions → `cbg.yaml` with
`source:` and `confidence:`.

### D-C3. Existing CBG plants

1. https://gobardhan.sbm.gov.in/plants-list → State: Uttar Pradesh → export (CSV/Excel) if
   offered; else save the page as PDF. It covers biogas plants; note whether CBG appears.
2. https://cseindia.org/content/downloadreports/12120 (CSE, CBG landscape in UP, Mar 2024).
3. `make register SRC=cbg_plants FILE=... URL="..."` per file.
- **Alternative:** SATAT LoI / commissioned-plant lists (satat.co.in or MoPNG), free.
