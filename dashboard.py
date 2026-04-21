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
import numpy as np

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Patent Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0e1a;
    color: #e8eaf0;
}
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 50%, #0a1020 100%);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1400px; }

.dash-header {
    background: linear-gradient(90deg, #00d4ff10, #7b2fff10);
    border: 1px solid #00d4ff30;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.dash-header::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, #00d4ff08 0%, transparent 70%);
    pointer-events: none;
}
.dash-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #7b2fff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1.1;
}
.dash-subtitle {
    color: #8892a4; font-size: 1rem;
    margin-top: 0.5rem; font-weight: 300; letter-spacing: 0.03em;
}
.kpi-card {
    background: linear-gradient(135deg, #131929, #0f1e35);
    border: 1px solid #1e2d45;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    position: relative; overflow: hidden;
}
.kpi-card::after {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00d4ff, #7b2fff);
}
.kpi-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
.kpi-label {
    font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 0.12em; color: #5a6a82; font-weight: 500;
}
.kpi-value {
    font-family: 'Syne', sans-serif; font-size: 1.9rem;
    font-weight: 700; color: #e8eaf0; line-height: 1.1; margin: 0.2rem 0;
}
.kpi-sub { font-size: 0.78rem; color: #00d4ff; font-weight: 500; }
.section-title {
    font-family: 'Syne', sans-serif; font-size: 1.1rem;
    font-weight: 700; color: #e8eaf0; letter-spacing: 0.04em;
    margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;
}
.section-title span {
    background: linear-gradient(90deg, #00d4ff, #7b2fff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #1e2d45, transparent);
    margin: 2rem 0;
}
.stTextInput input {
    background: #131929 !important; border: 1px solid #1e2d45 !important;
    border-radius: 10px !important; color: #e8eaf0 !important;
    font-family: 'DM Sans', sans-serif !important; padding: 0.6rem 1rem !important;
}
.stTextInput input:focus {
    border-color: #00d4ff !important; box-shadow: 0 0 0 2px #00d4ff20 !important;
}
[data-testid="stSidebar"] {
    background: #0d1526 !important; border-right: 1px solid #1e2d45 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return sqlite3.connect("database/patents.db", check_same_thread=False)

conn = get_connection()

@st.cache_data
def load_total_patents():
    return pd.read_sql_query("SELECT COUNT(*) AS total FROM patents", conn).iloc[0]["total"]

@st.cache_data
def load_top_inventors(limit=10):
    return pd.read_sql_query(f"""
        SELECT i.name, COUNT(r.patent_id) AS patents
        FROM inventors i
        JOIN patent_relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id ORDER BY patents DESC LIMIT {limit}
    """, conn)

@st.cache_data
def load_top_companies(limit=10):
    return pd.read_sql_query(f"""
        SELECT c.name, COUNT(r.patent_id) AS patents
        FROM companies c
        JOIN patent_relationships r ON c.company_id = r.company_id
        GROUP BY c.company_id ORDER BY patents DESC LIMIT {limit}
    """, conn)

@st.cache_data
def load_top_countries(limit=10):
    return pd.read_sql_query(f"""
        SELECT country, COUNT(DISTINCT r.patent_id) AS patents
        FROM inventors i
        JOIN patent_relationships r ON i.inventor_id = r.inventor_id
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country ORDER BY patents DESC LIMIT {limit}
    """, conn)

@st.cache_data
def load_yearly_trends():
    return pd.read_sql_query("""
        SELECT year, COUNT(*) AS patents FROM patents
        WHERE year IS NOT NULL AND year >= 1976
        GROUP BY year ORDER BY year
    """, conn)

@st.cache_data
def search_patents(keyword):
    return pd.read_sql_query(f"""
        SELECT patent_id, title, year, patent_type
        FROM patents WHERE title LIKE '%{keyword}%' LIMIT 50
    """, conn)

def dark_style():
    plt.rcParams.update({
        "figure.facecolor": "#131929", "axes.facecolor": "#131929",
        "axes.edgecolor": "#1e2d45", "axes.labelcolor": "#8892a4",
        "xtick.color": "#5a6a82", "ytick.color": "#5a6a82",
        "text.color": "#e8eaf0", "grid.color": "#1e2d45",
        "axes.spines.top": False, "axes.spines.right": False,
    })

dark_style()

# ══════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="dash-header">
    <div class="dash-title">⚡ Global Patent Intelligence</div>
    <div class="dash-subtitle">
        Real-time analytics  &nbsp;·&nbsp; Inventors &nbsp;·&nbsp; Companies &nbsp;·&nbsp; Countries &nbsp;·&nbsp; Trends
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════
total        = int(load_total_patents())
top_inv_row  = load_top_inventors(1).iloc[0]
top_comp_row = load_top_companies(1).iloc[0]
top_ctry_row = load_top_countries(1).iloc[0]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-icon">📄</div>
        <div class="kpi-label">Total Patents</div>
        <div class="kpi-value">{total:,}</div>
        <div class="kpi-sub">USPTO dataset</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-label">Top Inventor</div>
        <div class="kpi-value" style="font-size:1.15rem">{top_inv_row['name']}</div>
        <div class="kpi-sub">{int(top_inv_row['patents']):,} patents</div>
    </div>""", unsafe_allow_html=True)
with c3:
    short = top_comp_row['name'][:22] + "…" if len(top_comp_row['name']) > 22 else top_comp_row['name']
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-icon">🏢</div>
        <div class="kpi-label">Top Company</div>
        <div class="kpi-value" style="font-size:1.05rem">{short}</div>
        <div class="kpi-sub">{int(top_comp_row['patents']):,} patents</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-icon">🌍</div>
        <div class="kpi-label">Top Country</div>
        <div class="kpi-value">{top_ctry_row['country']}</div>
        <div class="kpi-sub">{int(top_ctry_row['patents']):,} patents</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
st.sidebar.markdown("### ⚙️ Controls")
top_n      = st.sidebar.slider("Results to show", 5, 20, 10)
yearly     = load_yearly_trends()
year_min   = int(yearly["year"].min())
year_max   = int(yearly["year"].max())
year_range = st.sidebar.slider("Year range", year_min, year_max, (year_min, year_max))
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#5a6a82'>Data: USPTO PatentsView<br>1M patents · 1976–present</small>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ROW 1: Inventors + Companies
# ══════════════════════════════════════════════════════════
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.markdown('<div class="section-title">🏆 <span>Top Inventors</span></div>', unsafe_allow_html=True)
    inventors = load_top_inventors(top_n)
    fig, ax = plt.subplots(figsize=(8, max(4, top_n * 0.55)))
    colors = [plt.cm.cool(0.2 + 0.6 * i / top_n) for i in range(top_n)]
    ax.barh(inventors["name"][::-1], inventors["patents"][::-1], color=colors, height=0.65, edgecolor="none")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Patents", fontsize=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

with col_r:
    st.markdown('<div class="section-title">🏢 <span>Top Companies</span></div>', unsafe_allow_html=True)
    companies = load_top_companies(top_n)
    companies["short_name"] = companies["name"].apply(lambda x: x[:28] + "…" if len(x) > 28 else x)
    fig, ax = plt.subplots(figsize=(8, max(4, top_n * 0.55)))
    colors = [plt.cm.autumn_r(0.1 + 0.7 * i / top_n) for i in range(top_n)]
    ax.barh(companies["short_name"][::-1], companies["patents"][::-1], color=colors, height=0.65, edgecolor="none")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Patents", fontsize=10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ROW 2: Trend + Countries
# ══════════════════════════════════════════════════════════
col_l2, col_r2 = st.columns([3, 2], gap="large")

with col_l2:
    st.markdown('<div class="section-title">📈 <span>Patents Per Year</span></div>', unsafe_allow_html=True)
    filtered = yearly[(yearly["year"] >= year_range[0]) & (yearly["year"] <= year_range[1])]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = filtered["year"].values
    y = filtered["patents"].values
    ax.plot(x, y, color="#00d4ff", linewidth=2.5, zorder=3)
    ax.fill_between(x, y, alpha=0.12, color="#00d4ff")
    peak_idx = np.argmax(y)
    ax.scatter(x[peak_idx], y[peak_idx], color="#7b2fff", s=80, zorder=5)
    ax.annotate(f"Peak: {int(y[peak_idx]):,}",
                xy=(x[peak_idx], y[peak_idx]), xytext=(10, 10),
                textcoords="offset points", color="#7b2fff", fontsize=9, fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_xlabel("Year", fontsize=10)
    ax.set_ylabel("Patents Granted", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

with col_r2:
    st.markdown('<div class="section-title">🌍 <span>Countries</span></div>', unsafe_allow_html=True)
    countries = load_top_countries(top_n)
    fig, ax = plt.subplots(figsize=(5, 5))
    colors = ["#00d4ff","#7b2fff","#ff6b6b","#ffd93d","#6bcb77",
              "#4d96ff","#ff922b","#cc5de8","#20c997","#f06595"][:top_n]
    wedges, texts, autotexts = ax.pie(
        countries["patents"], labels=countries["country"], autopct="%1.1f%%",
        colors=colors, startangle=140, pctdistance=0.78,
        wedgeprops={"edgecolor": "#0a0e1a", "linewidth": 2}
    )
    for t in texts:
        t.set_color("#8892a4"); t.set_fontsize(9)
    for at in autotexts:
        at.set_color("#e8eaf0"); at.set_fontsize(8); at.set_fontweight("bold")
    centre = plt.Circle((0, 0), 0.55, fc="#131929")
    ax.add_patch(centre)
    ax.text(0, 0, "🌍", ha="center", va="center", fontsize=20)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# DATA TABLES
# ══════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 <span>Data Tables</span></div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🏆 Inventors", "🏢 Companies", "🌍 Countries"])
with tab1:
    df = load_top_inventors(top_n).reset_index(drop=True); df.index += 1
    st.dataframe(df, use_container_width=True)
with tab2:
    df = load_top_companies(top_n)[["name","patents"]].reset_index(drop=True); df.index += 1
    st.dataframe(df, use_container_width=True)
with tab3:
    df = load_top_countries(top_n).reset_index(drop=True); df.index += 1
    st.dataframe(df, use_container_width=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PATENT SEARCH
# ══════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 <span>Search Patents</span></div>', unsafe_allow_html=True)
keyword = st.text_input("", placeholder="Type a keyword e.g. 'battery', 'solar', 'AI', 'camera'...")
if keyword:
    results = search_patents(keyword)
    if len(results) == 0:
        st.warning(f"No patents found for **{keyword}**")
    else:
        st.success(f"Found **{len(results)}** patents matching **'{keyword}'**")
        st.dataframe(results, use_container_width=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("<center><small style='color:#2a3a52'>⚡ Global Patent Intelligence · USPTO PatentsView · Built with Python + Streamlit</small></center>", unsafe_allow_html=True)