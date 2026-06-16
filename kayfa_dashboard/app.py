import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Kayfa Analytics Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme initialisation ─────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "active_page" not in st.session_state:
    st.session_state.active_page = "overview"

theme = st.session_state.theme

# ── CSS Variables by theme ───────────────────────────────────────────────────
if theme == "dark":
    ROOT_BG       = "linear-gradient(135deg, #0B1020 0%, #0F1A33 60%, #0D1526 100%)"
    BODY_COLOR    = "#E2E8F0"
    SURFACE       = "rgba(11,16,32,0.7)"
    BORDER        = "rgba(77,163,255,0.14)"
    NAV_BG        = "rgba(7,13,26,0.95)"
    NAV_BORDER    = "rgba(77,163,255,0.15)"
    NAV_TEXT      = "#94A3B8"
    NAV_ACTIVE_BG = "rgba(77,163,255,0.12)"
    NAV_ACTIVE_BC = "rgba(77,163,255,0.35)"
    NAV_ACTIVE_TXT= "#4DA3FF"
    HDR_BG        = "linear-gradient(135deg, rgba(77,163,255,0.1) 0%, rgba(139,92,246,0.08) 100%)"
    HDR_BORDER    = "rgba(77,163,255,0.2)"
    HDR_TITLE     = "#E2E8F0"
    HDR_ACCENT    = "#4DA3FF"
    HDR_SEP       = "rgba(77,163,255,0.3)"
    HDR_SUB       = "#64748B"
    FTR_BG        = "rgba(7,13,26,0.95)"
    FTR_BORDER    = "rgba(77,163,255,0.1)"
    FTR_TEXT      = "#475569"
    FTR_DOT       = "#22D3EE"
    SCROLL_TRACK  = "#0B1020"
    SCROLL_THUMB  = "rgba(77,163,255,0.3)"
    GRID_DOT      = "rgba(77,163,255,0.025)"
    METRIC_BG     = "rgba(15,26,51,0.6)"
    METRIC_BORDER = "rgba(77,163,255,0.12)"
    METRIC_LABEL  = "#64748B"
    METRIC_VAL    = "#F1F5F9"
    TAB_COLOR     = "#64748B"
    TAB_ACTIVE    = "#4DA3FF"
    BADGE_RED_BG  = "rgba(248,113,113,0.15)"; BADGE_RED_C = "#F87171"; BADGE_RED_BC = "rgba(248,113,113,0.3)"
    BADGE_GRN_BG  = "rgba(34,211,238,0.1)";  BADGE_GRN_C = "#22D3EE"; BADGE_GRN_BC = "rgba(34,211,238,0.25)"
    BADGE_AMB_BG  = "rgba(251,191,36,0.1)";  BADGE_AMB_C = "#FBD24C"; BADGE_AMB_BC = "rgba(251,191,36,0.25)"
    BADGE_PUR_BG  = "rgba(139,92,246,0.12)"; BADGE_PUR_C = "#A78BFA"; BADGE_PUR_BC = "rgba(139,92,246,0.3)"
    DEMO_BG = "rgba(251,191,36,0.08)"; DEMO_BC = "rgba(251,191,36,0.25)"; DEMO_C = "#FBD24C"
    TOGGLE_BG = "rgba(77,163,255,0.1)"; TOGGLE_BC = "rgba(77,163,255,0.3)"; TOGGLE_C = "#4DA3FF"
    TOGGLE_EMOJI = "☀️"; TOGGLE_LABEL = "Light Mode"
    GRID_BG_STYLE = f"""
      [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image:
          linear-gradient({GRID_DOT} 1px, transparent 1px),
          linear-gradient(90deg, {GRID_DOT} 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
      }}
    """
else:
    ROOT_BG       = "linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 60%, #EFF6FF 100%)"
    BODY_COLOR    = "#0F172A"
    SURFACE       = "#FFFFFF"
    BORDER        = "#E2E8F0"
    NAV_BG        = "rgba(255,255,255,0.97)"
    NAV_BORDER    = "#E2E8F0"
    NAV_TEXT      = "#64748B"
    NAV_ACTIVE_BG = "rgba(37,99,235,0.08)"
    NAV_ACTIVE_BC = "rgba(37,99,235,0.25)"
    NAV_ACTIVE_TXT= "#2563EB"
    HDR_BG        = "linear-gradient(135deg, rgba(37,99,235,0.06) 0%, rgba(99,102,241,0.05) 100%)"
    HDR_BORDER    = "rgba(37,99,235,0.15)"
    HDR_TITLE     = "#0F172A"
    HDR_ACCENT    = "#2563EB"
    HDR_SEP       = "rgba(37,99,235,0.3)"
    HDR_SUB       = "#64748B"
    FTR_BG        = "rgba(248,250,252,0.97)"
    FTR_BORDER    = "#E2E8F0"
    FTR_TEXT      = "#94A3B8"
    FTR_DOT       = "#22C55E"
    SCROLL_TRACK  = "#F1F5F9"
    SCROLL_THUMB  = "rgba(37,99,235,0.2)"
    GRID_DOT      = "rgba(0,0,0,0)"
    METRIC_BG     = "#FFFFFF"
    METRIC_BORDER = "#E2E8F0"
    METRIC_LABEL  = "#64748B"
    METRIC_VAL    = "#0F172A"
    TAB_COLOR     = "#64748B"
    TAB_ACTIVE    = "#2563EB"
    BADGE_RED_BG  = "rgba(220,38,38,0.08)";  BADGE_RED_C = "#DC2626"; BADGE_RED_BC = "rgba(220,38,38,0.25)"
    BADGE_GRN_BG  = "rgba(22,163,74,0.08)";  BADGE_GRN_C = "#16A34A"; BADGE_GRN_BC = "rgba(22,163,74,0.25)"
    BADGE_AMB_BG  = "rgba(202,138,4,0.08)";  BADGE_AMB_C = "#CA8A04"; BADGE_AMB_BC = "rgba(202,138,4,0.25)"
    BADGE_PUR_BG  = "rgba(99,102,241,0.08)"; BADGE_PUR_C = "#6366F1"; BADGE_PUR_BC = "rgba(99,102,241,0.25)"
    DEMO_BG = "rgba(234,179,8,0.06)"; DEMO_BC = "rgba(202,138,4,0.2)"; DEMO_C = "#CA8A04"
    TOGGLE_BG = "rgba(15,23,42,0.06)"; TOGGLE_BC = "#CBD5E1"; TOGGLE_C = "#334155"
    TOGGLE_EMOJI = "🌙"; TOGGLE_LABEL = "Dark Mode"
    GRID_BG_STYLE = ""

# ── Inject Global CSS ────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, [data-testid="stAppViewContainer"] {{
    background: {ROOT_BG} !important;
    font-family: 'Inter', sans-serif !important;
    color: {BODY_COLOR} !important;
  }}

  {GRID_BG_STYLE}

  /* Hide sidebar completely */
  [data-testid="stSidebar"] {{ display: none !important; }}
  [data-testid="collapsedControl"] {{ display: none !important; }}

  /* Main content */
  .main .block-container {{
    padding-top: 0 !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1400px !important;
  }}

  /* Scrollbar */
  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-track {{ background: {SCROLL_TRACK}; }}
  ::-webkit-scrollbar-thumb {{ background: {SCROLL_THUMB}; border-radius: 3px; }}

  /* Tabs */
  [data-testid="stTabs"] [role="tab"] {{
    color: {TAB_COLOR} !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
  }}
  [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: {TAB_ACTIVE} !important;
    border-bottom-color: {TAB_ACTIVE} !important;
  }}

  /* Metrics */
  [data-testid="stMetric"] {{
    background: {METRIC_BG};
    border: 1px solid {METRIC_BORDER};
    border-radius: 12px;
    padding: 16px;
  }}
  [data-testid="stMetric"] label {{ color: {METRIC_LABEL} !important; font-size: 0.78rem !important; }}
  [data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {METRIC_VAL} !important; }}

  /* Badges */
  .badge {{ display:inline-block; padding:3px 10px; border-radius:20px;
             font-size:0.72rem; font-weight:600; letter-spacing:0.05em; }}
  .badge-red    {{ background:{BADGE_RED_BG}; color:{BADGE_RED_C}; border:1px solid {BADGE_RED_BC}; }}
  .badge-green  {{ background:{BADGE_GRN_BG}; color:{BADGE_GRN_C}; border:1px solid {BADGE_GRN_BC}; }}
  .badge-amber  {{ background:{BADGE_AMB_BG}; color:{BADGE_AMB_C}; border:1px solid {BADGE_AMB_BC}; }}
  .badge-purple {{ background:{BADGE_PUR_BG}; color:{BADGE_PUR_C}; border:1px solid {BADGE_PUR_BC}; }}

  /* Plotly */
  .js-plotly-plot .plotly {{ background: transparent !important; }}

  /* Divider */
  hr {{ border-color: {BORDER} !important; margin: 24px 0 !important; }}

  /* Hide streamlit decorations */
  #MainMenu, footer, header {{ visibility: hidden; }}

  /* Dataframe theming */
  [data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; }}

  /* Download button */
  [data-testid="stDownloadButton"] > button {{
    background: {TOGGLE_BG} !important;
    color: {TOGGLE_C} !important;
    border: 1px solid {TOGGLE_BC} !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
  }}
  [data-testid="stDownloadButton"] > button:hover {{
    opacity: 0.85 !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── Global Header ────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
  background: {HDR_BG};
  border-bottom: 1px solid {HDR_BORDER};
  padding: 14px 32px 0 32px;
  margin: -1rem -2rem 0 -2rem;
  position: sticky;
  top: 0;
  z-index: 999;
  backdrop-filter: blur(12px);
">
  <!-- Brand row -->
  <div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:12px;">
    <div style="display:flex;align-items:center;gap:18px;">
      <div style="font-size:1.5rem;">🎓</div>
      <div>
        <div style="font-size:1.05rem;font-weight:800;color:{HDR_TITLE};letter-spacing:-0.02em;line-height:1.1;">
          Kayfa — <span style="font-weight:400;font-family:'Arial',sans-serif;">كيف</span>
          <span style="color:{HDR_SEP};font-weight:300;margin:0 6px;">·</span>
          <span style="font-weight:500;color:{HDR_ACCENT};">Month 1 · Week 2</span>
          <span style="color:{HDR_SEP};font-weight:300;margin:0 6px;">·</span>
          <span style="font-weight:500;color:{HDR_TITLE};">Data Analytics Track</span>
          <span style="color:{HDR_SEP};font-weight:300;margin:0 6px;">·</span>
          <span style="font-weight:600;color:{HDR_ACCENT};">Evaluation</span>
        </div>
        <div style="font-size:0.7rem;color:{HDR_SUB};margin-top:2px;letter-spacing:0.06em;text-transform:uppercase;">
          Analytics Intelligence Platform
        </div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Top Navigation Bar ───────────────────────────────────────────────────────
pages = {
    "overview":  ("🏠", "Executive Overview"),
    "students":  ("👥", "Student Intelligence"),
    "groups":    ("🏫", "Group Performance"),
    "concepts":  ("📚", "Concept Intelligence"),
    "audit":     ("⚠️", "Data Quality Audit"),
}

nav_cols = st.columns([1, 1, 1, 1, 1, 0.45])
page_keys = list(pages.keys())
for i, (key, (icon, label)) in enumerate(pages.items()):
    is_active = st.session_state.active_page == key
    with nav_cols[i]:
        if is_active:
            style = (f"background:{NAV_ACTIVE_BG};border:1px solid {NAV_ACTIVE_BC};"
                     f"color:{NAV_ACTIVE_TXT};border-radius:8px;")
        else:
            style = f"color:{NAV_TEXT};border-radius:8px;"
        if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.active_page = key
            st.rerun()

# Theme toggle button in last column
with nav_cols[5]:
    if st.button(f"{TOGGLE_EMOJI}", key="theme_toggle", help=TOGGLE_LABEL, use_container_width=True):
        st.session_state.theme = "dark" if theme == "light" else "light"
        st.rerun()

st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

# ── Demo mode banner ─────────────────────────────────────────────────────────
from db import is_demo_mode
if is_demo_mode():
    st.markdown(f"""
    <div style="background:{DEMO_BG};border:1px solid {DEMO_BC};
                border-radius:10px;padding:10px 18px;margin-bottom:16px;font-size:0.82rem;color:{DEMO_C};
                display:flex;align-items:center;gap:10px;">
      <span>⚡</span>
      <span><strong>Demo Mode</strong> — MongoDB Atlas not reachable from this environment.
      Showing realistic synthetic data. On your machine, all charts will load live from Atlas.</span>
    </div>
    """, unsafe_allow_html=True)

# ── Page routing ─────────────────────────────────────────────────────────────
page = st.session_state.active_page

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

# ── Global Footer ────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:48px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div style="
  border-top: 1px solid {FTR_BORDER};
  background: {FTR_BG};
  padding: 16px 32px;
  margin: 0 -2rem -2rem -2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
">
  <div style="font-size:0.75rem;color:{FTR_TEXT};display:flex;align-items:center;gap:16px;">
    <span>🎓 <strong style="color:{FTR_TEXT};">Kayfa</strong> Analytics Intelligence</span>
    <span style="color:{FTR_BORDER};">·</span>
    <span>Month 1 · Week 2 · Data Analytics Track</span>
  </div>
  <div style="font-size:0.72rem;color:{FTR_TEXT};display:flex;align-items:center;gap:8px;">
    <span style="width:6px;height:6px;border-radius:50%;background:{FTR_DOT};display:inline-block;"></span>
    <span>Live · MongoDB Atlas</span>
    <span style="color:{FTR_BORDER};">·</span>
    <span>v1.0.0</span>
  </div>
</div>
""", unsafe_allow_html=True)
