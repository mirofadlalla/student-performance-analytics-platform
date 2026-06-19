import streamlit as st
import sys, os
import scipy.stats as stats
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Kayfa Student Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────────────────────────────────
# THEME TOGGLE & PERSISTENCE
# ────────────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Render selector in sidebar (at the very bottom or top)
# We place it at the top for easy toggle access
theme_choice = st.sidebar.selectbox(
    "Appearance 🎨",
    ["Dark Theme 🌙", "Light Theme ☀️"],
    index=0 if st.session_state.theme == "dark" else 1
)
st.session_state.theme = "dark" if "Dark" in theme_choice else "light"
theme = st.session_state.theme

# Theme configurations
if theme == "light":
    bg_gradient = "linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 60%, #E2E8F0 100%)"
    text_primary = "#0F172A"
    text_secondary = "#334155"
    text_muted = "#64748B"
    border_color = "rgba(15, 23, 42, 0.12)"
    border_hover = "rgba(37, 99, 235, 0.4)"
    card_bg = "rgba(255, 255, 255, 0.85)"
    sidebar_bg = "#F1F5F9"
    primary_accent = "#2563EB"
    secondary_accent = "#7C3AED"
    kpi_value_color = "#1E293B"
    insight_box_bg = "linear-gradient(135deg, rgba(37,99,235,0.06) 0%, rgba(124,58,237,0.06) 100%)"
else:
    bg_gradient = "linear-gradient(135deg, #0B1020 0%, #0F1A33 60%, #0D1526 100%)"
    text_primary = "#F1F5F9"
    text_secondary = "#CBD5E1"
    text_muted = "#94A3B8"
    border_color = "rgba(77, 163, 255, 0.18)"
    border_hover = "rgba(77, 163, 255, 0.45)"
    card_bg = "rgba(11, 16, 32, 0.75)"
    sidebar_bg = "#0B1020"
    primary_accent = "#4DA3FF"
    secondary_accent = "#8B5CF6"
    kpi_value_color = "#F8FAFC"
    insight_box_bg = "linear-gradient(135deg, rgba(77,163,255,0.04) 0%, rgba(139,92,246,0.04) 100%)"

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  :root {{
    --bg-gradient: {bg_gradient};
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
    --text-muted: {text_muted};
    --border-color: {border_color};
    --border-hover: {border_hover};
    --card-bg: {card_bg};
    --sidebar-bg: {sidebar_bg};
    --primary-accent: {primary_accent};
    --secondary-accent: {secondary_accent};
    --kpi-value-color: {kpi_value_color};
    --insight-box-bg: {insight_box_bg};
  }}

  html, body, [data-testid="stAppViewContainer"] {{
    background: var(--bg-gradient) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
  }}
  [data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
      linear-gradient(rgba(77,163,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(77,163,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }}
  
  /* Sidebar style overrides */
  [data-testid="stSidebar"] {{
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border-color) !important;
  }}
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: var(--text-secondary) !important;
  }}

  .main .block-container {{
    padding-top: 1rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1400px !important;
  }}

  /* Header & Footer styling */
  .app-header {{
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--primary-accent);
    text-align: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 25px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }}
  .app-footer {{
    font-size: 0.8rem;
    color: var(--text-muted);
    text-align: center;
    padding: 20px 0;
    border-top: 1px solid var(--border-color);
    margin-top: 40px;
    letter-spacing: 0.05em;
  }}

  /* Hero */
  .hero-banner {{
    background: var(--insight-box-bg);
    border: 1px solid var(--border-color);
    border-radius: 20px; padding: 36px 40px; margin-bottom: 32px;
    position: relative; overflow: hidden;
  }}
  .hero-banner h1 {{
    font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(135deg, var(--primary-accent) 0%, var(--secondary-accent) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 8px 0; letter-spacing: -0.02em;
  }}
  .hero-banner p {{ color: var(--text-secondary); font-size:.95rem; margin:0; }}
  .hero-meta {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:20px; }}
  .hero-badge {{
    background: rgba(77,163,255,.05); border: 1px solid var(--border-color);
    border-radius:8px; padding:6px 14px; font-size:.78rem; color: var(--primary-accent); font-weight:600;
  }}

  /* KPI Cards */
  .kpi-card {{
    background: var(--card-bg);
    border:1px solid var(--border-color); border-radius:14px;
    padding:20px 22px; position:relative; overflow:hidden; transition:all .3s ease;
  }}
  .kpi-card:hover {{ border-color: var(--border-hover); box-shadow:0 0 24px rgba(77,163,255,.12); transform:translateY(-2px); }}
  .kpi-card::after {{ content:""; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg, var(--primary-accent), var(--secondary-accent)); }}
  .kpi-icon  {{ font-size:1.5rem; margin-bottom:10px; }}
  .kpi-value {{ font-size:2rem; font-weight:700; color: var(--kpi-value-color); line-height:1; }}
  .kpi-label {{ font-size:.73rem; color: var(--text-muted); font-weight:500; text-transform:uppercase; letter-spacing:.08em; margin-top:5px; }}
  .kpi-trend {{ font-size:.78rem; margin-top:8px; font-weight:500; }}
  .kpi-trend.up   {{ color:#22D3EE; }}
  .kpi-trend.down {{ color:#F87171; }}
  .kpi-trend.neutral {{ color: var(--text-muted); }}

  /* Question header */
  .q-header {{ display:flex; align-items:center; gap:12px; border-bottom:1px solid var(--border-color); padding-bottom:16px; margin-bottom:20px; }}
  .q-badge  {{ background:linear-gradient(135deg, var(--primary-accent), var(--secondary-accent)); border-radius:8px; padding:6px 12px; font-size:.78rem; font-weight:700; color:#fff; white-space:nowrap; }}
  .q-title  {{ font-size:1.2rem; font-weight:600; color: var(--text-primary); }}
  .q-desc   {{ font-size:0.95rem; color: var(--text-secondary); font-style:italic; margin-bottom:15px; }}

  /* Chart card */
  .chart-card {{ background: var(--card-bg); border:1px solid var(--border-color); border-radius:16px; padding:24px; margin-bottom:20px; backdrop-filter:blur(10px); }}
  .chart-card h3 {{ font-size:1rem; font-weight:600; color: var(--text-primary); margin:0 0 16px 0; border-bottom:1px solid var(--border-color); padding-bottom:12px; }}

  /* Insight box */
  .insight-box {{ background: var(--insight-box-bg); border:1px solid var(--border-color); border-left:3px solid var(--primary-accent); border-radius:10px; padding:16px 20px; margin-top:12px; font-size:.85rem; line-height:1.6; }}
  .insight-box .row {{ margin-bottom:7px; color: var(--text-primary); }}
  .insight-box .row:last-child {{ margin-bottom:0; }}
  .insight-box span.label {{ font-weight:600; margin-right:6px; color: var(--text-primary); }}

  /* Section title */
  .section-title {{ font-size:.78rem; font-weight:600; color: var(--primary-accent); text-transform:uppercase; letter-spacing:.12em; margin-bottom:16px; margin-top:8px; }}

  /* Tables / metrics */
  [data-testid="stDataFrame"] {{ border-radius:12px; overflow:hidden; border: 1px solid var(--border-color); }}
  [data-testid="stMetric"] {{ background: var(--card-bg); border:1px solid var(--border-color); border-radius:12px; padding:16px; }}
  [data-testid="stMetric"] label {{ color: var(--text-secondary) !important; font-size:.78rem !important; }}
  [data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: var(--text-primary) !important; }}

  /* Misc */
  ::-webkit-scrollbar {{ width:6px; height:6px; }}
  ::-webkit-scrollbar-track {{ background: var(--sidebar-bg); }}
  ::-webkit-scrollbar-thumb {{ background:rgba(77,163,255,.3); border-radius:3px; }}
  .js-plotly-plot .plotly {{ background:transparent !important; }}
  hr {{ border-color: var(--border-color) !important; margin:24px 0 !important; }}
</style>
""", unsafe_allow_html=True)

from db import (
    q1, q2, q3, q4, q5, q6, q7, q8, q9_att, q9_eng, q10,
    q11, q12, q13, q14, q15, master,
    insight_box, kpi_card, section_title,
    chart_card_open, chart_card_close, pearson_r, is_connected
)

BLUE   = "#4DA3FF"
PURPLE = "#8B5CF6"
CYAN   = "#22D3EE"
RED    = "#F87171"
AMBER  = "#FBD24C"
GREEN  = "#4ADE80"

# ────────────────────────────────────────────────────────────────────────────
# PLOTLY THEMED LAYOUT
# ────────────────────────────────────────────────────────────────────────────
def theme_plotly_layout(fig, title="", height=420):
    is_light = (st.session_state.theme == "light")
    text_color = "#334155" if is_light else "#E2E8F0"
    grid_color = "rgba(15, 23, 42, 0.06)" if is_light else "rgba(77, 163, 255, 0.06)"
    line_color = "rgba(15, 23, 42, 0.1)" if is_light else "rgba(77, 163, 255, 0.1)"
    bg_color = "rgba(255,255,255,0.85)" if is_light else "#0F1A33"
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=text_color, family="Inter"), x=0),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=text_color, size=12),
        legend=dict(bgcolor=bg_color, bordercolor=line_color,
                    borderwidth=1, font=dict(size=11, color=text_color)),
        xaxis=dict(gridcolor=grid_color, linecolor=line_color,
                   tickfont=dict(color=text_color, size=11), title_font=dict(color=text_color)),
        yaxis=dict(gridcolor=grid_color, linecolor=line_color,
                   tickfont=dict(color=text_color, size=11), title_font=dict(color=text_color)),
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(bgcolor=bg_color, bordercolor=line_color,
                        font=dict(family="Inter", color=text_color, size=12)),
    )
    return fig

# ────────────────────────────────────────────────────────────────────────────
# SIDEBAR LOGO & TITLE
# ────────────────────────────────────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(__file__), "logo", "Screenshot 2026-06-19 171627.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)

st.sidebar.markdown("<h3 style='text-align: center; color: var(--primary-accent); margin-top: 0;'>Kayfa — كيف</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 0.8rem; margin-top: -10px; color: var(--text-muted);'>Week 2 &middot; Evaluation Dashboard</p>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='margin: 10px 0; border-color: var(--border-color);'>", unsafe_allow_html=True)

# Navigation
questions_dict = {
    "📊 Overview & KPIs": "overview",
    "Q1: Attendance Rate per Group": "q1",
    "Q2: Score Distribution by Assessment Type": "q2",
    "Q3: Average Grade by Course": "q3",
    "Q4: Attendance vs Grade Correlation": "q4",
    "Q5: Engagement vs Academic Performance": "q5",
    "Q6: Highest Concept Failure Rates": "q6",
    "Q7: Worst Concept Mastery Over Time": "q7",
    "Q8: Late Submissions vs Score": "q8",
    "Q9: Attendance & Engagement Over Time": "q9",
    "Q10: Age Bands vs Outcomes": "q10",
    "Q11: Student Segmentation (K-Means)": "q11",
    "Q12: True Group Sizes vs Stated": "q12",
    "Q13: Non-Viable Group Analysis": "q13",
    "Q14: At-Risk Student Ranking": "q14",
    "Q15: Group Grade Trends Across Term": "q15"
}

selected_q_label = st.sidebar.radio("Select Analytics Section", list(questions_dict.keys()))
selected_q = questions_dict[selected_q_label]

# ────────────────────────────────────────────────────────────────────────────
# CONNECTION STATUS & DATA LOADING
# ────────────────────────────────────────────────────────────────────────────
db_ok = is_connected()
db_status = "🟢 Live" if db_ok else "🔴 Offline"

if not db_ok:
    st.error("⚠️ Cannot connect to MongoDB Atlas. Check MONGO_URI and DB_NAME in .streamlit/secrets.toml")
    st.stop()

@st.cache_data(ttl=300, show_spinner=False)
def load_all_data():
    return {
        "df_master": master(),
        "df_q1": q1(),
        "df_q2": q2(),
        "df_q3": q3(),
        "df_q4": q4(),
        "df_q5": q5(),
        "df_q6": q6(),
        "df_q7": q7(),
        "df_q8": q8(),
        "df_q9a": q9_att(),
        "df_q9b": q9_eng(),
        "df_q10": q10(),
        "df_q11": q11(),
        "df_q12": q12(),
        "df_q13": q13(),
        "df_q14": q14(),
        "df_q15": q15()
    }

with st.spinner("Syncing analytics intelligence from MongoDB Atlas…"):
    data = load_all_data()

# ────────────────────────────────────────────────────────────────────────────
# RENDER CONTENT BY SELECTED NAVIGATION option
# ────────────────────────────────────────────────────────────────────────────
if selected_q == "overview":
    # HERO HEADER
    st.markdown(f"""
    <div class="hero-banner">
      <h1>🎓 Kayfa Student Analytics</h1>
      <p>15-Question Intelligence Report · Attendance · Grades · Engagement · Risk Segmentation · Curriculum Gaps</p>
      <div class="hero-meta">
        <div class="hero-badge">📡 {db_status} · MongoDB Atlas</div>
        <div class="hero-badge">🗄️ StudentAnalytics DB</div>
        <div class="hero-badge">📊 15 Research Questions</div>
        <div class="hero-badge">👥 500 Students · 12 Groups</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # PLATFORM KPIs — from master_student_data
    section_title("PLATFORM OVERVIEW — KEY METRICS")
    df_master = data["df_master"]
    if not df_master.empty:
        total_s      = len(df_master)
        avg_grade    = round(df_master["avg_grade"].mean(), 1)
        avg_att      = round(df_master["att_rate_pct"].mean(), 1)
        failing_n    = int((df_master["avg_grade"] < 60).sum())
        passing_pct  = round((df_master["avg_grade"] >= 60).sum() / total_s * 100, 1)

        cols_kpi = st.columns(5)
        for col, (icon, val, label, trend, dir_) in zip(cols_kpi, [
            ("👥", str(total_s),       "Total Students",    "Active cohort",    "neutral"),
            ("📊", str(avg_grade),     "Platform Avg Grade","All students",     "up"),
            ("📅", f"{avg_att}%",      "Avg Attendance",    "Platform-wide",    "neutral"),
            ("⚠️", str(failing_n),    "Failing Students",  "Grade < 60",       "down"),
            ("✅", f"{passing_pct}%",  "Pass Rate",         "Grade ≥ 60",       "up"),
        ]):
            with col:
                kpi_card(icon, val, label, trend, dir_)
                
        # ── OVERVIEW CHARTS ─────────────────────────────────────────────────
        st.markdown("<hr>", unsafe_allow_html=True)
        section_title("📊 KEY PERFORMANCE INSIGHTS")
        
        c_insights_a, c_insights_b = st.columns(2)
        
        with c_insights_a:
            df_q1 = data["df_q1"]
            if not df_q1.empty:
                chart_card_open("Group Attendance Rates")
                df_q1s = df_q1.sort_values("att_rate_pct")
                plat_att = 77.3
                fig1 = go.Figure(go.Bar(
                    x=df_q1s["true_group"], y=df_q1s["att_rate_pct"],
                    marker_color=[RED if v else BLUE for v in df_q1s["below_avg"]],
                    text=df_q1s["att_rate_pct"].round(1).astype(str) + "%",
                    textposition="outside",
                    textfont=dict(size=11, color=text_primary),
                ))
                fig1.add_hline(y=plat_att, line_dash="dash", line_color=AMBER, line_width=1.5)
                fig1 = theme_plotly_layout(fig1, height=320)
                fig1.update_yaxes(range=[0, 100])
                st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
                chart_card_close()
                
        with c_insights_b:
            df_q3 = data["df_q3"]
            if not df_q3.empty:
                chart_card_open("Average Grade by Course")
                df_q3s = df_q3.sort_values("mean")
                fig3 = go.Figure(go.Bar(
                    x=df_q3s["course_name"], y=df_q3s["mean"],
                    error_y=dict(type="data", array=df_q3s["std"].tolist(), visible=True, color="#475569"),
                    marker_color=BLUE,
                    text=df_q3s["mean"].round(1).astype(str),
                    textposition="outside",
                    textfont=dict(size=11, color=text_primary),
                ))
                fig3.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1)
                fig3 = theme_plotly_layout(fig3, height=320)
                fig3.update_yaxes(range=[40, 90])
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
                chart_card_close()

        st.markdown("<hr>", unsafe_allow_html=True)
        section_title("📈 COHORT TRENDS OVER TIME")
        df_q9a = data["df_q9a"]
        df_q9b = data["df_q9b"]
        if not df_q9a.empty and not df_q9b.empty:
            chart_card_open("Monthly Attendance & Engagement Trend")
            df_q9as = df_q9a.sort_values("month")
            df_q9bs = df_q9b.sort_values("month")
            
            from plotly.subplots import make_subplots
            fig9 = make_subplots(rows=2, cols=1, subplot_titles=('Monthly Attendance Rate', 'Monthly Engagement Events'), shared_xaxes=True)
            
            fig9.add_trace(go.Scatter(
                x=df_q9as['month'], y=df_q9as['att_rate'],
                mode='lines+markers', name='Attendance %', line=dict(color=BLUE, width=2.5)
            ), row=1, col=1)
            
            fig9.add_trace(go.Bar(
                x=df_q9bs['month'], y=df_q9bs['events'],
                name='Total Events', marker_color=RED
            ), row=2, col=1)
            
            fig9 = theme_plotly_layout(fig9, height=400)
            st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})
            chart_card_close()

        st.markdown("<hr>", unsafe_allow_html=True)
        section_title("🎯 SEGMENTS & STUDENT RISK")
        
        c_risk_a, c_risk_b = st.columns([1, 1.4])
        
        with c_risk_a:
            df_q11 = data["df_q11"]
            if not df_q11.empty:
                chart_card_open("Student Segment Breakdown")
                seg_counts = df_q11["segment"].value_counts().reset_index()
                seg_counts.columns = ["segment", "count"]
                color_map11 = {
                    "High Achievers": CYAN, "Average Engaged": BLUE,
                    "Struggling": AMBER, "At-Risk Disengaged": RED,
                }
                colors11 = [color_map11.get(s, PURPLE) for s in seg_counts["segment"]]
                fig11a = go.Figure(go.Pie(
                    labels=seg_counts["segment"], values=seg_counts["count"],
                    hole=0.60,
                    marker=dict(colors=colors11, line=dict(color="#0B1020", width=2)),
                    textfont=dict(size=11, color=text_primary),
                ))
                fig11a.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"),
                    height=280, margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(font=dict(size=11, color=text_primary)),
                    annotations=[dict(
                        text=f"<b>{len(df_q11)}</b><br>Students",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=13, color=text_primary, family="Inter"),
                    )],
                )
                st.plotly_chart(fig11a, use_container_width=True, config={"displayModeBar": False})
                chart_card_close()
                
        with c_risk_b:
            df_q14 = data["df_q14"]
            if not df_q14.empty:
                chart_card_open("Top 10 At-Risk Students")
                df_q14s = df_q14.sort_values("risk_score", ascending=True)
                fig14 = px.bar(
                    df_q14s, x="risk_score", y="full_name",
                    orientation="h",
                    color="risk_score",
                    color_continuous_scale="Reds",
                    labels={"full_name": "Student", "risk_score": "Risk Score"},
                )
                fig14 = theme_plotly_layout(fig14, height=280)
                fig14.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig14, use_container_width=True, config={"displayModeBar": False})
                chart_card_close()
                
    else:
        st.info("Master data is empty or unavailable.")

elif selected_q == "q1":
    st.markdown('<div class="q-header"><span class="q-badge">Q1</span><span class="q-title">Which groups have the best and worst attendance rates?</span></div>', unsafe_allow_html=True)
    chart_card_open("📊 Attendance Rate per Group — Ranked")
    df_q1 = data["df_q1"]
    if not df_q1.empty:
        df_q1s = df_q1.sort_values("att_rate_pct")
        plat_att = 77.3 # Platform average as defined in notebook
        
        # Color mapped exactly to notebook values (below avg = RED/orange, above = BLUE)
        fig1 = go.Figure(go.Bar(
            x=df_q1s["true_group"], y=df_q1s["att_rate_pct"],
            marker_color=[RED if v else BLUE for v in df_q1s["below_avg"]],
            text=df_q1s["att_rate_pct"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=11, color=text_primary),
            hovertemplate="<b>%{x}</b><br>Attendance: %{y:.1f}%<extra></extra>",
        ))
        fig1.add_hline(y=plat_att, line_dash="dash", line_color=AMBER, line_width=1.5,
                       annotation_text=f"Platform avg: {plat_att:.1f}%",
                       annotation_font_color=AMBER, annotation_font_size=11)
        fig1 = theme_plotly_layout(fig1, height=380)
        fig1.update_yaxes(range=[0, 100], title_text="Attendance Rate (%)")
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        
        insight_box(
            "The platform average attendance is 77.3%. Groups G07 (60.2%) and G10 (65.4%) remain the primary outliers, significantly below average.",
            "Low-attendance groups often face scheduling conflicts or low student motivation.",
            "Audit G07 and G10 session times. Survey students on barriers. Consider rescheduling."
        )
    else:
        st.info("Q1 data not available.")
    chart_card_close()

elif selected_q == "q2":
    st.markdown('<div class="q-header"><span class="q-badge">Q2</span><span class="q-title">Score Distribution by Assessment Type</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Where is performance most volatile?</div>', unsafe_allow_html=True)
    chart_card_open("📊 Score Distribution by Assessment Type")
    df_q2 = data["df_q2"]
    if not df_q2.empty:
        c2a, c2b = st.columns(2)
        with c2a:
            df_q2s = df_q2.copy()
            # Category sorting matching notebook
            type_order = ['quiz', 'assignment', 'practical', 'exam']
            df_q2s['type'] = pd.Categorical(df_q2s['type'], categories=type_order, ordered=True)
            df_q2s = df_q2s.sort_values("type")
            
            fig2a = go.Figure(go.Bar(
                x=df_q2s["type"], y=df_q2s["mean"],
                marker_color=[BLUE, RED, CYAN, PURPLE],
                error_y=dict(type="data", array=df_q2s["std"].tolist(), visible=True, color="#475569"),
                text=df_q2s["mean"].round(1).astype(str),
                textposition="outside",
                textfont=dict(size=12, color=text_primary),
                hovertemplate="<b>%{x}</b><br>Mean: %{y:.1f}<extra></extra>",
            ))
            fig2a.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1,
                            annotation_text="Pass 60", annotation_font_color=RED)
            fig2a = theme_plotly_layout(fig2a, height=340)
            fig2a.update_yaxes(range=[0, 100], title_text="Average Score")
            st.plotly_chart(fig2a, use_container_width=True, config={"displayModeBar": False})
            
        with c2b:
            fig2b = go.Figure(go.Bar(
                x=df_q2s["type"], y=df_q2s["count"],
                marker_color=PURPLE, opacity=0.85,
                text=df_q2s["count"].astype(str),
                textposition="outside",
                textfont=dict(size=12, color=text_primary),
            ))
            fig2b = theme_plotly_layout(fig2b, height=340)
            fig2b.update_yaxes(title_text="Assessment Count")
            st.plotly_chart(fig2b, use_container_width=True, config={"displayModeBar": False})
            
        insight_box(
            "Assignments are the most volatile and challenging assessment type, with the lowest mean score (65.3) and the highest standard deviation (12.9).",
            "Students struggle more with the independent, long-form nature of assignments compared to structured testing.",
            "Provide scaffolding templates for assignments. Set up milestone check-ins."
        )
    else:
        st.info("Q2 data not available.")
    chart_card_close()

elif selected_q == "q3":
    st.markdown('<div class="q-header"><span class="q-badge">Q3</span><span class="q-title">Average Grade by Course</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Which course has the highest/lowest average and how does spread differ?</div>', unsafe_allow_html=True)
    chart_card_open("📚 Average Grade per Course")
    df_q3 = data["df_q3"]
    if not df_q3.empty:
        df_q3s = df_q3.sort_values("mean")
        fig3 = go.Figure(go.Bar(
            x=df_q3s["course_name"], y=df_q3s["mean"],
            error_y=dict(type="data", array=df_q3s["std"].tolist(), visible=True, color="#475569"),
            marker_color=BLUE,
            text=df_q3s["mean"].round(1).astype(str),
            textposition="outside",
            textfont=dict(size=11, color=text_primary),
            hovertemplate="<b>%{x}</b><br>Avg Score: %{y:.1f}<extra></extra>",
        ))
        fig3.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1,
                       annotation_text="Pass 60", annotation_font_color=RED)
        fig3 = theme_plotly_layout(fig3, height=380)
        fig3.update_yaxes(range=[40, 90], title_text="Average Score")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        
        insight_box(
            "Cybersecurity Essentials leads with an average grade of 76.2 (std=8.4). Digital Marketing is the clear outlier on the low end, averaging 59.1.",
            "Digital Marketing course material or instruction is currently not bringing the student cohort to a passing average.",
            "Redistribute teaching resources and add supplemental sessions to the Digital Marketing track."
        )
    else:
        st.info("Q3 data not available.")
    chart_card_close()

elif selected_q == "q4":
    st.markdown('<div class="q-header"><span class="q-badge">Q4</span><span class="q-title">Attendance Rate vs Average Grade</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Is there a relationship? Quantify it.</div>', unsafe_allow_html=True)
    chart_card_open("🔗 Attendance Rate vs Average Grade — Scatter")
    df_q4 = data["df_q4"]
    if not df_q4.empty:
        r4, p4 = pearson_r(df_q4, "att_rate_pct", "avg_grade")
        
        fig4 = px.scatter(
            df_q4, x="att_rate_pct", y="avg_grade",
            trendline="ols", opacity=0.55,
            color_discrete_sequence=[BLUE],
            labels={"att_rate_pct": "Attendance Rate (%)", "avg_grade": "Average Grade"},
        )
        fig4.update_traces(marker=dict(size=5))
        fig4.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1)
        fig4 = theme_plotly_layout(fig4, height=420)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
        
        insight_box(
            f"We see a moderate positive correlation (r = {r4:.3f}) between attendance and grades across {len(df_q4)} students.",
            "Students who attend more sessions receive more instruction and practice opportunities.",
            "Make attendance the primary leading KPI. Intervene when a student drops below 70%."
        )
    else:
        st.info("Q4 data not available.")
    chart_card_close()

elif selected_q == "q5":
    st.markdown('<div class="q-header"><span class="q-badge">Q5</span><span class="q-title">Engagement vs Academic Performance</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Does login frequency and video-watch time relate to grades?</div>', unsafe_allow_html=True)
    chart_card_open("🖥️ Platform Engagement vs Average Grade")
    df_q5 = data["df_q5"]
    if not df_q5.empty:
        tab5a, tab5b = st.tabs(["Login Frequency", "Total Video Watch Time"])
        
        with tab5a:
            r5a, p5a = pearson_r(df_q5, "login_count", "avg_grade")
            fig5a = px.scatter(
                df_q5, x="login_count", y="avg_grade",
                trendline="ols", opacity=0.55,
                color_discrete_sequence=[RED],
                labels={"login_count": "Login Count", "avg_grade": "Average Grade"},
            )
            fig5a.update_traces(marker=dict(size=5))
            fig5a = theme_plotly_layout(fig5a, height=380, title=f"Login Frequency vs Average Grade (r = {r5a:.3f})")
            st.plotly_chart(fig5a, use_container_width=True, config={"displayModeBar": False})
            
        with tab5b:
            r5b, p5b = pearson_r(df_q5, "video_seconds", "avg_grade")
            fig5b = px.scatter(
                df_q5, x="video_seconds", y="avg_grade",
                trendline="ols", opacity=0.55,
                color_discrete_sequence=[GREEN],
                labels={"video_seconds": "Total Video Seconds", "avg_grade": "Average Grade"},
            )
            fig5b.update_traces(marker=dict(size=5))
            fig5b = theme_plotly_layout(fig5b, height=380, title=f"Total Video Watch Time (s) vs Average Grade (r = {r5b:.3f})")
            st.plotly_chart(fig5b, use_container_width=True, config={"displayModeBar": False})
            
        insight_box(
            "Engagement metrics are strong predictors of performance. Video watch time (r=0.402) has a stronger correlation with grades than login frequency (r=0.330).",
            "The quality of engagement (actually consuming content) is more impactful than simply logging into the platform.",
            "Gamify video watching. Set minimum video watch milestones as a course requirement."
        )
    else:
        st.info("Q5 data not available.")
    chart_card_close()

elif selected_q == "q6":
    st.markdown('<div class="q-header"><span class="q-badge">Q6</span><span class="q-title">Highest Concept Failure Rates</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Which concepts are hardest? Which course has the biggest curriculum weak spot?</div>', unsafe_allow_html=True)
    chart_card_open("🏴 Top 15 Concepts by Failure Rate")
    df_q6 = data["df_q6"]
    if not df_q6.empty:
        df_q6s = df_q6.sort_values("failure_rate_pct", ascending=True)
        fig6 = px.bar(
            df_q6s, x="failure_rate_pct", y="concept_name",
            color="course_name", orientation="h",
            labels={"failure_rate_pct": "Failure Rate (%)", "concept_name": "Concept", "course_name": "Course"},
            text=df_q6s["failure_rate_pct"].round(1).astype(str) + "%"
        )
        fig6 = theme_plotly_layout(fig6, height=450)
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
        
        insight_box(
            "Recursion remains the most difficult concept with a staggering 85.3% failure rate, followed by Overfitting & Model Evaluation in Cybersecurity (50-60%).",
            "Concepts requiring abstract reasoning and math foundations consistently yield higher failure rates.",
            "Add supplementary workshops for Recursion and Model Evaluation. Create visualised step-through exercises."
        )
    else:
        st.info("Q6 data not available.")
    chart_card_close()

elif selected_q == "q7":
    st.markdown('<div class="q-header"><span class="q-badge">Q7</span><span class="q-title">Worst Concept Mastery Over Time</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Is Recursion improving, flat, or getting worse?</div>', unsafe_allow_html=True)
    chart_card_open("📈 Recursion Mastery Rate Trend")
    df_q7 = data["df_q7"]
    if not df_q7.empty:
        df_q7s = df_q7.sort_values("month")
        fig7 = px.line(
            df_q7s, x="month", y="mastery_rate_pct",
            markers=True,
            color_discrete_sequence=[RED]
        )
        fig7.add_hline(y=60, line_dash="dash", line_color="gray", annotation_text="60% target")
        fig7 = theme_plotly_layout(fig7, height=340)
        fig7.update_yaxes(range=[0, 50], title_text="Mastery Rate (%)")
        st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})
        
        insight_box(
            "Recursion mastery reached 30.0% at its peak but dipped to 9.0% at its lowest.",
            "Recursion requires cumulative understanding — early weakness cascades into persistent failure.",
            "Introduce visual recursion trees and weekly peer coding sessions. Track monthly improvement."
        )
    else:
        st.info("Q7 data not available.")
    chart_card_close()

elif selected_q == "q8":
    st.markdown('<div class="q-header"><span class="q-badge">Q8</span><span class="q-title">Late Submissions vs Score</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Do late submitters score lower?</div>', unsafe_allow_html=True)
    chart_card_open("📬 Late vs On-Time Submission Analysis")
    df_q8 = data["df_q8"]
    if not df_q8.empty:
        # Compute Point Biserial Correlation matching notebook
        r8, p8 = stats.pointbiserialr(df_q8['is_late'].astype(int), df_q8['score'])
        
        col8a, col8b = st.columns(2)
        with col8a:
            fig8a = px.box(
                df_q8, x="is_late", y="score",
                color="is_late",
                color_discrete_map={True: RED, False: BLUE},
                labels={"is_late": "Submitted Late", "score": "Score"}
            )
            fig8a = theme_plotly_layout(fig8a, height=350, title=f"Score Distribution: On-Time vs Late Submissions (r = {r8:.3f})")
            st.plotly_chart(fig8a, use_container_width=True, config={"displayModeBar": False})
            
        with col8b:
            fig8b = px.scatter(
                df_q8.sample(min(1000, len(df_q8)), random_state=42),
                x="buffer_hours", y="score", opacity=0.3, trendline="ols",
                color_discrete_sequence=[GREEN],
                labels={"buffer_hours": "Hours Before Deadline (negative = late)", "score": "Score"}
            )
            fig8b = theme_plotly_layout(fig8b, height=350, title="Submission Buffer vs Score")
            st.plotly_chart(fig8b, use_container_width=True, config={"displayModeBar": False})
            
        late_avg   = df_q8[df_q8['is_late']==True]['score'].mean()
        ontime_avg = df_q8[df_q8['is_late']==False]['score'].mean()
        
        insight_box(
            f"On-time submissions score {ontime_avg - late_avg:.2f} points higher on average (67.07 vs 62.13).",
            "Late submissions signal disengagement or overload; rushed work also lowers quality.",
            "Set automated deadline reminders 24 hrs before due date. Apply a grace-period penalty to incentivise timeliness."
        )
    else:
        st.info("Q8 data not available.")
    chart_card_close()

elif selected_q == "q9":
    st.markdown('<div class="q-header"><span class="q-badge">Q9</span><span class="q-title">Attendance & Engagement Over Time</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Is there a cohort-wide dip? What could explain it?</div>', unsafe_allow_html=True)
    chart_card_open("📉 Monthly Attendance & Engagement — 6-Month Trend")
    df_q9a = data["df_q9a"]
    df_q9b = data["df_q9b"]
    
    if not df_q9a.empty and not df_q9b.empty:
        df_q9as = df_q9a.sort_values("month")
        df_q9bs = df_q9b.sort_values("month")
        
        from plotly.subplots import make_subplots
        fig9 = make_subplots(rows=2, cols=1, subplot_titles=('Monthly Attendance Rate', 'Monthly Engagement Events'), shared_xaxes=True)
        
        fig9.add_trace(go.Scatter(
            x=df_q9as['month'], y=df_q9as['att_rate'],
            mode='lines+markers', name='Attendance %', line=dict(color=BLUE, width=2.5)
        ), row=1, col=1)
        
        fig9.add_trace(go.Bar(
            x=df_q9bs['month'], y=df_q9bs['events'],
            name='Total Events', marker_color=RED
        ), row=2, col=1)
        
        fig9 = theme_plotly_layout(fig9, height=500)
        st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})
        
        insight_box(
            "The analysis confirms a synchronized dip in March 2026, where attendance fell to 62.2% and engagement events dropped to 3,983.",
            "Seasonal dips align with external factors such as holiday breaks or exam periods.",
            "Pre-schedule makeup sessions and release lighter assignments around identified low-attendance months."
        )
    else:
        st.info("Q9 data not available.")
    chart_card_close()

elif selected_q == "q10":
    st.markdown('<div class="q-header"><span class="q-badge">Q10</span><span class="q-title">Age Bands vs Outcomes</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Does age relate to grade, attendance, and engagement?</div>', unsafe_allow_html=True)
    chart_card_open("🎂 Academic Outcomes by Age Band")
    df_q10 = data["df_q10"]
    if not df_q10.empty:
        fig10 = go.Figure()
        for col, color, name in [('avg_grade', BLUE, 'Avg Grade'), ('avg_att', RED, 'Attendance %'), ('avg_events', GREEN, 'Avg Events')]:
            fig10.add_trace(go.Bar(
                x=df_q10['age_band'].astype(str), y=df_q10[col],
                name=name, marker_color=color
            ))
        fig10 = theme_plotly_layout(fig10, height=380)
        fig10.update_layout(barmode='group')
        st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar": False})
        
        insight_box(
            "The 26-30 age band shows the best overall outcomes, with the highest average grade (71.3) and attendance (79.1%).",
            "Older students may be more self-regulated, while younger students might require more structured accountability.",
            "Tailor peer mentoring and time-management resources for younger students."
        )
    else:
        st.info("Q10 data not available.")
    chart_card_close()

elif selected_q == "q11":
    st.markdown('<div class="q-header"><span class="q-badge">Q11</span><span class="q-title">Student Segmentation (K-Means Clustering)</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Segment students by attendance, engagement, average grade, and failed concepts.</div>', unsafe_allow_html=True)
    df_q11 = data["df_q11"]
    if not df_q11.empty:
        c11a, c11b = st.columns([1, 1.6])
        
        with c11a:
            chart_card_open("🎯 Segment Distribution")
            seg_counts = df_q11["segment"].value_counts().reset_index()
            seg_counts.columns = ["segment", "count"]
            color_map11 = {
                "High Achievers": CYAN, "Average Engaged": BLUE,
                "Struggling": AMBER, "At-Risk Disengaged": RED,
            }
            colors11 = [color_map11.get(s, PURPLE) for s in seg_counts["segment"]]
            fig11a = go.Figure(go.Pie(
                labels=seg_counts["segment"], values=seg_counts["count"],
                hole=0.60,
                marker=dict(colors=colors11, line=dict(color="#0B1020", width=2)),
                textfont=dict(size=11, color=text_primary),
            ))
            fig11a.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"),
                height=300, margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(font=dict(size=11, color=text_primary)),
                annotations=[dict(
                    text=f"<b>{len(df_q11)}</b><br>Students",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14, color=text_primary, family="Inter"),
                )],
            )
            st.plotly_chart(fig11a, use_container_width=True, config={"displayModeBar": False})
            chart_card_close()
            
        with c11b:
            chart_card_open("🔭 Attendance vs Grade by Segment")
            fig11b = px.scatter(
                df_q11.dropna(subset=["att_rate", "avg_grade"]),
                x="att_rate", y="avg_grade", color="segment",
                color_discrete_map=color_map11,
                hover_data=["full_name", "total_events", "failed_concepts"],
                opacity=0.7,
                labels={"att_rate": "Attendance Rate (%)", "avg_grade": "Avg Grade", "segment": "Segment"},
            )
            fig11b.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1)
            fig11b.add_vline(x=70, line_dash="dot", line_color=AMBER, line_width=1)
            fig11b = theme_plotly_layout(fig11b, height=320)
            st.plotly_chart(fig11b, use_container_width=True, config={"displayModeBar": False})
            chart_card_close()
            
        insight_box(
            "K-Means identified 68 students in the 'At-Risk Disengaged' category (att=61.5%, grade=57.6, 13+ failed concepts).",
            "Low attendance combined with low engagement signals high dropout risk.",
            "Trigger automated re-engagement campaigns and 1:1 mentorship calls for this segment immediately."
        )
    else:
        st.info("Q11 data not available.")

elif selected_q == "q12":
    st.markdown('<div class="q-header"><span class="q-badge">Q12</span><span class="q-title">True Group Sizes vs Self-Reported Counts</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Visualize the discrepancies.</div>', unsafe_allow_html=True)
    chart_card_open("📋 Stated vs Actual Group Headcount")
    df_q12 = data["df_q12"]
    if not df_q12.empty:
        df_q12s = df_q12.sort_values("discrepancy", ascending=False)
        fig12 = go.Figure()
        fig12.add_trace(go.Bar(
            x=df_q12s["group_id"], y=df_q12s["stated_num_students"],
            name="Stated Count", marker_color=PURPLE, opacity=0.75,
        ))
        fig12.add_trace(go.Bar(
            x=df_q12s["group_id"], y=df_q12s["actual_count"],
            name="Actual Count", marker_color=BLUE,
        ))
        fig12.update_layout(barmode="group")
        fig12 = theme_plotly_layout(fig12, height=360)
        st.plotly_chart(fig12, use_container_width=True, config={"displayModeBar": False})
        
        insight_box(
            "Serious discrepancies exist in group headcounts. G10 and G05 both have a 30-student deficit between stated and actual counts.",
            "Database records may not have been updated after group restructuring or student transfers.",
            "Sync the groups table with actual student roster data. Audit all groups with discrepancy > 5."
        )
    else:
        st.info("Q12 data not available.")
    chart_card_close()

elif selected_q == "q13":
    st.markdown('<div class="q-header"><span class="q-badge">Q13</span><span class="q-title">Non-Viable Group — Identify, Profile & Recommend</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Find the too-small group, its closest counterpart, and make a data-backed recommendation.</div>', unsafe_allow_html=True)
    chart_card_open("🔍 G10 Non-Viable Group Profile")
    df_q13 = data["df_q13"]
    if not df_q13.empty:
        row13 = df_q13.iloc[0]
        st.markdown("""
        <div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);
                    border-radius:12px;padding:20px 24px;margin-bottom:16px;">
          <div style="font-size:1.1rem;font-weight:700;color:#F87171;margin-bottom:12px;">
            ⚠️ G10 — Non-Viable Group Detected
          </div>
        """, unsafe_allow_html=True)
        mc13a, mc13b, mc13c, mc13d = st.columns(4)
        with mc13a:
            st.metric("Group ID", row13.get("group_id", "G10"))
        with mc13b:
            st.metric("Stated Capacity", int(row13.get("stated_num_students", 31)))
        with mc13c:
            st.metric("Actual Enrolled", int(row13.get("actual_count", 1)))
        with mc13d:
            st.metric("Headcount Gap", int(row13.get("discrepancy", 30)))
        st.markdown("</div>", unsafe_allow_html=True)
        
        insight_box(
            "Group G10 is operationally non-viable with only 1 enrolled student (Adel AbdelHamid).",
            "No other groups are currently running the C007 Cybersecurity Essentials course, making a direct merge impossible.",
            "Develop a custom individual learning path, or transition them to a related C006 group (G08/G09) based on profile similarity."
        )
    else:
        st.info("Q13 data not available.")
    chart_card_close()

elif selected_q == "q14":
    st.markdown('<div class="q-header"><span class="q-badge">Q14</span><span class="q-title">At-Risk Student Ranking</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Top 10 students an instructor should contact first.</div>', unsafe_allow_html=True)
    df_q14 = data["df_q14"]
    if not df_q14.empty:
        c14a, c14b = st.columns([1.4, 1])
        with c14a:
            chart_card_open("🚨 Composite Risk Score — Top 10 At-Risk Students")
            df_q14s = df_q14.sort_values("risk_score", ascending=True)
            fig14 = px.bar(
                df_q14s, x="risk_score", y="full_name",
                orientation="h",
                color="risk_score",
                color_continuous_scale="Reds",
                labels={"full_name": "Student", "risk_score": "Risk Score"},
            )
            fig14 = theme_plotly_layout(fig14, height=420)
            st.plotly_chart(fig14, use_container_width=True, config={"displayModeBar": False})
            chart_card_close()
            
        with c14b:
            chart_card_open("📋 At-Risk Student Details")
            display14 = df_q14.sort_values("risk_score", ascending=False)[[
                "full_name", "group_id", "overall_att", "avg_grade", "failed_concepts", "risk_score"
            ]].rename(columns={
                "full_name": "Student", "group_id": "Group",
                "overall_att": "Att. %", "avg_grade": "Avg Grade",
                "failed_concepts": "Failed Conc.", "risk_score": "Risk Score",
            })
            st.dataframe(display14, use_container_width=True, hide_index=True, height=380)
            chart_card_close()
            
        insight_box(
            "Marwan ElBaz (S0453) and Rowan ElBaz (S0201) are the highest-risk students, with composite risk scores above 83.",
            "The top 10 at-risk list is heavily dominated by G07 students, reinforcing that G07 is the primary site of academic failure.",
            "Schedule 1:1 instructor calls within 48 hours. Assign a dedicated academic coach to G07 immediately."
        )
    else:
        st.info("Q14 data not available.")

elif selected_q == "q15":
    st.markdown('<div class="q-header"><span class="q-badge">Q15</span><span class="q-title">Group Grade Trends Across the Term</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="q-desc">Which groups are trending up and which are sliding down?</div>', unsafe_allow_html=True)
    chart_card_open("📈 Average Grade per Group — Monthly Trend")
    df_q15 = data["df_q15"]
    if not df_q15.empty:
        df_q15s = df_q15.sort_values("month")
        fig15 = px.line(
            df_q15s, x="month", y="avg_score", color="true_group",
            markers=True,
            labels={"month": "Month", "avg_score": "Avg Score", "true_group": "Group"},
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig15.add_hline(y=60, line_dash="dot", line_color="red", annotation_text="Pass threshold (60)")
        fig15 = theme_plotly_layout(fig15, height=450)
        st.plotly_chart(fig15, use_container_width=True, config={"displayModeBar": False})
        
        insight_box(
            "Most groups recovered after the March dip, but G07 remained consistently below the 60% pass threshold for nearly the entire term.",
            "Small student volumes in certain groups make average scores highly unstable over time.",
            "Escalate declining groups to academic leadership. Assign tutors to groups staying below pass threshold."
        )
    else:
        st.info("Q15 data not available.")
    chart_card_close()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="app-footer">Kayfa — كيف &nbsp;&middot;&middot;&nbsp; Week 2 &nbsp;&middot;&nbsp; Data Analytics Track &nbsp;&middot;&nbsp; Evaluation</div>', unsafe_allow_html=True)
