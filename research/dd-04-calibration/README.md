# DD-04 calibration data

Status: decided 2026-10-03. Last updated 2026-10-03.
Source figures and scripts behind DD-04, the rent clamp and city rate tier calibration ([open decisions](../../docs/open-decisions.md)). The clamp is the policy floor and cap on every rent change ([ADR-020](../../docs/decisions/ADR-020-rent-clamp-and-symbolic-bands.md)). Rate tiers are per-city rent levels ([ADR-012](../../docs/decisions/ADR-012-data-scale-scenarios-and-variants.md)).

## Files

| File | Holds | Made by |
|---|---|---|
| `city_zips.csv` | City to ZIP map for the seven cities | Hand-built, rules below |
| `safmr_city_zips.csv` | HUD SAFMR 2BR and 3BR, FY2026 and FY2027, for those ZIPs | Browser extraction, steps below |
| `acs_places_2024.csv` | Census ACS 2020 to 2024 5-year median gross rent, all units, 2BR, 3BR | `fetch_acs.py` |
| `fetch_acs.py` | Census API pull for the seven places | |
| `summarize.py` | Per-city table and pooled year-over-year change | |
| `raw/` | Local copies of source spreadsheets. Gitignored | You, by hand |

## Sources
- HUD Small Area Fair Market Rents (SAFMRs), ZIP-level rent benchmarks. Data page: https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html
  - FY2027: https://www.huduser.gov/portal/datasets/fmr/fmr2027/FY27_safmrs.xlsx
  - FY2026 revised: https://www.huduser.gov/portal/datasets/fmr/fmr2026/fy2026_safmrs_revised.xlsx
  - Methodology: https://www.huduser.gov/portal/datasets/fmr/fmr2027/FY27-Public-SAFMR-Methodology.pdf
- Census ACS 5-year, 2024 vintage, tables B25064 (median gross rent) and B25031 (median gross rent by bedrooms). API: https://api.census.gov/data/2024/acs/acs5. Key signup: https://api.census.gov/data/key_signup.html

## Re-fetch the HUD files
HUD serves a bot check. `curl` gets an empty HTTP 202, so download by browser.
1. Open the data page above in a browser. Under "FY2027 Small Area FMRs", open the Data tab and click "Small Area FMRs". For FY2026, use the FY2026 section's revised file
2. Save both into `research/dd-04-calibration/raw/`
3. In each file, filter the `SAFMRs` sheet to the ZIPs in `city_zips.csv`, taking the first Texas row per ZIP. Keep columns `ZIP Code`, `HUD Area Code`, `SAFMR 2BR`, `SAFMR 3BR`
4. Compare against `safmr_city_zips.csv`. SHA-256 of the committed file: `c9190a0d3dc65e0163045bf7f03c0ca21eda60f5616e94a1b029087feb562580`

The committed CSV was extracted in a browser session that parsed both spreadsheets directly. Its hash was computed in the browser and matched the file on disk.

## Re-fetch the ACS figures
1. Put `CENSUS_API_KEY` in `.env` (see `.env.example`)
2. `uv run --no-project --env-file .env research/dd-04-calibration/fetch_acs.py`
3. `uv run --no-project research/dd-04-calibration/summarize.py`

## City to ZIP rules
- USPS city ZIPs for each city, residential only
- ZIPs carrying the metro default value (the same figure as most PO-box ZIPs in that FMR area) are left out
- Highland Park is 75205 only. University Park and Dallas ZIPs that touch it are left out
- Lewisville is 75057 and 75067. 75077 is shared with Highland Village and Flower Mound, and 75056 is mostly The Colony
- Dallas is 75201 to 75254 plus 75287, without 75205. Fort Worth leaves out ZIPs whose USPS city is another town

## Results (2026-10-03)

| City | ACS median gross rent | ACS 3BR | ZIPs | SAFMR FY2027 3BR median | 3BR range | 3BR FY26 to FY27 median % | 3BR FY26 to FY27 range % |
|---|---|---|---|---|---|---|---|
| Highland Park | 1940 | suppressed | 1 | 3410 | 3410 to 3410 | -6.1 | -6.1 to -6.1 |
| Prosper | 2176 | 2700 | 1 | 3260 | 3260 to 3260 | -7.1 | -7.1 to -7.1 |
| Plano | 1841 | 2340 | 6 | 2815 | 2390 to 3030 | -8.3 | -9.0 to +0.0 |
| Lewisville | 1670 | 2269 | 2 | 2365 | 2340 to 2390 | -7.8 | -8.4 to -7.1 |
| Dallas | 1472 | 1665 | 47 | 2090 | 1420 to 3410 | -7.4 | -9.9 to +0.0 |
| Fort Worth | 1509 | 1823 | 29 | 2210 | 1780 to 3350 | -0.5 | -4.0 to +4.2 |
| Arlington | 1470 | 1889 | 12 | 2405 | 2050 to 3310 | -0.5 | -4.5 to +1.6 |

Pooled 3BR FY26 to FY27 across 98 ZIPs: median -5.5%, min -9.9%, max +4.2%.

## Decided values (2026-10-03)
- Clamp: floor -5%, cap +6%. Bands: REDUCE -5 to below 0, HOLD 0, LOW above 0 to 2, MODERATE above 2 to 4, HIGH above 4 to 6 ([ADR-020](../../docs/decisions/ADR-020-rent-clamp-and-symbolic-bands.md))
- Base monthly rent per rate tier: low $1,800 to $2,400, medium $2,400 to $3,000, high $3,000 to $3,600 ([ADR-012](../../docs/decisions/ADR-012-data-scale-scenarios-and-variants.md))
- Rate tiers per city are unchanged. Dallas (sourced low, kept medium) and Lewisville (sourced medium, kept low) keep a contrasting demand value in every tier

## Reading the numbers
- SAFMR is HUD's 40th percentile gross rent benchmark for voucher payment standards. It is not a market rent or a renewal increase
- ACS 5-year figures pool 2020 to 2024 and cover all renter units, mostly apartments. Single-family homes rent higher
- The Dallas and Fort Worth-Arlington FMR areas have the same definitions in FY2026 and FY2027. The Dallas-area drop is in HUD's estimates, not a boundary change. Its cause was not investigated
- Highland Park ACS 3BR is suppressed by Census (sentinel -666666666). Highland Park and Prosper rest on one ZIP each

## Known gaps and open questions
- ZIP lists are hand-built from USPS city names. A HUD USPS crosswalk would be more exact but needs an API token
