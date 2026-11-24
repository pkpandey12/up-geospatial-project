# Data sources

One row per source. A source must be listed here **before** a notebook uses it (notebook 02
checks) and before a file can be registered (`make register` copies the licence from the
row below). `source_id` is the folder name under `data/raw/` and the prefix of its dbt
models later.

Licence column: the licence's name **and** where you read it. "Unknown" is allowed while
exploring, but it is flagged ⚠ and a source can't be *kept* for the model (EDA step 6)
until it's resolved, because the repo may go public and the tool may be used commercially.

Details per source (file names, columns, coverage, alternatives): `docs/eda/sources-register.md`.
How to download each one: `docs/eda/downloads.md`.

## In use or planned (Phase 1)

| source_id | Name | Publisher | URL | Format | Grain → district | Period | Licence (and where stated) | Status |
|---|---|---|---|---|---|---|---|---|
| `lgd` | Local Government Directory: Districts of Uttar Pradesh | Ministry of Panchayati Raj, GoI | https://lgdirectory.gov.in/ (Download Directory → Districts of a State) | PDF | District; **LGD district code** (the project's key) | Snapshot 2026-11-21 | **GODL-India** (Government Open Data License – India): LGD is published on data.gov.in under NDSAP; redistribution allowed with attribution. Attribution below. | In use (EDA 01) |
| `apy_idp` | Crop-wise Area, Production & Yield, two resources: DES (1997-98 to 2022-23) and UPAG (2013-14 to 2024-25) | India Data Portal (ISB), from DES / UPAg, MoA&FW | https://ckandev.indiadataportal.com/dataset/area-production-yield-apy | CKAN datastore API → CSV (UP rows only) | District name + LGD district code | 1997-98 to 2024-25 | **ODC-By 1.0** (Open Data Commons Attribution; CKAN `license_title` of the dataset). Underlying DES/UPAg data: GoI, terms not stated on the mirror | Loaded (EDA 10) |
| `apy_des` | DES crop APY report (official, for a 2024-25 check if UPAG lags) | DES, MoA&FW | https://data.desagri.gov.in/website/crops-apy-report-web | Excel/CSV export | District × season | to 2024-25 (to check) | ⚠ Unknown: not stated (to check on the portal) | Card only (optional) |
| `sansad_cane` | Lok Sabha unstarred Q 324 (2 Dec 2025): district sugarcane yield (Annex I), mills with district (Annex II) | Lok Sabha Secretariat | https://eparlib.sansad.in/bitstream/123456789/3015866/1/AU324_dfOACC.pdf | PDF | District (75); mill → district | 2012-13 to 2023-24 | ⚠ Not stated; a public parliamentary record (check the eparlib terms) | Card |
| `icrisat_dld` | ICRISAT–TCI District Level Database (apportioned) | ICRISAT, Cornell TCI | https://tci.cornell.edu/data | CSV/Excel | District on 1966 boundaries | 1966–2017 | ⚠ "Open access" per PM register; exact terms to read on download | Card (low priority) |
| `sugar_mills` | Sugar mills: district, TCD, crushing, recovery, molasses (hand-built list) | UP Cane Development; company annual reports | https://upcane.gov.in/ (to check); annual reports | PDF / web → hand-built CSV | Mill → district | 2024-25 | ⚠ Varies by document; note per row | Card (S-1: state-level for now) |
| `dfpd_distilleries` | DFPD approved ethanol interest-subvention projects 2018–22 | Dept of Food & Public Distribution | https://dfpd.gov.in/WriteReadData/Other/annexure-dir-sug-I.pdf | PDF | Plant → district (district in unit name) | 2018–22 | ⚠ Not stated | Card |
| `cgwb_gw` | Dynamic Ground Water Resources of UP (block categories) | Central Ground Water Board | https://cgwb.gov.in/cgwbpnm/publication-detail/1534 | PDF (block tables); INGRES export | Block listed under district | 2024 (2025 if found) | ⚠ Not stated | Card |
| `igrs_circle_rates` | Circle rates (*mulyankan suchi*), sample of 10–15 districts | Stamps & Registration Dept, UP (IGRS UP) | https://igrsup.gov.in/igrsup/getUploadedRateList | PDF per sub-registrar office (captcha) | Sub-registrar area → district | Revised per district | ⚠ Not stated | Card (S-2: sample) |
| `industrial_land` | Industrial-area rates: UPEIDA 2025 EOI nodes; UPSIDA plot lists | UPEIDA, UPSIDA | https://invest.up.gov.in/wp-content/uploads/2025/07/UPEIDA-16x25-1.pdf | PDF brochure | Park → district | 2025 | ⚠ Not stated | Card |
| `wikidata_hq` | District headquarters and their coordinates | Wikidata | https://query.wikidata.org/ (SPARQL, P12746 LGD District Code, P36 capital, P625 coordinates) | JSON | LGD district code → HQ point | Live; snapshot 2026-11-24 | **CC0 1.0** (Wikidata structured data, https://www.wikidata.org/wiki/Wikidata:Licensing) | Loaded (EDA 11) |
| `nasa_power` | NASA POWER daily point data at district HQs | NASA Langley Research Center | https://power.larc.nasa.gov/api/temporal/daily/point | CSV per point | HQ point → district | 2015-01-01 to 2024-12-31 | **CC BY 4.0** (stated in https://power.larc.nasa.gov/llms.txt) | Loaded (EDA 11) |
| `fci_rice_price` | FCI rice price for distilleries under OMSS (national constant) for ESY 2026-27 | DFPD / FCI (PIB press releases) | https://pib.gov.in/ (search "rice ethanol OMSS") | Press release | Nation (constant) | ESY 2026-27 | n/a: a published price, typed into the profile with its source | Constant (to find) |
| `cane_sap` | UP state-advised cane price (statewide constant) | UP Govt (press reports) | https://www.tribuneindia.com/news/business/up-hikes-rs-30-per-quintal-sugarcane-prices-for-2025-26-season | News report | State | 2025-26 (2026-27 pending) | n/a: a published price, typed into the profile with its source | Constant |
| `agmarknet_ceda` | Agmarknet mandi prices and arrivals (maize, paddy, rice, broken rice, wheat) | DMI, MoA&FW, via CEDA Ashoka mirror | https://agmarknet.ceda.ashoka.edu.in/ | CSV download (email OTP login) | Market → Census 2011 district id (71 UP districts) | 2001 onward | ⚠ Unknown: CEDA's republish policy (https://ceda.ashoka.edu.in/republish-policy/) to read | Card |
| `uperc_tariff` | UPERC tariff order FY 2026-27 (HV-2) | UPERC; DISCOMs | https://pvvnl.org/public/en/20/53/Tariff-Order | PDF | State | FY 2026-27 | Public regulatory order (no licence stated) | Constant |
| `sansad_odop` | Lok Sabha Q 493 (28 Nov 2024), Annex II: food ODOP by district | Lok Sabha Secretariat | https://eparlib.sansad.in/bitstream/123456789/3002968/1/AU493_IWvd2Q.pdf | PDF | District | 2024 | ⚠ Not stated; public parliamentary record | Card (reference) |
| `livestock_census` | 20th Livestock Census 2019, UP district-wise | DAHD, via AIKosh | https://aikosh.indiaai.gov.in/home/datasets/details/uttar_pradesh_district_wise_livestock_population_details_20th_livestock_census_2019.html | CSV/XLSX | District | 2019 (21st census: check) | ⚠ PM register says OGL-India; confirm on the AIKosh page | Card (CBG) |
| `residue_ratios` | Residue-to-crop ratios (MNRE/ASCI study; IIT Bombay 2023) | MNRE/ASCI; journal article | https://samarth.powermin.gov.in/content/policies/8233f67e-8817-4a95-813b-abda2b3052fa.pdf | PDF | Crop | 2015–18 base | ⚠ Not stated (gov report); journal: publisher terms. Ratios are facts and go into the profile with a citation | Card (CBG) |
| `cbg_plants` | Existing CBG / biogas plants (GOBARdhan list; CSE UP landscape report) | DDWS (GOBARdhan); CSE | https://gobardhan.sbm.gov.in/plants-list | Web table export; PDF | Plant → district | 2024–25 | ⚠ Not stated | Card (CBG) |

## Phase 2 sources (recorded now, not used in Phase 1)

| source_id | Name | Publisher | URL | Format | Grain → district | Period | Licence (and where stated) | Status |
|---|---|---|---|---|---|---|---|---|
| `lgd_ogd` | LGD district list, monthly, with an API (free key) | MoPR via data.gov.in (OGD Platform India) | https://www.data.gov.in/ (search "Local Government Directory district"; API key from your data.gov.in account) | JSON/CSV API | District; LGD code | Monthly | **GODL-India** (data.gov.in, NDSAP) | Phase 2 extractor replaces the manual `lgd` PDF |

## Attribution

Required by the licences above; repeat it wherever the data is redistributed (README of a
public repo, results page, fixture READMEs).

- **LGD** (`lgd`, `lgd_ogd`): "Local Government Directory, Ministry of Panchayati Raj,
  Government of India, published under the Government Open Data License – India (GODL-India)."
  Applies to `tests/fixtures/lgd/` and the seeds in `dbt/seeds/` derived from it.
- **India Data Portal** (`apy_idp`): "Area, Production, Yield (APY), India Data Portal (ISB),
  licensed under the Open Data Commons Attribution License (ODC-By 1.0); original data DES /
  UPAg, Ministry of Agriculture & Farmers Welfare."
- **NASA POWER** (`nasa_power`): "These data were obtained from the NASA Langley Research
  Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program."
  (CC BY 4.0)
- **Wikidata** (`wikidata_hq`): CC0, no attribution required; credited anyway.

## How to download a source (Phase 1 convention)

1. Follow the source's card in `docs/eda/downloads.md`.
2. Register the file: `make register SRC=<source_id> FILE=<path> URL=<url>`. It copies the
   file into `data/raw/<source_id>/ingest_date=<today>/` (never edit files there) and appends
   a line to `data/raw/<source_id>/_manifest.jsonl` (sha256, bytes, URL, time, licence).
3. Note anything odd (captchas, partial years, units) in `NOTES="..."` and the data-quality log.

Learn: `docs/learn/raw-manifest.md`.
