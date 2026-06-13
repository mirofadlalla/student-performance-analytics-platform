import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Kayfa Analytics Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  /* ── Root & Background ── */
  html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0B1020 0%, #0F1A33 60%, #0D1526 100%) !important;
    font-family: 'Inter', sans-serif !important;
    color: #E2E8F0 !important;
  }
  [data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
      linear-gradient(rgba(77,163,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(77,163,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070D1A 0%, #0B1426 100%) !important;
    border-right: 1px solid rgba(77,163,255,0.15) !important;
  }
  [data-testid="stSidebar"] * { color: #CBD5E1 !important; }
  [data-testid="stSidebar"] .stRadio label { color: #94A3B8 !important; font-size: 0.85rem; }

  /* ── Main content offset ── */
  .main .block-container {
    padding-top: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1400px !important;
  }

  /* ── Page Header ── */
  .page-header {
    background: linear-gradient(135deg, rgba(77,163,255,0.08) 0%, rgba(139,92,246,0.08) 100%);
    border: 1px solid rgba(77,163,255,0.2);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
  }
  .page-header::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -20%;
    width: 60%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(77,163,255,0.06) 0%, transparent 70%);
    pointer-events: none;
  }
  .page-header h1 {
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4DA3FF 0%, #8B5CF6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
  }
  .page-header p {
    color: #94A3B8;
    font-size: 0.92rem;
    margin: 0;
    font-weight: 400;
  }

  /* ── KPI Cards ── */
  .kpi-grid { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
  .kpi-card {
    flex: 1;
    min-width: 180px;
    background: linear-gradient(135deg, rgba(15,26,51,0.9) 0%, rgba(11,16,32,0.9) 100%);
    border: 1px solid rgba(77,163,255,0.18);
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
  }
  .kpi-card:hover {
    border-color: rgba(77,163,255,0.45);
    box-shadow: 0 0 24px rgba(77,163,255,0.12);
    transform: translateY(-2px);
  }
  .kpi-card::after {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4DA3FF, #8B5CF6);
  }
  .kpi-icon { font-size: 1.5rem; margin-bottom: 10px; }
  .kpi-value { font-size: 2rem; font-weight: 700; color: #F1F5F9; line-height: 1; }
  .kpi-label { font-size: 0.75rem; color: #64748B; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 5px; }
  .kpi-trend { font-size: 0.78rem; margin-top: 8px; font-weight: 500; }
  .kpi-trend.up { color: #22D3EE; }
  .kpi-trend.down { color: #F87171; }
  .kpi-trend.neutral { color: #94A3B8; }

  /* ── Glass Chart Card ── */
  .chart-card {
    background: rgba(11,16,32,0.7);
    border: 1px solid rgba(77,163,255,0.14);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
  }
  .chart-card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #CBD5E1;
    margin: 0 0 16px 0;
    border-bottom: 1px solid rgba(77,163,255,0.1);
    padding-bottom: 12px;
  }

  /* ── Insight Box ── */
  .insight-box {
    background: linear-gradient(135deg, rgba(77,163,255,0.04) 0%, rgba(139,92,246,0.04) 100%);
    border: 1px solid rgba(77,163,255,0.12);
    border-left: 3px solid #4DA3FF;
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 12px;
    font-size: 0.85rem;
    line-height: 1.6;
  }
  .insight-box .row { margin-bottom: 7px; color: #CBD5E1; }
  .insight-box .row:last-child { margin-bottom: 0; }
  .insight-box span.label {
    font-weight: 600;
    margin-right: 6px;
  }

  /* ── Section Title ── */
  .section-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #4DA3FF;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 16px;
    margin-top: 8px;
  }

  /* ── Tables ── */
  .dataframe { background: transparent !important; }
  [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

  /* ── Tabs ── */
  [data-testid="stTabs"] [role="tab"] {
    color: #64748B !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
  }
  [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #4DA3FF !important;
    border-bottom-color: #4DA3FF !important;
  }

  /* ── Metrics ── */
  [data-testid="stMetric"] {
    background: rgba(15,26,51,0.6);
    border: 1px solid rgba(77,163,255,0.12);
    border-radius: 12px;
    padding: 16px;
  }
  [data-testid="stMetric"] label { color: #64748B !important; font-size: 0.78rem !important; }
  [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #F1F5F9 !important; }

  /* ── Status Badges ── */
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
  }
  .badge-red { background: rgba(248,113,113,0.15); color: #F87171; border: 1px solid rgba(248,113,113,0.3); }
  .badge-green { background: rgba(34,211,238,0.1); color: #22D3EE; border: 1px solid rgba(34,211,238,0.25); }
  .badge-amber { background: rgba(251,191,36,0.1); color: #FBD24C; border: 1px solid rgba(251,191,36,0.25); }
  .badge-purple { background: rgba(139,92,246,0.12); color: #A78BFA; border: 1px solid rgba(139,92,246,0.3); }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #0B1020; }
  ::-webkit-scrollbar-thumb { background: rgba(77,163,255,0.3); border-radius: 3px; }

  /* ── Plotly bg ── */
  .js-plotly-plot .plotly { background: transparent !important; }

  /* ── Divider ── */
  hr { border-color: rgba(77,163,255,0.1) !important; margin: 24px 0 !important; }

  /* ── Hide streamlit decorations ── */
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="collapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar Brand ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 24px 0; border-bottom: 1px solid rgba(77,163,255,0.15); margin-bottom: 20px;">
      <div style="font-size:1.4rem; font-weight:800; background:linear-gradient(135deg,#4DA3FF,#8B5CF6);
                  -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:-0.02em;">
        🎓 Kayfa
      </div>
      <div style="font-size:0.72rem; color:#475569; margin-top:4px; text-transform:uppercase; letter-spacing:0.1em;">
        Analytics Intelligence Platform
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;">Navigation</div>', unsafe_allow_html=True)

    pages = {
        "🏠  Executive Overview": "overview",
        "👥  Student Intelligence": "students",
        "🏫  Group Performance": "groups",
        "📚  Concept Intelligence": "concepts",
        "⚠️  Data Quality Audit": "audit",
    }

    if "active_page" not in st.session_state:
        st.session_state.active_page = "overview"

    for label, key in pages.items():
        is_active = st.session_state.active_page == key
        btn_style = "background:rgba(77,163,255,0.12);border:1px solid rgba(77,163,255,0.3);color:#4DA3FF;" if is_active else "background:transparent;border:1px solid transparent;color:#64748B;"
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.active_page = key
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="border-top:1px solid rgba(77,163,255,0.1);padding-top:16px;font-size:0.72rem;color:#334155;">
      <div style="margin-bottom:6px;">📡 <span style="color:#22D3EE;">Live</span> · MongoDB Atlas</div>
      <div>🗄️ StudentaAnalytics DB</div>
      <div style="margin-top:8px;color:#1E3A5F;">v1.0.0 · Production</div>
    </div>
    """, unsafe_allow_html=True)
page = st.session_state.active_page

# Demo mode banner
from db import is_demo_mode
if is_demo_mode():
    st.markdown("""
    <div style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);
                border-radius:10px;padding:10px 18px;margin-bottom:16px;font-size:0.82rem;color:#FBD24C;
                display:flex;align-items:center;gap:10px;">
      <span>⚡</span>
      <span><strong>Demo Mode</strong> — MongoDB Atlas not reachable from this environment.
      Showing realistic synthetic data. On your machine, all charts will load live from Atlas.</span>
    </div>
    """, unsafe_allow_html=True)

if page == "overview":
    from pages import overview; overview.render()
elif page == "students":
    from pages import students; students.render()
elif page == "groups":
    from pages import groups; groups.render()
elif page == "concepts":
    from pages import concepts; concepts.render()
elif page == "audit":
    from pages import audit; audit.render()
