# UP Factory Siting Tool: Design Document

Nov 24, 2026 · @Sage

**Revised 24 Nov 2026** after Sage's call: the MVP is district-level and non-geographic, piloted on ethanol (first) and CBG; costs are shown as ranges; the stack is local first, with AWS and Snowflake in March 2027. Decisions D-28 to D-40 are in the PM project's decision log, which wins where this doc and the log differ.

## Purpose

The tool is an intelligence service for commercial land operators setting up a venture in UP. It tells them which districts to target for a given product, and later where in the district. It informs; it doesn't decide, so buyers and sellers still do their own checks. Newcomers to UP use it to choose where to target and build a network; existing factory owners use it to plan expansion. The first user is Sage's partner Manvendra, who runs CBG and ethanol plants; the cost factors come from his own decision process.

**MVP question (district level, no geography).** For a given product and plant size, which UP districts keep the variable overheads lowest: raw material (volume, quality and consistency), land, water and climate? Labour, machinery and other fixed costs are treated as equal everywhere.

**Step 2 (after the MVP).** Where in the district: first geography (boundaries, road density, land quality), then villages, land parcels, Bhulekh ownership and active cases, and the people to contact. District agents in the network can see operators and pitch to them.

Every recommendation must be explainable: an operator sees which costs drove the ranking and how sure each number is. The MVP is **viable** if it clears two bars: its ranking broadly agrees with Manvendra's own choices (e.g. Lakhimpur Kheri for ethanol, because of its cane), and it beats a naive sort by raw-material volume somewhere that matters. The answers come from exploratory data analysis (EDA) first. Where a public source is poor, the data is bought from an aggregator or supplier rather than cleaned by hand.

## Scope

The MVP ranks UP's 75 districts for one product at a time, at district level and without geography: every source must reach a district through its name or LGD code, not a map. It doesn't pick the product, value land parcels, or quote real prices. Most variables only mean something for a named product: the raw material for an ethanol plant is cane, molasses or grain; for a CBG plant it's crop residue, press mud or dung. So every analysis starts from a **product profile**.

| In the MVP | Not in the MVP |
| --- | --- |
| District-level ranking for a chosen product profile and plant size (TPD) | Choosing which product to make |
| Raw material (volume, quality, consistency, feedstock indicators), land, water and climate | Market access, a distance (geography stage); electricity as a ranker (the tariff is statewide, so it's a constant in the total) |
| Indicative land cost: district averages, urban vs rural | Boundaries, road density and land quality (geography stage); parcels, Bhulekh and contacts (step 2) |
| A ₹/t range, a confidence rating and a rank range per district | Labour, machinery and other fixed costs (treated as equal everywhere); personal factors such as distance from home |
| Pilots: ethanol (first), CBG, and a third from Manvendra | Real-time feeds; all of India |

**Product profile.** For each product, a short config: its raw materials and tonnes of each per tonne of output; electricity (kWh) and water (kL) per tonne, and the water quality it needs; its buyers; the maximum sourcing distance; a TPD range (tonnes of output per day, chosen at run time); operating days per year and project life; and a land rule, plot acres = fixed acres + acres per TPD × TPD. Manvendra's rule for CBG is TPD + 2 acres, so a 3 TPD plant needs about 5 acres. Plots fall into size classes: Micro under 1 acre, Small 1–2, Medium 2–5, Large 5 and over. The EDA fills each profile from public sources, with a source and a confidence rating per field. Manvendra's real plant figures then override them from a private file that never goes into the public repo.

**ODOP as a reference.** UP's One District One Product list names the product each district is meant to specialise in. The pilots no longer come from it (they come from Manvendra's own plants), but it stays a sanity check wherever it covers a pilot's raw material.

## Decision framework

Districts are ranked by an estimated variable overhead in rupees per tonne of output, not by an abstract score, because an operator compares money. Each term is built from the product profile, the chosen plant size and district data. In the MVP, market access waits for the geography stage, and power is the same everywhere, so it sets the level of the total but not the order:

```latex
\text{Overhead}_{d,p,s} = C^{\text{raw}}_{d,p,s} + C^{\text{land}}_{d,p,s} + C^{\text{water}}_{d,p,s} + C^{\text{power}}_{p} \quad (\text{₹ per tonne of output; district } d \text{, product } p \text{, plant size } s)
```

| Term | How it's estimated (first version) |
| --- | --- |
| Raw material | For each input: tonnes needed per tonne of output, divided by a relative quality factor (district quality ÷ reference, e.g. sugar recovery; 1.0 where there's no data), times the input price. Haulage within the district only, until the geography stage |
| Land | Indicative land price (₹/sq m) × plot size from the profile's land rule (1 acre = 4,046.86 sq m), spread over the project life, divided by annual output (TPD × operating days) |
| Water | kL per tonne × (supply cost + treatment cost to reach the product's quality needs) |
| Power | kWh per tonne × the statewide tariff. A constant across districts in the MVP; connection cost and reliability wait for the geography stage |
| Market | Not in the MVP: a distance to buyers, so it comes with the geography stage |

**Hard filters come before the ranking.** Some conditions rule a district out rather than add cost. In the MVP: not enough raw material in the district for the chosen plant size, and, for a water-heavy product, a high share of over-exploited or critical groundwater blocks. The substation filter needs geography and comes later. Filters run first, so the ranking never recommends somewhere that can't work.

**What can't be priced becomes a risk flag, not a weight.** Supply consistency (year-to-year swings in output), climate risks (heat, rainfall variability) and data confidence are shown beside each district rather than folded into the rupee total, so an operator sees the trade-off instead of trusting a hidden weighting.

**Costs are shown as ranges, not points.** The inputs are estimates, so each district gets a ₹/t range, a confidence rating (strong / moderate / weak) and a rank range (e.g. rank 3–6). The range comes from rerunning the model with each major assumption (feedstock price and ratio, land price, water cost, haulage) varied by ±20%. A district that stays near the top across the runs is a robust pick.

**The naive baseline.** Every ranking is compared with a plain sort by raw-material volume. The model earns its keep only where it disagrees for a reason, e.g. a high-cane district with over-exploited groundwater, or a less obvious district with much cheaper land. If it only reproduces the one-column sort, it adds little.

## Variables and the EDA questions

Each interview question becomes a measurable quantity, a data source and an EDA check that decides whether it can be used at district level. In the MVP, every variable must reach the district without a map. Market access and electricity mostly wait for geography (see the notes under 2 and 4), and climate is added as 6. Machinery is out: it costs roughly the same everywhere.

### 1. Raw material

| Interview question | Measure | Candidate data | EDA must answer |
| --- | --- | --- | --- |
| How easy is it to source? | Production within the product's sourcing radius, minus what existing processors already take | District crop production ([DES / UPAg](https://www.india.gov.in/category/agriculture-rural-environment/subcategory/agricultural-produce/details/prices-arrival-reports-agmarknet)); [ICRISAT District Level Database](https://tci.cornell.edu/data) for long history (to 2017); existing mill or plant capacity | Are production figures complete for all 75 districts? Do 2017 and later sources line up? |
| What does it cost? | District modal price by month | [Agmarknet](https://agmarknet.ceda.ashoka.edu.in/README.html) daily mandi prices and arrivals | Does price really vary between districts? Regulated crops (cane has a state-advised price) may show none, which is itself a finding |
| What is its quality? | Product-specific yield factor, e.g. sugar recovery % | Mill-level recovery from the UP cane department and mill annual reports ([example](https://www.trivenigroup.com/Annual-Report-2024-25/pdf/mda/Triveni%20Sugar%20Business_%20Overview.pdf)); Agmark grading for graded produce | Is there a quality measure for each pilot product, and does it vary within UP? |
| How consistently can I source it? | Coefficient of variation of production over 10+ years; trend | Same production series | Which districts are steady, which swing with the monsoon? |
| How close is the source? | Production-weighted road distance from supply to a candidate site | Production by district (later by block); road network from OpenStreetMap | Is district-centroid distance good enough, or does it mislead for large districts? |

The interview's sugarcane example is worth checking in the EDA rather than assuming: UP's sugar department reported [9.5% recovery for 2024–25](https://organiser.org/2026/01/03/333320/bharat/uttar-pradesh-emerges-as-indias-sugar-leader-surpasses-maharashtra-in-the-current-season/), above the national average that season. Quality figures move year to year, so the tool uses recent multi-year averages.

**On the suggested QCI data:** no public, district-level QCI dataset on raw-material quality turned up. QCI's agricultural work is third-party assessment for specific buyers (e.g. [pulses and oilseeds for NAFED](https://ppid.qcin.org/?p=9394)). Treat it as an open question for the partners, and use product-specific proxies meanwhile.

**Feedstock for the pilots (24 Nov).** Feedstock is an indication derived from agricultural output, which users verify on the ground. For ethanol: cane, rice and maize production, and molasses from sugar mill crushing. For CBG: crop production × published residue-to-crop ratios, press mud from sugar mills, and dung from district livestock figures. Both subtract what existing distilleries and CBG plants already use. Distances to supply wait for the geography stage; in the MVP, supply is counted within the district.

### 2. Market availability

| Interview question | Measure | Candidate data | EDA must answer |
| --- | --- | --- | --- |
| How close am I to a buyer? | Road distance and travel time to the main demand centres for the product | City populations (Census); OpenStreetMap roads with a routing engine (e.g. OSRM) | Which demand centres matter for each product (local mandis, Delhi NCR, export)? |
| Where's the best price? | Output price by market, net of haulage | Agmarknet for agricultural outputs; trade price reports for others | For which pilot products do output prices exist at market level at all? |
| Am I near the right infrastructure? | Distance to the nearest expressway access, dedicated freight corridor station, dry port and airport | UP logistics material lists dry ports at [Dadri, Agra, Mirzapur, Moradabad and Kanpur](https://invest.up.gov.in/wp-content/uploads/2024/07/Investment-Opportunities-Logistics-warehousing_240724.pdf); OpenStreetMap; UPEIDA expressway maps | Can the infrastructure points be geocoded reliably? New ones open often, so the list needs a date |

**Deferred to the geography stage (24 Nov).** Market access is a distance to buyers, ports and infrastructure, so it leaves the MVP. Output prices by market may still be explored where they exist.

### 3. Land

| Interview question | Measure | Candidate data | EDA must answer |
| --- | --- | --- | --- |
| What does land cost here? | Indicative ₹ per sq m, urban vs rural, per district | DM circle rates on [IGRS UP](https://housing.com/news/circle-rates-in-uttar-pradesh/amp/) (per sub-registrar office); allotment rates in government industrial areas, e.g. [₹10,850/sq m at Trans Ganga City, Unnao](https://www.scribd.com/document/641078911/investorguide) and [₹1,914/sq m in a Lalitpur park](https://www.magzter.com/hi/stories/newspaper/Capital-Information/STATEOFTHEART-PARK-IN-LALITPUR-TO-BOOST-PHARMA-SECTOR-IN-UP) | Can circle rates be collected at scale (they sit behind captchas and in PDFs)? How far do circle rates sit below market prices? Ask the land partner for real deal prices in 3–5 districts as a check |

Circle rates are a legal minimum for stamp duty, not a market price, so they rank districts but don't price a deal. Ready industrial plots are a separate, often cheaper option with infrastructure included; the tool should show both.

Road density is a useful land-price proxy: in Manvendra's experience, lower road density usually means cheaper land. It comes with the geography stage. Manvendra's real deal prices in 3–5 districts are the check on circle rates.

### 4. Electricity

| Interview question | Measure | Candidate data | EDA must answer |
| --- | --- | --- | --- |
| Is there enough supply? | Hours of supply and outage frequency by area | UPPCL and DISCOM reports; data access unclear | Is any reliability data public at district level? |
| Is the infrastructure there? | Distance to the nearest 132 kV or 220 kV substation and its spare capacity | CEA monthly lists of commissioned substations (e.g. [FY 2026–27 to July](https://cea.nic.in/wp-content/uploads/transmission/2026/07/SS_Commissioned_during_FY_2026_27_till_July__2026.pdf)); OpenStreetMap power lines | Can a full substation list with locations be built? Spare capacity is probably not public |
| How much does solar save? | Annual solar yield (kWh per kWp) × the grid tariff it replaces, minus system cost | Irradiance from [NASA POWER](https://power.larc.nasa.gov/llms.txt) (free API) or the Global Solar Atlas; tariff from UPERC orders, where the approved average billing rate for large and heavy power (HV-2) is [₹7.97 per unit](https://powerpeakdigest.com/?p=60944) | How much does irradiance actually vary across UP? |

The grid tariff is set for the whole state, so in the MVP power is a constant in the cost total and doesn't rank districts. Connection cost and substations need geography; no public reliability data has turned up; solar yield comes with the climate data (6).

### 5. Water

| Interview question | Measure | Candidate data | EDA must answer |
| --- | --- | --- | --- |
| Is there enough water? | Block category by stage of groundwater extraction: safe up to 70%, semi-critical, critical, and over-exploited above 100% ([CGWB definitions](https://www.cgwb.gov.in/cgwbpnm/public/uploads/documents/1742294726543197566file.pdf)) | CGWB Dynamic Ground Water Resources of UP, 2024 ([report](https://www.cgwb.gov.in/cgwbpnm/public/uploads/documents/1742294844551285154file.pdf)); surface water from India-WRIS | How do blocks map to districts? A district can hold both safe and over-exploited blocks |
| Is the quality good enough without treatment? | pH, hardness, TDS or conductivity, fluoride, nitrate against the product's needs | CGWB groundwater quality data and [yearbooks](https://cgwb.gov.in/en/node/1852) (monitoring-well samples) | How many wells per district? Is the sample dense enough to say anything about a district? |

Water is where hard filters matter most: a water-heavy product in an over-exploited block faces abstraction limits as well as cost.

In the MVP, blocks reach their district through CGWB's own listing of blocks under districts, with no map needed. Each district gets the share of its blocks that are over-exploited or critical.

### 6. Climate

One value per district from [NASA POWER](https://power.larc.nasa.gov/llms.txt) (free API, gridded), read at the district headquarters' coordinates (taken from Wikidata, CC0). The grid is coarse, so a point is about as precise as a district average, and it needs no boundaries. Climate appears as context and as risk flags (heat, rainfall variability), and it gives the solar yield for the power term.

## Data source inventory

The MVP draws on the sources below, with ethanol's first; those marked *Geography stage* or *Step 2* wait. "Found" means the source was seen to exist, not that its data has been downloaded and checked; that's the EDA's first job. Indian government sites can't be reached from the coding environment, so EDA files are downloaded by hand and logged in a manifest (file, checksum, URL, date, licence).

| Dataset | Publisher | Finest level | Access | Used for | Status |
| --- | --- | --- | --- | --- | --- |
| [LGD codes](https://ckandev.indiadataportal.com/dataset/lgd-codes) (state, district, sub-district, village) | Ministry of Panchayati Raj | Village | PDF/CSV; monthly API on data.gov.in | The join key for every other dataset | **Loaded** (75-district spine); GODL-India licence |
| District crop production (cane, rice, maize, others) | DES, Ministry of Agriculture (UPAg portal) | District | Portal download | Raw material and feedstock volume, consistency | Access to check |
| [ICRISAT District Level Database](https://tci.cornell.edu/data) | ICRISAT and Cornell TCI | District, 1966–2017 | Free download | Long-run production history | Found |
| Sugar mill crushing, recovery and molasses | UP Cane Development / Sugar Commissioner; mill annual reports | Mill (mapped to its district) | Reports (PDF) | Ethanol raw material and quality; press mud for CBG | Access to check |
| Distilleries and ethanol capacity | UP Excise; ethanol blending programme lists | Plant | Lists (PDF/web) | Existing use of feedstock (ethanol) | To find |
| Existing CBG plants | SATAT / GOBARdhan lists | Plant | Web lists | Existing use of feedstock (CBG) | To find |
| District livestock figures | Livestock Census (DAHD) | District | Report tables | Dung for CBG | To find (check the latest census) |
| Residue-to-crop ratios | Government biomass assessments; published literature | Crop | Reports | Crop residue for CBG | To find |
| [Agmarknet prices and arrivals](https://agmarknet.ceda.ashoka.edu.in/README.html) | Ministry of Agriculture (CEDA mirror) | Market, daily | Download or API | Input prices (grain); cane has a statewide advised price | Found |
| Circle rates (mulyankan suchi) | UP Stamps and Registration, IGRS UP | Sub-registrar area | Web, captcha, PDFs | Indicative land cost | Hard to collect at scale; consider an aggregator |
| Industrial area rates | UPSIDA, UPEIDA | Industrial area | Brochures, allotment notices | Land cost in ready parks | Found (scattered) |
| [Groundwater resources and quality](https://www.cgwb.gov.in/cgwbpnm/public/uploads/documents/1742294844551285154file.pdf) | CGWB | Block (listed under districts) | PDF reports, yearbooks, India-WRIS | Water availability; hard filter | Found; PDF extraction needed |
| [NASA POWER](https://power.larc.nasa.gov/llms.txt) climate and irradiance | NASA | Point (gridded) | Free API | Climate and solar yield at each district HQ | Found |
| District HQ coordinates | Wikidata | Point | Free API (CC0) | Where to read NASA POWER | Found |
| Tariff orders | UPERC, DISCOMs | State | PDF | Power cost (a constant) | Found |
| [ODOP list](https://www.data.gov.in/catalog/one-district-one-product) | GoI / UP MSME dept | District | data.gov.in | Reference check | Found |
| Substation lists ([CEA](https://cea.nic.in/wp-content/uploads/transmission/2026/07/SS_Commissioned_during_FY_2026_27_till_July__2026.pdf)), supply reliability | CEA; UPPCL, DISCOMs | Substation, area | Monthly PDFs; unknown | Grid access and reliability | *Geography stage* |
| OpenStreetMap | OSM contributors | Road, rail, power line | Free download (Geofabrik) | Distances, road density, infrastructure | *Geography stage* |
| [UP Bhulekh](https://www.godrejproperties.com/blog/up-bhulekh-how-to-check-and-download-khatauni) (Khatauni, Khasra) and Bhu-Naksha | UP Revenue Department | Plot | Web lookup, one record at a time | Ownership and plots | *Step 2*; no bulk access |

The licence for every source goes into `docs/data-sources.md` before it's ingested. Several state portals publish no licence; those need checking before any commercial use.

Where a government source proves poor, the data is bought from an aggregator or supplier instead, with its licence and cost logged, rather than cleaned by hand.

## EDA plan

The EDA's job is to decide which variables survive at district level, before any scoring is built. It runs in this order:

1. **Build the spine.** Done (22 Nov 2026): UP's 75 districts keyed on LGD codes, with a name-matching table (spellings differ across sources, and five districts were created after 2011). Boundaries move to the geography stage.
2. **Audit coverage.** For each source: which districts and years it covers, its gaps, its latest date and its licence. Output: a coverage grid of source × district. Files are downloaded by hand and registered in the manifest.
3. **Write the pilot profiles.** Ethanol and CBG from public sources, with a source and confidence per field; then Manvendra's real plant figures in the private file.
4. **Explore each variable on its own.** Its distribution across districts, how much it varies (a variable that barely changes between districts can't rank them), its outliers and its trend over time.
5. **Join into one district table.** Every kept source joined to the spine: 75 rows, one per LGD code, with coverage shown per column.
6. **Check variables against each other.** Correlations and redundancy, so one effect isn't counted twice.
7. **Check against the ground.** Manvendra's good and avoid districts for each pilot, given before he sees any output; his real land deal prices against circle rates.
8. **Prototype the cost model** in a notebook: hard filters, ₹/t ranges, confidence and rank ranges, and the comparison with the naive baseline (rank correlation, plus a written reason for every district that moves a lot). The go / pivot decision follows, by 1 Jan 2027: if the two viability bars fail, the pipeline is kept and pointed at a question the data does answer.

**A variable goes into the MVP only if** it covers at least 70 of 75 districts, its data is no older than 3 years (or the age is shown), it varies enough between districts to change a ranking, and its licence allows the use.

**Outputs of the EDA:** a short write-up per variable (keep, drop or proxy, and why), a data-quality log, the filled product profiles, the district table, and the prototype model with its baseline comparison. Claude Code finds and assesses the sources and loads each into a notebook; Sage builds the joins, the analysis and the cost model.

## Architecture

**Updated 24 Nov 2026.** The MVP runs locally first: Postgres/PostGIS, DuckDB and pandas for the EDA, then Python extractors on an **Airflow** schedule (in Docker) and **dbt** models, with no cloud spend during the EDA. In March 2027 it moves to AWS (S3 for raw files, one EC2 instance running Airflow in Docker), with **Snowflake** as the warehouse as a stretch goal (fallback: Postgres on AWS). No Spark or EMR: the data is small. Airflow fits because the sources update on different schedules (Agmarknet and NASA POWER daily, LGD and CEA monthly), government sites need retries and backfills, and dbt should run only after loads succeed.

&#91;embedded content: architecture · MVP pipeline and the scale-up path\]

Every source lands raw (the original file plus Parquet, with a manifest) before it's modelled, so a new dataset means a new extractor and model, not a redesign. dbt runs on Postgres locally and on Snowflake in the cloud, so the models keep spatial logic in one place, use dbt's cross-database macros and avoid Postgres-only features. Kafka for live feeds, Terraform and Kubernetes are added only if they're needed after the MVP.

## Step 2: geography, then land parcels

Step 2 starts after the MVP ranking holds up and after the March–April 2027 interviews. It opens with a geography stage: district boundaries, road density as a land-price proxy, land quality, and distances to supply, buyers and substations. Then it narrows a chosen district down to villages and plots, and to the people who sign off.

1. **Rank within the district.** Rerun the same variables at block and tehsil level where the data allows (groundwater is already block-level; roads, substations and dry ports are points, so distances work at any level).
2. **Shortlist villages.** Villages within reach of a substation, an all-weather road and the raw material, using LGD village codes and OpenStreetMap.
3. **Look up the land.** For shortlisted villages, the Khatauni (record of rights: owners, khata) and Khasra (plot number, area, land class) on [UP Bhulekh](https://www.godrejproperties.com/blog/up-bhulekh-how-to-check-and-download-khatauni), and plot boundaries on Bhu-Naksha. Online copies are for reference; a deal needs certified copies from the tehsil office.
4. **Map the people and offices.** The tehsil (tehsildar and the village lekhpal for records), the sub-registrar office for registration and circle rates, the Nivesh Mitra single window for approvals, and UPSIDA or UPEIDA if a ready industrial plot fits better. The partners know which steps are slow in practice.

**Bulk access is the open problem.** Bhulekh serves one record at a time behind a captcha. District sites mention a [Bhulekh Data API](https://fatehpur.nic.in/?p=2872) for sharing land-record data with other applications; whether outsiders can get access is the first thing to find out. Scraping the portal is not the plan: it raises terms-of-use and legal questions the lawyer partner should advise on.

**Owner names are personal data.** Anything storing Khatauni owner details needs a lawful basis and a retention rule under India's data protection law; the lawyer partner should set these before Phase II stores a single record.

**Questions for the lawyer partner** before step 2 stores anything:

- Is automating Bhulekh lookups allowed (terms of use, the captcha, IT law)? The plan is one plot at a time, by a person or with a web library.
- Under the DPDP Act, what lawful basis and consent are needed to store landowner names and contacts and show them to agents who'll pitch them?
- Can outsiders get access to the official Bhulekh Data API?
- Would an opt-in network, where landowners and agents agree to be contacted, solve the consent question?

## Risks, assumptions and open questions

The biggest risk is false precision: a rupee total built on circle rates, district averages and old data can look more certain than it is. Every number carries a source date and a confidence rating for that reason.

| Risk or assumption | Why it matters | Mitigation |
| --- | --- | --- |
| Circle rates sit below market prices, by different amounts in different places | Land cost could be wrong in both level and ranking | Calibrate against Manvendra's real deal prices |
| District averages hide variation inside a district | A good district can have bad blocks, and the reverse | Show the spread where block data exists; step 2 drills down |
| Some prices are regulated (cane, grid tariff) | They can't separate districts | Keep them in the cost total as constants; let the EDA drop them as rankers |
| Product profiles are estimates | Every term scales with them | Manvendra's real figures check them; the ranges show the effect |
| Feedstock is inferred from crop and livestock data | Availability may be over- or under-stated | Shown as an indication with a confidence rating; users verify on the ground |
| Licences: some sources are non-commercial or unstated | A paid product can't use them as is | Log licences from day one; buy from an aggregator if needed |
| Data is old or patchy (water-quality wells, Census gaps for newer districts) | A variable may be unusable | The EDA's keep, drop or proxy rule decides |
| Manvendra's plant figures or contacts leak into the public repo | Breaks his trust and his business confidentiality | Private git-ignored file with a pre-commit guard; scrub before the repo goes public |

**Open questions for Sage and the partners:**

- [ ] The third pilot product (Manvendra)
- [ ] Manvendra's real plant figures for ethanol and CBG: feedstock type, ratio and price; water; power; operating days; TPD range; project life
- [ ] His good and avoid districts for each pilot, given before he sees any output
- [ ] Real recent land deal prices in 3–5 districts, urban and rural
- [ ] Does the TPD + 2 acres land rule also hold for ethanol?
- [ ] QCI or other quality data for the inputs (low priority)
- [ ] The lawyer partner's answers on Bhulekh and the DPDP Act (step 2 only)

Answered: the first user is Manvendra; the pilots are ethanol and CBG; TPD means tonnes of output per day; the CBG land rule is TPD + 2 acres. Power reliability is deprioritised, since power doesn't rank districts in the MVP.

## Next steps

The build follows a dated plan, sized to 10 hours a week. **The March 2027 minimum** is ethanol end to end, from sources through Airflow and dbt to the ranking, running in the cloud, with a clear README. Everything else is a bonus.

| When | Goal |
| --- | --- |
| Dec 2026 | EDA and viability: district-level sources, joins, first cost model for ethanol, then CBG; go / pivot decision by 1 Jan |
| Jan 2027 | Raw layer locally: Airflow in Docker, extractors for the kept sources; repo public with a good README |
| 1–14 Feb | dbt staging and intermediate models, with tests and docs |
| 15–28 Feb | dbt ranking marts: cost components, filters, ranges and confidence |
| 1–15 Mar | Move to AWS (S3, one EC2 running Airflow), with Snowflake as the stretch goal |
| 16–31 Mar | Simple results page, recorded walkthrough, case study and interview notes |
| Apr | Buffer only |
| After interviews | Geography stage, then step 2 (land parcels, Bhulekh, the network) |

- [ ] Manvendra's answers by 15 Dec 2026
- [ ] Manual source downloads by Sage (early Dec)
- [ ] Go / pivot decision by 1 Jan 2027
