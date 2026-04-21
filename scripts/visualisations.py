"""
visualizations.py
Generates data visualizations from the patents database
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

DB_PATH = "database/patents.db"
os.makedirs("reports/charts", exist_ok=True)

conn = sqlite3.connect(DB_PATH)

print("=" * 55)
print("        GENERATING PATENT VISUALIZATIONS")
print("=" * 55)

# ══════════════════════════════════════════════════════════
# FETCH DATA
# ══════════════════════════════════════════════════════════
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
# CHART 1: Top 10 Inventors (horizontal bar)
# ══════════════════════════════════════════════════════════
print("\n[1/5] Top 10 Inventors chart...")

fig, ax = plt.subplots(figsize=(12, 6))
colors = plt.cm.Blues_r([i / 10 for i in range(10)])
bars = ax.barh(top_inventors["name"][::-1], top_inventors["patents"][::-1], color=colors)

ax.set_xlabel("Number of Patents", fontsize=12)
ax.set_title("Top 10 Inventors by Patent Count", fontsize=15, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

for bar in bars:
    width = bar.get_width()
    ax.text(width + 30, bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig("reports/charts/top_inventors.png", dpi=150)
plt.close()
print("  Saved → reports/charts/top_inventors.png")

# ══════════════════════════════════════════════════════════
# CHART 2: Top 10 Companies (horizontal bar)
# ══════════════════════════════════════════════════════════
print("\n[2/5] Top 10 Companies chart...")

# Shorten long company names for display
top_companies["short_name"] = top_companies["name"].apply(
    lambda x: x[:35] + "..." if len(x) > 35 else x
)

fig, ax = plt.subplots(figsize=(12, 6))
colors = plt.cm.Oranges_r([i / 10 for i in range(10)])
bars = ax.barh(top_companies["short_name"][::-1], top_companies["patents"][::-1], color=colors)

ax.set_xlabel("Number of Patents", fontsize=12)
ax.set_title("Top 10 Companies by Patent Count", fontsize=15, fontweight="bold", pad=15)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

for bar in bars:
    width = bar.get_width()
    ax.text(width + 1000, bar.get_y() + bar.get_height() / 2,
            f"{int(width):,}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig("reports/charts/top_companies.png", dpi=150)
plt.close()
print("  Saved → reports/charts/top_companies.png")

# ══════════════════════════════════════════════════════════
# CHART 3: Top 10 Countries (pie chart)
# ══════════════════════════════════════════════════════════
print("\n[3/5] Top Countries pie chart...")

fig, ax = plt.subplots(figsize=(10, 8))
colors = plt.cm.Set3.colors[:10]
wedges, texts, autotexts = ax.pie(
    top_countries["patents"],
    labels=top_countries["country"],
    autopct="%1.1f%%",
    colors=colors,
    startangle=140,
    pctdistance=0.82
)

for text in autotexts:
    text.set_fontsize(9)

ax.set_title("Top 10 Countries by Patent Share", fontsize=15, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("reports/charts/top_countries_pie.png", dpi=150)
plt.close()
print("  Saved → reports/charts/top_countries_pie.png")

# ══════════════════════════════════════════════════════════
# CHART 4: Patents Per Year (line chart)
# ══════════════════════════════════════════════════════════
print("\n[4/5] Patents per year trend chart...")

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(yearly_trends["year"], yearly_trends["patents"],
        color="#2196F3", linewidth=2, marker="o", markersize=3)

ax.fill_between(yearly_trends["year"], yearly_trends["patents"],
                alpha=0.15, color="#2196F3")

ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Number of Patents", fontsize=12)
ax.set_title("Patent Grants Per Year (1976 — Present)", fontsize=15, fontweight="bold", pad=15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("reports/charts/patents_per_year.png", dpi=150)
plt.close()
print("  Saved → reports/charts/patents_per_year.png")

# ══════════════════════════════════════════════════════════
# CHART 5: Top Countries (bar chart)
# ══════════════════════════════════════════════════════════
print("\n[5/5] Top Countries bar chart...")

fig, ax = plt.subplots(figsize=(12, 6))
colors = plt.cm.Greens_r([i / 10 for i in range(10)])
bars = ax.bar(top_countries["country"], top_countries["patents"], color=colors)

ax.set_xlabel("Country", fontsize=12)
ax.set_ylabel("Number of Patents", fontsize=12)
ax.set_title("Top 10 Countries by Patent Count", fontsize=15, fontweight="bold", pad=15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 10000,
            f"{int(height):,}", ha="center", fontsize=8, rotation=45)

plt.tight_layout()
plt.savefig("reports/charts/top_countries_bar.png", dpi=150)
plt.close()
print("  Saved → reports/charts/top_countries_bar.png")

# ══════════════════════════════════════════════════════════
# DONE
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("  All 5 charts saved to reports/charts/")
print("=" * 55)
print("\nNext step → push charts to GitHub!")