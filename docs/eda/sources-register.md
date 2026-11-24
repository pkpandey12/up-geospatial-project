# Source register (Phase 1)

*From the PM chat's register (`pm/08-data-sources.md`, 24 Nov 2026), checked in session 2 on
24 Nov 2026. The PM's research isn't redone here: this file records what each link turned
out to be, fills what the PM table left open (exact files, sizes, columns) and maps every
row to a `source_id` (`docs/data-sources.md`) and a download card (`docs/eda/downloads.md`).*

## How the links were checked

| Host type | Result from the cloud session |
| --- | --- |
| India Data Portal, NASA POWER, Wikidata, CEDA | **Reached** once allowed in this repo's cloud environment (`up-geospatial-project`, created this session). Loaded: APY, NASA POWER, Wikidata. CEDA: the data download needs an email-OTP login, so it stays manual |
| `.gov.in`, `sansad.in`, `cornell.edu`, `dataful.in`, `cseindia.org`, news sites | **Not reachable** (blocked by the session's network policy and permission rules). These links are **not verified**: each card asks Sage to confirm the link as he downloads, and says what to do if it has moved |

Verification column: ✅ opened and matched the PM's description · ⚠ opened but differs (see
note) · ⏳ not reachable from the session; verify on download.

## Ethanol

| # | source_id | Need | Link (PM) | Check | Exact file(s), size, columns (what's now known) | Card |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | `apy_idp` | Crop production: cane, rice, maize (+ wheat) | [IDP APY resource](https://ckandev.indiadataportal.com/dataset/area-production-yield-apy/resource/f980409d-49a2-42ae-9eb0-182365005c04) | ⚠ **better than listed** | The dataset has **two** resources. *DES* `crop-wise-area-production-yield.csv`, 56.2 MB, 455,359 rows (UP: 56,511), 1997-98 to 2022-23, columns `year, state_name, state_code, district_name, district_code, crop_name, crop_code, crop_type, season, area, area_unit, production, production_unit, yield, yield_unit`. *UPAG* `cropwise-area-production-yield-upag.csv`, 16.9 MB, 156,189 rows (UP: 19,208), **2013-14 to 2024-25**, updated 12 Oct 2026, columns `year, state_name, state_code, district_name, district_code, season, crop_category, crop_name, crop_code, area, production, yield` (ha, t, kg/ha). `district_code` **is the LGD code** (checked for all 75). The CSV links redirect to a Wasabi S3 host; the CKAN datastore API on the same site serves the rows. Licence ODC-By 1.0 | Loaded: EDA 10 |
| E1b | `apy_des` | Official DES APY (2024-25 check) | [DES APY report](https://data.desagri.gov.in/website/crops-apy-report-web) | ⏳ | IDP lists this page (and [UPAg's district report](https://upag.gov.in/dash-reports/desdistrictwisecompletedatasetreport?rtab=Area%2C+Production+%26+Yield&rtype=reports)) as its extraction pages. Only needed if UPAG 2024-25 looks wrong (DQ-006) | D-E1b (optional) |
| E2 | `sansad_cane` | Cane yield cross-check; mills with district | [LS Q 324, Annex I](https://eparlib.sansad.in/bitstream/123456789/3015866/1/AU324_dfOACC.pdf) | ⏳ | **Moves up**: UPAG/DES cane covers only 45 districts from 2020-21 (DQ-007); this annexure has yields for 75 | D-E2 |
| E3 | `icrisat_dld` | Long-run history | [TCI data](https://tci.cornell.edu/data) | ⏳ | **Moves down**: DES on IDP already goes back to 1997-98 with LGD codes, enough for 10+ year consistency | D-E3 (low) |
| E4 | `sugar_mills` | Mills: district, TCD, crushing, recovery, molasses | Cane dept site; annual reports; LS Q 324 Annex II | ⏳ | No single official table (PM). Follow **S-1 (b)**: state recovery and quality factor 1.0 now | D-E4 |
| E5 | `dfpd_distilleries` | Distilleries and capacity | [DFPD annexure](https://dfpd.gov.in/WriteReadData/Other/annexure-dir-sug-I.pdf); [Dataful 24160](https://dataful.in/datasets/24160/) | ⏳ | — | D-E5 |
| E6 | `cgwb_gw` | Groundwater block categories | [CGWB publication 1534](https://cgwb.gov.in/cgwbpnm/publication-detail/1534); [2024 fact sheet](https://www.cgwb.gov.in/cgwbpnm/public/uploads/documents/1742294844551285154file.pdf); [INGRES](https://ingres.iith.ac.in/) for 2025 | ⏳ | S-3: 2025 if INGRES exports it, else 2024 | D-E6 |
| E7a | `igrs_circle_rates` | Circle rates | igrsup.gov.in/igrsup/getUploadedRateList | ⏳ | S-2 (a): hand-collect 10–15 districts | D-E7a |
| E7b | `industrial_land` | Industrial park rates | [UPEIDA EOI brochure](https://invest.up.gov.in/wp-content/uploads/2025/07/UPEIDA-16x25-1.pdf); UPSIDA site | ⏳ | — | D-E7b |
| E8 | `wikidata_hq`, `nasa_power` | Climate and solar at district HQ | [NASA POWER](https://power.larc.nasa.gov/llms.txt); Wikidata Query Service | ✅ | Wikidata finds all 75 districts **by LGD code** (property P12746), no name matching. **Amethi's HQ is linked to the wrong item** (a Gauriganj outside UP) and Siddharthnagar's HQ has no coordinates: both fall back to the district item's point (DQ-008). NASA POWER daily point API, no key, ~1 s per point; 75 CSVs, 2001–2025, 6 parameters, 31 MB | Loaded: EDA 11 |
| E9a | `cane_sap` | Cane SAP (constant) | [Tribune](https://www.tribuneindia.com/news/business/up-hikes-rs-30-per-quintal-sugarcane-prices-for-2025-26-season) | ⏳ | ₹400/q early, ₹390/q common (2025-26, per PM). 2026-27 not announced. Typed into the profile with its source | none (constant) |
| E9b | `agmarknet_ceda` | Grain prices (maize, rice) | [CEDA README](https://agmarknet.ceda.ashoka.edu.in/README.html) | ⚠ **moved** | The README URL returns **404**; the portal is at [agmarknet.ceda.ashoka.edu.in](https://agmarknet.ceda.ashoka.edu.in/). Commodity ids: Wheat 1, Paddy(Dhan)(Common) 2, Rice 3, **Maize 4**, Broken Rice 293, Sugarcane 150, Gur 74. Districts use **Census 2011 ids** (71 for UP; Amethi, Hapur, Sambhal, Shamli absent): map via `spine.census_2011_code`. "Download Data" needs an **email OTP login** | D-E9b |
| E9c | `fci_rice_price` | FCI OMSS rice price for distilleries (constant) | *new* | — | Grain ethanol from FCI rice is priced nationally, not by district: a constant like the SAP. Source: DFPD / PIB press release for ESY 2026-27 | none (constant) |
| E10 | `uperc_tariff` | Power tariff (constant) | [summary](https://powerpeakdigest.com/?p=60944); [PVVNL](https://pvvnl.org/public/en/20/53/Tariff-Order) | ⏳ | HV-2 ₹7.97/unit (per PM). A constant; the PDF is only for the citation | D-E10 (low) |
| E11 | `sansad_odop` | ODOP (reference) | [LS Q 493 Annex II](https://eparlib.sansad.in/bitstream/123456789/3002968/1/AU493_IWvd2Q.pdf) | ⏳ | — | D-E11 (low) |
| E12 | `lgd`, `lgd_ogd` | LGD spine | Loaded; Dataful 21838; data.gov.in API | ✅ (local) | Loaded 21 Nov. Phase 2 source: data.gov.in API (`lgd_ogd`) | none |

## CBG

| # | source_id | Need | Link (PM) | Check | Notes | Card |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | `livestock_census` | Dung (cattle, buffalo) | [AIKosh 20th census UP](https://aikosh.indiaai.gov.in/home/datasets/details/uttar_pradesh_district_wise_livestock_population_details_20th_livestock_census_2019.html); [DAHD stats](https://dahd.gov.in/schemes/programmes/animal-husbandry-statistics) | ⏳ | 2019 is 7 years old: it fails the "≤ 3 years" rule unless the age is shown. Check DAHD for 21st census results first | D-C1 |
| C2 | `residue_ratios` | Residue-to-crop ratios | [MNRE/ASCI study](https://samarth.powermin.gov.in/content/policies/8233f67e-8817-4a95-813b-abda2b3052fa.pdf); IIT Bombay (J. Env. Mgmt 341, 118055, 2023) | ⏳ | Ratios are a handful of numbers per crop: they go into `cbg.yaml` with a citation, not into a district table | D-C2 |
| C3 | `cbg_plants` | Existing CBG plants | [GOBARdhan list](https://gobardhan.sbm.gov.in/plants-list); [CSE report](https://cseindia.org/content/downloadreports/12120) | ⏳ | — | D-C3 |
| C4 | (derived) | Press mud | from `sugar_mills` × ratio | — | Depends on E4; state total 3.78 Mt (CSE) as a check | none |

## Corrections to the PM register

1. **E1:** two resources, not one; the UPAG resource runs to **2024-25** (not 2023) and was
   updated 12 Oct 2026. The DES resource's own metadata says data last updated 14 Dec 2023,
   retrieved 26 Feb 2026, not "updated 2 Mar 2026" (that's the resource's creation date).
2. **E1, new finding:** sugarcane is reported for only **45 districts from 2020-21**, with a
   jump in state area and production the same year (DQ-007). E2 moves up as the fix.
3. **E9b:** `README.html` is a dead link (404); the download needs a login; districts are
   Census-2011-coded (71).
4. **E8:** Wikidata has an LGD District Code property (P12746): join by code, not by name.
5. **Grain ethanol:** add the FCI rice price for distilleries as a statewide constant (E9c).

## Poor sources: consider buying

| Source | Why it's poor | Commercial / alternative | Likely cost | Licence to expect |
| --- | --- | --- | --- | --- |
| Sugar mills (E4) | No official mill-wise table with district, TCD, crushing, recovery and molasses | (1) **ChiniMandi** mill database / reports; (2) **ISMA** (Indian Sugar & Bio-Energy Manufacturers Association) yearbook / member data; (3) build by hand from the cane department's mill list + listed companies' annual reports (PM's option a) | Not published: quote needed (directory/subscription products) | Typically internal use only, no redistribution: fine for the private analysis, not for a public repo |
| Distilleries / ethanol capacity (E5) | Only 2018–22 approvals and state totals | (1) **Dataful** (free tier has the DFPD list; paid "Custom" for more); (2) OMC ethanol tender allocation lists (IOCL/BPCL/HPCL EOI results, free PDFs; capacity by plant); (3) GEMA / ISMA member lists | Dataful free / custom on request; OMC lists free | Dataful: commercial use not stated (ask); OMC PDFs: public documents |
| Circle rates (E7a) | ~350 sub-registrar PDFs behind a captcha | **Landeed**, **2bigha.ai** (locality-level circle rates); market prices: PropEquity, Square Yards | Quote needed (PM: "ask for a quote if circle rates go ahead") | Usually licensed for internal use; check redistribution |
| Existing CBG plants (C3) | GOBARdhan lists biogas, not CBG; CSE locations partial | SATAT LoI/commissioning lists (MoPNG/OMCs, free); industry trackers from consultancies | SATAT free; trackers quote needed | Public / commercial terms vary |
| Livestock (C1), if the 21st census isn't out | 2019 data, 7 years old | None better at district level; show the age | — | — |
