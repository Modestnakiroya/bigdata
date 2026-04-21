"""
queries.py
Runs all 7 required SQL queries against the patents database
"""

import sqlite3
import pandas as pd

DB_PATH = "database/patents.db"
conn = sqlite3.connect(DB_PATH)

print("=" * 55)
print("           PATENT SQL QUERIES (Q1 - Q7)")
print("=" * 55)

# ══════════════════════════════════════════════════════════
# Q1: Top Inventors (who has the most patents?)
# ══════════════════════════════════════════════════════════
print("\nQ1: TOP INVENTORS")
q1 = pd.read_sql_query("""
    SELECT i.name, COUNT(r.patent_id) AS patent_count
    FROM inventors i
    JOIN patent_relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)
print(q1.to_string(index=False))

# ══════════════════════════════════════════════════════════
# Q2: Top Companies (which companies own the most patents?)
# ══════════════════════════════════════════════════════════
print("\nQ2: TOP COMPANIES")
q2 = pd.read_sql_query("""
    SELECT c.name, COUNT(r.patent_id) AS patent_count
    FROM companies c
    JOIN patent_relationships r ON c.company_id = r.company_id
    GROUP BY c.company_id
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)
print(q2.to_string(index=False))

# ══════════════════════════════════════════════════════════
# Q3: Top Countries (which countries produce the most patents?)
# ══════════════════════════════════════════════════════════
print("\nQ3: TOP COUNTRIES")
q3 = pd.read_sql_query("""
    SELECT country, COUNT(DISTINCT r.patent_id) AS patent_count
    FROM inventors i
    JOIN patent_relationships r ON i.inventor_id = r.inventor_id
    WHERE country IS NOT NULL AND country != ''
    GROUP BY country
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)
print(q3.to_string(index=False))

# ══════════════════════════════════════════════════════════
# Q4: Trends Over Time (patents per year)
# ══════════════════════════════════════════════════════════
print("\nQ4: PATENTS PER YEAR")
q4 = pd.read_sql_query("""
    SELECT year, COUNT(*) AS patent_count
    FROM patents
    WHERE year IS NOT NULL AND year >= 1976
    GROUP BY year
    ORDER BY year
""", conn)
print(q4.to_string(index=False))

# ══════════════════════════════════════════════════════════
# Q5: JOIN Query (patents + inventors + companies)
# ══════════════════════════════════════════════════════════
print("\nQ5: JOIN - PATENTS WITH INVENTORS AND COMPANIES")
q5 = pd.read_sql_query("""
    SELECT 
        p.patent_id,
        p.title,
        p.year,
        i.name  AS inventor_name,
        c.name  AS company_name
    FROM patents p
    JOIN patent_relationships r ON p.patent_id = r.patent_id
    JOIN inventors i            ON r.inventor_id = i.inventor_id
    JOIN companies c            ON r.company_id  = c.company_id
    LIMIT 10
""", conn)
print(q5.to_string(index=False))

# ══════════════════════════════════════════════════════════
# Q6: CTE Query (top inventors per country)
# ══════════════════════════════════════════════════════════
print("\nQ6: CTE - TOP INVENTOR PER COUNTRY")
q6 = pd.read_sql_query("""
    WITH inventor_counts AS (
        SELECT 
            i.name,
            i.country,
            COUNT(r.patent_id) AS patent_count
        FROM inventors i
        JOIN patent_relationships r ON i.inventor_id = r.inventor_id
        WHERE i.country IS NOT NULL AND i.country != ''
        GROUP BY i.inventor_id
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY country ORDER BY patent_count DESC) AS rank
        FROM inventor_counts
    )
    SELECT name, country, patent_count
    FROM ranked
    WHERE rank = 1
    ORDER BY patent_count DESC
    LIMIT 10
""", conn)
print(q6.to_string(index=False))

# ══════════════════════════════════════════════════════════
# Q7: Ranking Query (rank inventors using window functions)
# ══════════════════════════════════════════════════════════
print("\nQ7: WINDOW FUNCTION - RANKED INVENTORS")
q7 = pd.read_sql_query("""
    SELECT 
        name,
        patent_count,
        RANK()       OVER (ORDER BY patent_count DESC) AS rank,
        DENSE_RANK() OVER (ORDER BY patent_count DESC) AS dense_rank,
        NTILE(4)     OVER (ORDER BY patent_count DESC) AS quartile
    FROM (
        SELECT i.name, COUNT(r.patent_id) AS patent_count
        FROM inventors i
        JOIN patent_relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id
        ORDER BY patent_count DESC
        LIMIT 100
    )
    LIMIT 20
""", conn)
print(q7.to_string(index=False))

conn.close()
print("\n" + "=" * 55)
print("  All queries complete!")
print("=" * 55)
print("\nNext step → run:  python scripts/report.py")