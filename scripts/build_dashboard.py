"""Build index.html: embed the clean A&E dataset into dashboard_template.html.

Usage:  python3 scripts/build_dashboard.py
Reads   data/nhs_ae_apr_sep_2026_clean.csv and dashboard_template.html
Writes  index.html (one self-contained file, no server needed)
"""
import json, pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
d = pd.read_csv(ROOT / "data" / "nhs_ae_apr_sep_2026_clean.csv")
months = sorted(d["month"].unique())
idx = {m: i for i, m in enumerate(months)}

FIELDS = ["attendances_total", "within4h_total", "attendances_type1", "within4h_type1",
          "dta_wait_12h_plus", "emergency_admissions_total"]

orgs = []
for code, g in d.groupby("org_code"):
    first = g.sort_values("month").iloc[-1]
    series = {f: [None] * len(months) for f in FIELDS}
    for _, r in g.iterrows():
        for f in FIELDS:
            series[f][idx[r["month"]]] = int(r[f])
    orgs.append({
        "c": code,
        "n": first["org_name"],
        "t1": first["provider_type"].startswith("Major"),
        "r": first["nhs_region"],
        "i": first["icb_name"].replace(" Of ", " of "),
        "a": series["attendances_total"],
        "w": series["within4h_total"],
        "a1": series["attendances_type1"],
        "w1": series["within4h_type1"],
        "x12": series["dta_wait_12h_plus"],
        "ea": series["emergency_admissions_total"],
    })

payload = {"months": months, "orgs": orgs, "built": pd.Timestamp.now().strftime("%d %B %Y")}
tpl = (ROOT / "dashboard_template.html").read_text(encoding="utf-8")
body = tpl.replace("/*__DATA__*/null", json.dumps(payload, separators=(",", ":")))
html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '</head>\n<body>\n' + body + '\n</body>\n</html>\n')
(ROOT / "index.html").write_text(html, encoding="utf-8")
# page body only, for hosts that supply their own document wrapper
(ROOT / "build").mkdir(exist_ok=True)
(ROOT / "build" / "england-ae-waits.html").write_text(body, encoding="utf-8")
print(f"index.html written: {len(orgs)} providers, {len(months)} months, {len(html)/1024:.0f} KB")
