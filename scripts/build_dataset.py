"""Combine NHS England monthly A&E CSVs (Apr-Sep 2026) with the ICB system mapping
into one tidy dataset, and check every month against NHS England's own TOTAL row."""
import glob, os, re, sys
import pandas as pd

UP = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

MONTHS = {"APRIL": 4, "MAY": 5, "JUNE": 6, "JULY": 7, "AUGUST": 8, "SEPTEMBER": 9,
          "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12, "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3}

RENAME = {
    "A&E attendances Type 1": "att_type1",
    "A&E attendances Type 2": "att_type2",
    "A&E attendances Other A&E Department": "att_other",
    "A&E attendances Booked Appointments Type 1": "att_booked_type1",
    "A&E attendances Booked Appointments Type 2": "att_booked_type2",
    "A&E attendances Booked Appointments Other Department": "att_booked_other",
    "Attendances over 4hrs Type 1": "over4h_type1",
    "Attendances over 4hrs Type 2": "over4h_type2",
    "Attendances over 4hrs Other Department": "over4h_other",
    "Attendances over 4hrs Booked Appointments Type 1": "over4h_booked_type1",
    "Attendances over 4hrs Booked Appointments Type 2": "over4h_booked_type2",
    "Attendances over 4hrs Booked Appointments Other Department": "over4h_booked_other",
    "Patients who have waited 4-12 hs from DTA to admission": "dta_wait_4_12h",
    "Patients who have waited 12+ hrs from DTA to admission": "dta_wait_12h_plus",
    "Emergency admissions via A&E - Type 1": "emerg_adm_type1",
    "Emergency admissions via A&E - Type 2": "emerg_adm_type2",
    "Emergency admissions via A&E - Other A&E department": "emerg_adm_other",
    "Other emergency admissions": "emerg_adm_not_via_ae",
}
NUM = list(RENAME.values())

frames, totals, checks = [], [], []
for f in sorted(glob.glob(os.path.join(UP, "*.csv"))):
    raw = pd.read_csv(f, dtype=str)
    raw.columns = [c.strip() for c in raw.columns]
    raw = raw.rename(columns=RENAME)
    for c in raw.columns:
        raw[c] = raw[c].str.strip()
    is_total = raw["Period"].str.upper() == "TOTAL"
    tot = raw[is_total].copy()
    df = raw[~is_total].copy()
    for c in NUM:
        df[c] = pd.to_numeric(df[c]).astype(int)
        tot[c] = pd.to_numeric(tot[c]).astype(int)
    m = re.match(r"MSitAE-([A-Z]+)-(\d{4})", df["Period"].iloc[0])
    mon, yr = MONTHS[m.group(1)], int(m.group(2))
    df["month"] = pd.Timestamp(year=yr, month=mon, day=1)
    # check: sum of org rows equals NHS England's TOTAL row, column by column
    diff = (df[NUM].sum() - tot[NUM].iloc[0]).abs().sum()
    checks.append((df["month"].iloc[0].strftime("%b %Y"), len(df), int(diff)))
    frames.append(df)

data = pd.concat(frames, ignore_index=True)
data = data.rename(columns={"Org Code": "org_code", "Parent Org": "nhs_region_raw", "Org name": "org_name_as_reported"})
data["nhs_region"] = (data["nhs_region_raw"].str.replace("NHS ENGLAND ", "", regex=False)
                      .str.title().str.replace(" And ", " and ").str.replace(" Of ", " of "))

# one consistent display name per org: the most recent name it reported under
latest = data.sort_values("month").groupby("org_code")["org_name_as_reported"].last()
data["org_name"] = data["org_code"].map(latest).str.title() \
    .str.replace(" Nhs ", " NHS ").str.replace(" And ", " and ").str.replace(" Of ", " of ") \
    .str.replace("'S ", "'s ").str.replace(" Utc", " UTC").str.replace(" Ucc", " UCC") \
    .str.replace(" Miu", " MIU").str.replace(" Ooh", " OOH").str.replace(" Gp ", " GP ") \
    .str.replace(" Cic", " CIC").str.replace(" C.I.C", " C.I.C").str.replace("Dhu ", "DHU ") \
    .str.replace("Llr Ea", "LLR EA").str.replace("Phl ", "PHL ").str.replace(" Ltd", " Ltd") \
    .str.replace(" Upon ", " upon ").str.replace(" Med.Ctr", " Med. Ctr")

# --- headline measures (NHS England definitions: booked appointments count as attendances)
data["attendances_type1"] = data["att_type1"] + data["att_booked_type1"]
data["attendances_type2"] = data["att_type2"] + data["att_booked_type2"]
data["attendances_other"] = data["att_other"] + data["att_booked_other"]
data["attendances_total"] = data[["attendances_type1", "attendances_type2", "attendances_other"]].sum(axis=1)
data["over4h_type1_total"] = data["over4h_type1"] + data["over4h_booked_type1"]
data["over4h_total"] = data[[c for c in NUM if c.startswith("over4h")]].sum(axis=1)
data["within4h_total"] = data["attendances_total"] - data["over4h_total"]
data["within4h_type1"] = data["attendances_type1"] - data["over4h_type1_total"]
data["pct_within_4h_all"] = (data["within4h_total"] / data["attendances_total"]).where(data["attendances_total"] > 0)
data["pct_within_4h_type1"] = (data["within4h_type1"] / data["attendances_type1"]).where(data["attendances_type1"] > 0)
data["emergency_admissions_via_ae"] = data[["emerg_adm_type1", "emerg_adm_type2", "emerg_adm_other"]].sum(axis=1)
data["emergency_admissions_total"] = data["emergency_admissions_via_ae"] + data["emerg_adm_not_via_ae"]

# provider type: does it run a major (Type 1) A&E at any point in the period?
has_t1 = data.groupby("org_code")["attendances_type1"].max() > 0
data["provider_type"] = data["org_code"].map(lambda c: "Major A&E (Type 1) trust" if has_t1[c]
                                             else "Other urgent care provider")

# --- ICB mapping
mp = pd.read_excel(os.path.join(UP, [f for f in os.listdir(UP) if f.endswith(".xls")][0]), header=7)
mp = mp.dropna(axis=1, how="all").dropna(subset=["Code"])
mp.columns = ["org_code", "mapping_name", "icb_code", "icb_name", "commissioning_region"]
mp["org_code"] = mp["org_code"].astype(str).str.strip()
for c in ["icb_code", "icb_name"]:
    mp[c] = mp[c].astype(str).str.strip()
mp["icb_name"] = mp["icb_name"].str.replace(" And ", " and ")
dupes = mp[mp["org_code"].duplicated(keep=False)]
mp1 = mp.drop_duplicates("org_code")
data = data.merge(mp1[["org_code", "icb_code", "icb_name"]], on="org_code", how="left")
unmapped = sorted(data.loc[data["icb_code"].isna(), "org_code"].unique())
data["icb_name"] = data["icb_name"].fillna("Not in April 2026 mapping file")

cols = ["month", "org_code", "org_name", "org_name_as_reported", "provider_type", "nhs_region",
        "icb_code", "icb_name",
        "attendances_total", "attendances_type1", "attendances_type2", "attendances_other",
        "within4h_total", "over4h_total", "pct_within_4h_all",
        "within4h_type1", "over4h_type1_total", "pct_within_4h_type1",
        "dta_wait_4_12h", "dta_wait_12h_plus",
        "emergency_admissions_via_ae", "emerg_adm_not_via_ae", "emergency_admissions_total"]
tidy = data[cols].sort_values(["month", "org_code"]).reset_index(drop=True)
tidy["month"] = tidy["month"].dt.strftime("%Y-%m-01")
tidy.to_csv(os.path.join(OUT, "nhs_ae_apr_sep_2026_clean.csv"), index=False)

# England summary by month
eng = data.groupby("month")[["attendances_total", "within4h_total", "attendances_type1", "within4h_type1",
                             "dta_wait_12h_plus", "emergency_admissions_total"]].sum()
eng["pct_within_4h_all"] = eng["within4h_total"] / eng["attendances_total"]
eng["pct_within_4h_type1"] = eng["within4h_type1"] / eng["attendances_type1"]
eng.index = eng.index.strftime("%b %Y")

print("CHECK vs NHS TOTAL rows (month, org rows, absolute difference):")
for c in checks: print("  ", c)
print("\nRows in clean file:", len(tidy), "| orgs:", tidy.org_code.nunique())
print("Orgs per month:", tidy.groupby("month").org_code.nunique().to_dict())
print("\nMapping duplicates:\n", dupes.to_string() if len(dupes) else "  none")
print("\nUnmapped org codes:", unmapped)
for c in unmapped:
    print("   ", c, data.loc[data.org_code == c, "org_name"].iloc[0])
print("\nEngland by month:\n", eng.round(4).to_string())
# orgs not present in every month
pres = tidy.groupby("org_code").month.nunique()
print("\nOrgs missing some months:")
for c, n in pres[pres < tidy.month.nunique()].items():
    print("   ", c, tidy.loc[tidy.org_code == c, "org_name"].iloc[0], sorted(tidy.loc[tidy.org_code == c, "month"]))
# name changes
nc = data.groupby("org_code")["org_name_as_reported"].nunique()
print("\nName changes:")
for c in nc[nc > 1].index:
    print("   ", c, list(data.loc[data.org_code == c].sort_values("month")["org_name_as_reported"].unique()))
