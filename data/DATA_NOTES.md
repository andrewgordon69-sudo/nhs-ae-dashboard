# NHS A&E Performance, April–September 2026: Data Notes

## Source
NHS England, *A&E Attendances and Emergency Admissions 2026-27*: the monthly provider-level CSVs for April to September 2026, plus the System Mapping File (last updated 14 May 2026) for each provider's Integrated Care Board (ICB).

## The clean file
`nhs_ae_apr_sep_2026_clean.csv` has one row per provider per month: 1,147 rows covering 192 providers, 7 NHS regions and 37 ICBs.

## How it was checked
For every month, the provider rows were summed column by column and compared with NHS England's own TOTAL row. All six months match exactly (zero difference). The TOTAL rows were then removed from the clean file, so they are not double-counted.

## Measures
- **attendances_total**: all A&E attendances, including booked appointments (NHS England's definition).
- **pct_within_4h_all**: the share of all attendances admitted, transferred or discharged within 4 hours. The national standard is 95%; the 2026-27 operational target is 82%.
- **pct_within_4h_type1**: the same measure for major (Type 1) A&E departments only. It is the stricter, most-quoted figure.
- **dta_wait_12h_plus**: patients who waited more than 12 hours from the decision to admit to actually being admitted ("trolley waits").
- **provider_type**: "Major A&E (Type 1) trust" if the provider reported any Type 1 attendances during the period, otherwise "Other urgent care provider" (walk-in centres, UTCs, MIUs and specialist trusts).

Percentages are blank where a provider had no attendances of that type. In Power BI, recalculate percentages from the counts (for example, SUM of within4h_total ÷ SUM of attendances_total) rather than averaging the percentage column.

## Things to know
- **Bristol merger.** From July 2026, North Bristol NHS Trust (RVJ) stops reporting, and University Hospitals Bristol and Weston (RA7) reports as "Bristol NHS Foundation Trust", with a jump in attendances. Treat RA7's step change from July as a merger, not a real rise in demand.
- **Renamed trust.** RXG became "South West Yorkshire Partnership *Teaching* NHS Foundation Trust" in July. The clean file uses each provider's latest name, and keeps the original in `org_name_as_reported`.
- **New sites.** Enderby Leisure Centre (NNJ10) and Lutterworth Hospital (NNJ11) appear from May 2026 only.
- **Unmapped provider.** Ashford Walk-In-Centre (NTV0B) is not in the April 2026 mapping file, so its ICB is shown as "Not in April 2026 mapping file". Its region (South East) is still populated.
