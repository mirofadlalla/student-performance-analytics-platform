"""
db.py — Kayfa Analytics Dashboard
Loads pre-computed Q1–Q15 collections directly from MongoDB Atlas StudentAnalytics DB.
"""

import streamlit as st
import pandas as pd
from scipy import stats as scipy_stats

try:
    import certifi
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

# ── Secrets ─────────────────────────────────────────────────────────────────
MONGO_URI = None
DB_NAME = None

try:
    MONGO_URI = st.secrets["MONGO_URI"]
    DB_NAME = st.secrets["DB_NAME"]
except KeyError as e:
    st.error(f"Missing Streamlit secret: {e}. Configure MONGO_URI and DB_NAME in .streamlit/secrets.toml")
    st.stop()
except Exception as e:
    st.error(f"Error reading secrets: {e}")
    st.stop()

# ── Connection ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_db():
    if not MONGO_AVAILABLE:
        return None
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=8000)
        client.admin.command("ping")
        return client[DB_NAME]
    except Exception as e:
        st.error(f"MongoDB Connection Error: {e}")
        return None

def is_connected():
    return get_db() is not None

# ── Raw collection loader ────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_raw(collection_name: str) -> pd.DataFrame:
    db = get_db()
    if db is None:
        return pd.DataFrame()
    try:
        docs = list(db[collection_name].find({}, {"_id": 0}))
        return pd.DataFrame(docs) if docs else pd.DataFrame()
    except Exception as e:
        st.warning(f"Failed to load '{collection_name}': {str(e)}")
        return pd.DataFrame()

# ── Convenience loaders for each Q collection ────────────────────────────────
def q1():  return load_raw("q1_attendance_group")
def q2():  return load_raw("q2_score_dist_type")
def q3():  return load_raw("q3_avg_grade_course")
def q4():  return load_raw("q4_att_vs_grade")
def q5():  return load_raw("q5_engagement_vs_grade")
def q6():  return load_raw("q6_concept_failure_rates")
def q7():  return load_raw("q7_recursion_trend")
def q8():  return load_raw("q8_late_vs_score")
def q9_att(): return load_raw("q9_platform_trends")
def q9_eng(): return load_raw("q9_engagement_trends")
def q10(): return load_raw("q10_age_outcomes")
def q11(): return load_raw("q11_student_segments")
def q12(): return load_raw("q12_group_size_discrepancy")
def q13(): return load_raw("q13_g10_viability")
def q14(): return load_raw("q14_at_risk_ranking")
def q15(): return load_raw("q15_group_grade_trends")
def master(): return load_raw("master_student_data")

# ── Pearson r ─────────────────────────────────────────────────────────────────
def pearson_r(df, col_x, col_y):
    sub = df[[col_x, col_y]].dropna()
    if len(sub) < 3:
        return float("nan"), float("nan")
    r, p = scipy_stats.pearsonr(sub[col_x], sub[col_y])
    return round(r, 3), p

# ── Shared UI helpers ─────────────────────────────────────────────────────────
def plotly_layout(fig, title="", height=420):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#CBD5E1", family="Inter"), x=0),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94A3B8", size=12),
        legend=dict(bgcolor="rgba(11,16,32,0.8)", bordercolor="rgba(77,163,255,0.2)",
                    borderwidth=1, font=dict(size=11, color="#94A3B8")),
        xaxis=dict(gridcolor="rgba(77,163,255,0.06)", linecolor="rgba(77,163,255,0.1)",
                   tickfont=dict(color="#64748B", size=11), title_font=dict(color="#94A3B8")),
        yaxis=dict(gridcolor="rgba(77,163,255,0.06)", linecolor="rgba(77,163,255,0.1)",
                   tickfont=dict(color="#64748B", size=11), title_font=dict(color="#94A3B8")),
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(bgcolor="#0F1A33", bordercolor="rgba(77,163,255,0.3)",
                        font=dict(family="Inter", color="#E2E8F0", size=12)),
    )
    return fig

def insight_box(what, why, action):
    st.markdown(f"""
    <div class="insight-box">
      <div class="row"><span class="label">🟡 What happened:</span> {what}</div>
      <div class="row"><span class="label">🧠 Why it happened:</span> {why}</div>
      <div class="row"><span class="label">🎯 Recommendation:</span> {action}</div>
    </div>
    """, unsafe_allow_html=True)

def kpi_card(icon, value, label, trend, trend_dir="neutral"):
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-trend {trend_dir}">{trend}</div>
    </div>
    """, unsafe_allow_html=True)

def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)

def chart_card_open(title):
    st.markdown(f'<div class="chart-card"><h3>{title}</h3>', unsafe_allow_html=True)

def chart_card_close():
    st.markdown('</div>', unsafe_allow_html=True)
