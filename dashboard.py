"""
dashboard.py
Interactive Streamlit dashboard for Global Patent Intelligence
Run with: streamlit run dashboard.py
"""

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Global Patent Intelligence",
    page_icon="🔬",
    layout="wide"
)

# ── Database connection ───────────────────────────────────
@st.cache_resource
def get_connection():
    return sqlite3.connect("database/patents.db", check_same_thread=False)

conn = get_connection()

# ── Data loaders (cached) ─────────────────────────────────
@st.cache_data
def load_total_patents():
    return pd.read_sql_query("SELECT COUNT(*) AS total FROM patents", conn).iloc[0]["total"]

@st.cache_data
def load_top_inventors(limit=10):
    return pd.read_sql_query(f"""
        SELECT i.name, COUNT(r.patent_id) AS patents
        FROM inventors i
        JOIN patent_relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id
        ORDER BY patents DESC
        LIMIT {limit}
    """, conn)

@st.cache_data
def load_top_companies(limit=10):
    return pd.read_sql_query(f"""
        SELECT c.name, COUNT(r.patent_id) AS patents
        FROM companies c
        JOIN patent_relationships r ON c.company_id = r.company_id
        GROUP BY c.company_id
        ORDER BY patents DESC
        LIMIT {limit}
    """, conn)

@st.cache_data
def load_top_countries(limit=10):
    return pd.read_sql_query(f"""
        SELECT country, COUNT(DISTINCT r.patent_id) AS patents
        FROM inventors i
        JOIN patent_relationships r ON i.inventor_id = r.inventor_id
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country
        ORDER BY patents DESC
        LIMIT {limit}
    """, conn)

@st.cache_data
def load_yearly_trends():
    return pd.read_sql_query("""
        SELECT year, COUNT(*) AS patents
        FROM patents
        WHERE year IS NOT NULL AND year >= 1976
        GROUP BY year
        ORDER BY year
    """, conn)

@st.cache_data
def search_patents(keyword):
    return pd.read_sql_query(f"""
        SELECT patent_id, title, year, patent_type
        FROM patents
        WHERE title LIKE '%{keyword}%'
        LIMIT 50
    """, conn)

# ══════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════
st.title("🔬 Global Patent Intelligence Dashboard")
st.markdown("Analyzing **1,000,000 patents** from the USPTO PatentsView dataset")
st.divider()

# ══════════════════════════════════════════════════════════
# KPI METRICS ROW
# ══════════════════════════════════════════════════════════
total = int(load_total_patents())
top_inv = load_top_inventors(1)
top_comp = load_top_companies(1)
top_country = load_top_countries(1)

col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Total Patents",     f"{total:,}")
col2.metric("🏆 Top Inventor",      top_inv.iloc[0]["name"].split()[-1])
col3.metric("🏢 Top Company",       top_comp.iloc[0]["name"][:20] + "...")
col4.metric("🌍 Top Country",       top_country.iloc[0]["country"])

st.divider()

# ══════════════════════════════════════════════════════════
# SIDEBAR FILTERS
# ══════════════════════════════════════════════════════════
st.sidebar.title("⚙️ Filters")
top_n = st.sidebar.slider("Number of results to show", 5, 20, 10)

# ══════════════════════════════════════════════════════════
# ROW 1: Inventors + Companies
# ══════════════════════════════════════════════════════════
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 Top Inventors")
    inventors = load_top_inventors(top_n)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.Blues_r([i / top_n for i in range(top_n)])
    ax.barh(inventors["name"][::-1], inventors["patents"][::-1], color=colors)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Patents")
    ax.set_title(f"Top {top_n} Inventors", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.dataframe(inventors.reset_index(drop=True), use_container_width=True)

with col_right:
    st.subheader("🏢 Top Companies")
    companies = load_top_companies(top_n)
    companies["short_name"] = companies["name"].apply(
        lambda x: x[:30] + "..." if len(x) > 30 else x
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.Oranges_r([i / top_n for i in range(top_n)])
    ax.barh(companies["short_name"][::-1], companies["patents"][::-1], color=colors)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Patents")
    ax.set_title(f"Top {top_n} Companies", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.dataframe(companies[["name", "patents"]].reset_index(drop=True), use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════
# ROW 2: Countries + Yearly Trend
# ══════════════════════════════════════════════════════════
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("🌍 Top Countries")
    countries = load_top_countries(top_n)

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.Set3.colors[:top_n]
    ax.pie(
        countries["patents"],
        labels=countries["country"],
        autopct="%1.1f%%",
        colors=colors,
        startangle=140
    )
    ax.set_title(f"Top {top_n} Countries by Patent Share", fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.dataframe(countries.reset_index(drop=True), use_container_width=True)

with col_right2:
    st.subheader("📈 Patents Per Year")
    yearly = load_yearly_trends()

    year_min = int(yearly["year"].min())
    year_max = int(yearly["year"].max())
    year_range = st.sidebar.slider(
        "Year range", year_min, year_max, (year_min, year_max)
    )

    filtered = yearly[
        (yearly["year"] >= year_range[0]) &
        (yearly["year"] <= year_range[1])
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(filtered["year"], filtered["patents"], color="#2196F3", linewidth=2)
    ax.fill_between(filtered["year"], filtered["patents"], alpha=0.15, color="#2196F3")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Year")
    ax.set_ylabel("Patents")
    ax.set_title("Patent Grants Over Time", fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.divider()

# ══════════════════════════════════════════════════════════
# PATENT SEARCH
# ══════════════════════════════════════════════════════════
st.subheader("🔍 Search Patents by Keyword")
keyword = st.text_input("Enter a keyword (e.g. 'battery', 'solar', 'AI')")

if keyword:
    results = search_patents(keyword)
    if len(results) == 0:
        st.warning("No patents found for that keyword.")
    else:
        st.success(f"Found {len(results)} patents matching '{keyword}'")
        st.dataframe(results, use_container_width=True)

st.divider()
st.caption("Data source: USPTO PatentsView | Built with Python, SQLite, pandas, matplotlib, Streamlit")