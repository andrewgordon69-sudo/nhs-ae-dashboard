# England A&E Waits

An interactive dashboard showing how quickly A&E departments in England saw patients between April and September 2026. You can look at England as a whole or filter by NHS region, local health system (ICB) or individual trust.

**Live dashboard:** open `index.html` in any browser, or visit the GitHub Pages link in this repository's About section.

## What it shows

- The share of patients admitted, transferred or discharged within four hours, compared with the 82% target for 2026-27 and the 95% NHS Constitution standard.
- Monthly trends for all A&E types and for major (Type 1) emergency departments.
- A regional comparison, where selecting a region filters the whole page.
- A sortable, searchable table of 120 major A&E trusts and 72 other urgent care providers, with six-month sparklines and status against the target.
- Patients waiting more than 12 hours for a bed after the decision to admit them.

## Headline findings

- England saw **74.4%** of A&E patients within four hours in September 2026, down from 76.9% in April and 7.6 points short of the 82% target.
- In major (Type 1) departments, the figure fell from 63.8% to **60.6%**.
- Only **7 of 120** major A&E trusts met 82% in September.
- Between 45,000 and 51,000 patients a month waited more than 12 hours for a bed after the decision to admit.

## Data

- **Source:** NHS England, [A&E Attendances and Emergency Admissions 2026-27](https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/ae-attendances-and-emergency-admissions-2026-27/). I used the monthly provider-level CSVs for April to September 2026, plus the April 2026 System Mapping File for ICBs.
- **Validation:** for every month, the provider rows reconcile exactly to NHS England's published England totals.
- **Data quirks handled:**
  - The Bristol trusts merged in July 2026.
  - Two trusts were renamed.
  - Two sites only report from May.
  - One provider is missing from the ICB mapping file.

  [`data/DATA_NOTES.md`](data/DATA_NOTES.md) explains each of these.

## How it was built

| Step | Tool |
|---|---|
| Combine six monthly files, clean names, map providers to ICBs, check against NHS totals | Python and pandas (`scripts/build_dataset.py`) |
| Embed the clean data into a single self-contained web page | Python (`scripts/build_dashboard.py`) |
| Dashboard charts, filters and table | Plain HTML, CSS and JavaScript, with no libraries or server needed |

The data preparation and dashboard were built with AI assistance (Claude), with the figures checked against the source totals.

To rebuild after adding a new month:

```bash
python3 scripts/build_dataset.py <folder of NHS CSVs + mapping .xls> data/
python3 scripts/build_dashboard.py
```

## Repository contents

```
index.html                      the dashboard (open in a browser)
dashboard_template.html         dashboard source, before the data is embedded
data/nhs_ae_apr_sep_2026_clean.csv   the clean dataset, one row per provider per month
data/DATA_NOTES.md              definitions, checks and caveats
scripts/build_dataset.py        raw NHS files -> clean dataset
scripts/build_dashboard.py      clean dataset -> index.html
```

This is an independent analysis of published official statistics, not an NHS publication.
