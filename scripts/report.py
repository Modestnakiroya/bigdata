"""
report.py
Generates console report, CSV files, and JSON report
"""

import sqlite3
import pandas as pd
import json
import os

DB_PATH = "database/patents.db"
os.makedirs("reports", exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# ══════════════════════════════════════════════════════════
# FETCH DATA
# ══════════════════════════════════════════════════════════

total_patents = pd.read_sql_query("SELECT COUNT(*) AS total FROM patents", conn).iloc[0]["total"]

top_inventors = pd.read_sql_query("""
    SELECT i.name, COUNT(r.patent_id) AS patents
    FROM inventors i
    JOIN patent_relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id
    ORDER BY patents DESC
    LIMIT 10
""", conn)

top_companies = pd.read_sql_query("""
    SELECT c.name, COUNT(r.patent_id) AS patents
    FROM companies c
    JOIN patent_relationships r ON c.company_id = r.company_id
    GROUP BY c.company_id
    ORDER BY patents DESC
    LIMIT 10
""", conn)

top_countries = pd.read_sql_query("""
    SELECT country, COUNT(DISTINCT r.patent_id) AS patents
    FROM inventors i
    JOIN patent_relationships r ON i.inventor_id = r.inventor_id
    WHERE country IS NOT NULL AND country != ''
    GROUP BY country
    ORDER BY patents DESC
    LIMIT 10
""", conn)

yearly_trends = pd.read_sql_query("""
    SELECT year, COUNT(*) AS patents
    FROM patents
    WHERE year IS NOT NULL AND year >= 1976
    GROUP BY year
    ORDER BY year
""", conn)

conn.close()

# ══════════════════════════════════════════════════════════
# A. CONSOLE REPORT
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 52)
print("           GLOBAL PATENT INTELLIGENCE REPORT")
print("=" * 52)
print(f"\n  Total Patents: {int(total_patents):,}")

print("\n  TOP 10 INVENTORS:")
for i, row in top_inventors.iterrows():
    print(f"    {i+1}. {row['name']} — {int(row['patents']):,} patents")

print("\n  TOP 10 COMPANIES:")
for i, row in top_companies.iterrows():
    print(f"    {i+1}. {row['name']} — {int(row['patents']):,} patents")

print("\n  TOP 10 COUNTRIES:")
for i, row in top_countries.iterrows():
    print(f"    {i+1}. {row['country']} — {int(row['patents']):,} patents")

print("\n  PATENTS PER YEAR (last 10 years):")
for _, row in yearly_trends.tail(10).iterrows():
    print(f"    {int(row['year'])}: {int(row['patents']):,}")

print("\n" + "=" * 52)

# ══════════════════════════════════════════════════════════
# B. CSV REPORTS
# ══════════════════════════════════════════════════════════
top_inventors.to_csv("reports/top_inventors.csv",   index=False)
top_companies.to_csv("reports/top_companies.csv",   index=False)
top_countries.to_csv("reports/country_trends.csv",  index=False)
yearly_trends.to_csv("reports/yearly_trends.csv",   index=False)

print("\n  CSV files saved:")
print("    reports/top_inventors.csv")
print("    reports/top_companies.csv")
print("    reports/country_trends.csv")
print("    reports/yearly_trends.csv")

# ══════════════════════════════════════════════════════════
# C. JSON REPORT
# ══════════════════════════════════════════════════════════
total = int(total_patents)

report = {
    "total_patents": total,
    "top_inventors": [
        {"rank": i+1, "name": row["name"], "patents": int(row["patents"])}
        for i, row in top_inventors.iterrows()
    ],
    "top_companies": [
        {"rank": i+1, "name": row["name"], "patents": int(row["patents"])}
        for i, row in top_companies.iterrows()
    ],
    "top_countries": [
        {
            "rank": i+1,
            "country": row["country"],
            "patents": int(row["patents"]),
            "share": round(int(row["patents"]) / total, 4)
        }
        for i, row in top_countries.iterrows()
    ],
    "yearly_trends": [
        {"year": int(row["year"]), "patents": int(row["patents"])}
        for _, row in yearly_trends.iterrows()
    ]
}

with open("reports/patent_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("    reports/patent_report.json")
print("\n" + "=" * 52)
print("  All reports generated successfully!")
print("=" * 52)
print("\nNext step → push everything to GitHub!")