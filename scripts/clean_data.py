"""
clean_data.py
Cleans raw patent TSV files and exports cleaned CSVs to data/clean/
"""

import pandas as pd
import os

# ── Create output folder ──────────────────────────────────────────────────────
os.makedirs("data/clean", exist_ok=True)

print("=" * 55)
print("         PATENT DATA CLEANING PIPELINE")
print("=" * 55)

# ══════════════════════════════════════════════════════════
# 1. LOAD RAW DATA
# ══════════════════════════════════════════════════════════
print("\n[1/5] Loading raw data...")

patent_df   = pd.read_csv("data/raw/g_patent.tsv",               sep="\t", nrows=1000000, low_memory=False)
inventor_df = pd.read_csv("data/raw/g_inventor_disambiguated.tsv", sep="\t", low_memory=False)
assignee_df = pd.read_csv("data/raw/g_assignee_disambiguated.tsv", sep="\t", low_memory=False)
abstract_df = pd.read_csv("data/raw/g_patent_abstract.tsv",       sep="\t", nrows=1000000, low_memory=False)
location_df = pd.read_csv("data/raw/g_location_disambiguated.tsv", sep="\t", low_memory=False)

print(f"  Patents loaded:   {len(patent_df):,}")
print(f"  Inventors loaded: {len(inventor_df):,}")
print(f"  Assignees loaded: {len(assignee_df):,}")
print(f"  Abstracts loaded: {len(abstract_df):,}")
print(f"  Locations loaded: {len(location_df):,}")

# ══════════════════════════════════════════════════════════
# 2. CLEAN PATENTS
# ══════════════════════════════════════════════════════════
print("\n[2/5] Cleaning patents...")

# Merge abstracts in
patents_clean = patent_df.merge(abstract_df, on="patent_id", how="left")

# Select and rename columns
patents_clean = patents_clean[[
    "patent_id", "patent_title", "patent_abstract",
    "patent_date", "patent_type", "num_claims"
]].rename(columns={
    "patent_title":    "title",
    "patent_abstract": "abstract",
    "patent_date":     "filing_date"
})

# Extract year from date
patents_clean["filing_date"] = pd.to_datetime(patents_clean["filing_date"], errors="coerce")
patents_clean["year"]        = patents_clean["filing_date"].dt.year
patents_clean["filing_date"] = patents_clean["filing_date"].dt.strftime("%Y-%m-%d")

# Drop rows with no patent_id or title
patents_clean.dropna(subset=["patent_id", "title"], inplace=True)
patents_clean.drop_duplicates(subset="patent_id", inplace=True)

# Fill missing abstracts
patents_clean["abstract"].fillna("No abstract available", inplace=True)

print(f"  Clean patents: {len(patents_clean):,}")
patents_clean.to_csv("data/clean/clean_patents.csv", index=False)
print("  Saved → data/clean/clean_patents.csv")

# ══════════════════════════════════════════════════════════
# 3. CLEAN INVENTORS  (join location for country)
# ══════════════════════════════════════════════════════════
print("\n[3/5] Cleaning inventors...")

# Keep only the location country column from locations
loc_country = location_df[["location_id", "disambig_country"]].drop_duplicates("location_id")

inventors_clean = inventor_df.merge(loc_country, on="location_id", how="left")

# Build full name
inventors_clean["name"] = (
    inventors_clean["disambig_inventor_name_first"].fillna("") + " " +
    inventors_clean["disambig_inventor_name_last"].fillna("")
).str.strip()

inventors_clean = inventors_clean[[
    "inventor_id", "name", "disambig_country", "patent_id"
]].rename(columns={"disambig_country": "country"})

# Drop rows missing inventor_id
inventors_clean.dropna(subset=["inventor_id"], inplace=True)
inventors_clean["name"].replace("", "Unknown", inplace=True)

print(f"  Clean inventor records: {len(inventors_clean):,}")
inventors_clean.to_csv("data/clean/clean_inventors.csv", index=False)
print("  Saved → data/clean/clean_inventors.csv")

# ══════════════════════════════════════════════════════════
# 4. CLEAN COMPANIES (assignees)
# ══════════════════════════════════════════════════════════
print("\n[4/5] Cleaning companies...")

assignees_clean = assignee_df.copy()

# Use organization name; fall back to individual name
assignees_clean["name"] = assignees_clean["disambig_assignee_organization"].fillna(
    (
        assignees_clean["disambig_assignee_individual_name_first"].fillna("") + " " +
        assignees_clean["disambig_assignee_individual_name_last"].fillna("")
    ).str.strip()
)

assignees_clean = assignees_clean[[
    "assignee_id", "name", "patent_id"
]].rename(columns={"assignee_id": "company_id"})

# Drop rows missing company_id or name
assignees_clean.dropna(subset=["company_id", "name"], inplace=True)
assignees_clean = assignees_clean[assignees_clean["name"] != ""]

print(f"  Clean company records: {len(assignees_clean):,}")
assignees_clean.to_csv("data/clean/clean_companies.csv", index=False)
print("  Saved → data/clean/clean_companies.csv")

# ══════════════════════════════════════════════════════════
# 5. SUMMARY
# ══════════════════════════════════════════════════════════
print("\n[5/5] Cleaning complete!")
print("=" * 55)
print(f"  Patents:   {len(patents_clean):,} rows")
print(f"  Inventors: {len(inventors_clean):,} rows")
print(f"  Companies: {len(assignees_clean):,} rows")
print("=" * 55)
print("\nNext step → run:  python scripts/load_to_db.py")