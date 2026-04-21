"""
load_to_db.py
Loads cleaned CSV data into a SQLite database using schema.sql
"""

import pandas as pd
import sqlite3
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
DB_PATH     = "database/patents.db"
SCHEMA_PATH = "sql/schema.sql"

os.makedirs("database", exist_ok=True)

print("=" * 55)
print("       LOADING DATA INTO SQLITE DATABASE")
print("=" * 55)

# ── Connect and apply schema ──────────────────────────────────────────────────
print("\n[1/5] Setting up database schema...")
conn = sqlite3.connect(DB_PATH)

with open(SCHEMA_PATH, "r") as f:
    conn.executescript(f.read())

conn.commit()
print(f"  Database created at: {DB_PATH}")

# ── Load cleaned CSVs ─────────────────────────────────────────────────────────
print("\n[2/5] Loading clean_patents.csv...")
patents_df = pd.read_csv("data/clean/clean_patents.csv")
patents_df = patents_df[["patent_id", "title", "abstract", "filing_date", "year", "patent_type", "num_claims"]]
patents_df.to_sql("patents", conn, if_exists="append", index=False)
print(f"  Inserted {len(patents_df):,} patents")

print("\n[3/5] Loading clean_inventors.csv...")
inventors_df = pd.read_csv("data/clean/clean_inventors.csv")

# Unique inventors table (one row per inventor_id)
inventors_unique = inventors_df[["inventor_id", "name", "country"]].drop_duplicates("inventor_id")
inventors_unique.to_sql("inventors", conn, if_exists="append", index=False)
print(f"  Inserted {len(inventors_unique):,} unique inventors")

print("\n[4/5] Loading clean_companies.csv...")
companies_df = pd.read_csv("data/clean/clean_companies.csv")

# Unique companies table
companies_unique = companies_df[["company_id", "name"]].drop_duplicates("company_id")
companies_unique.to_sql("companies", conn, if_exists="append", index=False)
print(f"  Inserted {len(companies_unique):,} unique companies")

print("\n[5/5] Building relationships table...")

# Inventor → patent links
inv_links = inventors_df[["patent_id", "inventor_id"]].dropna()

# Company → patent links
comp_links = companies_df[["patent_id", "company_id"]].dropna()

# Merge on patent_id (outer join to keep all links)
relationships = inv_links.merge(comp_links, on="patent_id", how="outer")
relationships.dropna(subset=["patent_id"], inplace=True)
relationships.to_sql("patent_relationships", conn, if_exists="append", index=False)
print(f"  Inserted {len(relationships):,} relationship rows")

conn.commit()
conn.close()

print("\n" + "=" * 55)
print("  Database ready!")
print(f"  File: {DB_PATH}")
print("=" * 55)
print("\nNext step → run:  python scripts/queries.py")