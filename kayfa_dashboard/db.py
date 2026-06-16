import streamlit as st
import pandas as pd
import numpy as np
import io

try:
    import certifi
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

# Streamlit Cloud → App Settings → Secrets
try:
    MONGO_URI = st.secrets["MONGO_URI"]
    DB_NAME = st.secrets["DB_NAME"]
except Exception:
    st.error(
        "Missing Streamlit secrets. Please configure MONGO_URI and DB_NAME in App Settings → Secrets."
    )
    st.stop()

# ── Demo data (realistic — mirrors notebook outputs) ─────────────────────────
def _demo_students_master(n=500):
    np.random.seed(42)
    groups = [f"G{str(i).zfill(2)}" for i in range(1, 11)]
    courses = {
        "G01":"C001","G02":"C002","G03":"C002","G04":"C003","G05":"C003",
        "G06":"C004","G07":"C005","G08":"C006","G09":"C007","G10":"C007",
    }
    course_names = {
        "C001":"Python Fundamentals","C002":"Data Structures & Algorithms",
        "C003":"Machine Learning","C004":"Web Development","C005":"Digital Marketing",
        "C006":"Database Design","C007":"Cybersecurity Essentials",
    }
    instructors = {"G01":"Dr. Amira","G02":"Dr. Tarek","G03":"Dr. Tarek","G04":"Dr. Sara",
                   "G05":"Dr. Sara","G06":"Dr. Khaled","G07":"Dr. Laila","G08":"Dr. Omar",
                   "G09":"Dr. Hassan","G10":"Dr. Hassan"}
    names = ["Ahmed Ali","Sara Hassan","Mohamed Said","Nour Khaled","Omar Yasser",
             "Aya Ibrahim","Karim Fady","Mona Tarek","Youssef Sherif","Hana Ziad",
             "Marwan ElBaz","Rowan ElBaz","Adel AbdelHamid","Farida Gamal","Salma Nabil"]
    rows = []
    for i in range(n):
        gid = np.random.choice(groups[:9] if i != 450 else ["G10"], p=None)
        att = np.clip(np.random.normal(77, 12), 30, 100)
        grade = np.clip(att * 0.7 + np.random.normal(20, 8), 35, 98)
        rows.append({
            "student_id": f"S{str(i+1).zfill(4)}",
            "full_name": f"{names[i%len(names)].split()[0]} Student{i+1}",
            "group_id": gid,
            "course_id": courses.get(gid, "C001"),
            "course_name": course_names.get(courses.get(gid, "C001"), "Unknown"),
            "instructor": instructors.get(gid, "Unknown"),
            "att_rate_pct": round(att, 1),
            "avg_grade": round(grade, 1),
            "failed_concepts": max(0, int(np.random.normal(6 if grade < 65 else 3, 3))),
            "late_submissions": max(0, int(np.random.poisson(2))),
            "login_count": max(0, int(np.random.normal(40, 15))),
            "total_events": max(0, int(np.random.normal(80, 25))),
            "gender": np.random.choice(["Male", "Female"]),
            "age": int(np.clip(np.random.normal(24, 4), 17, 40)),
        })
    return pd.DataFrame(rows)

def _demo_group_summaries():
    groups = [f"G{str(i).zfill(2)}" for i in range(1, 11)]
    courses = {
        "G01":"Python Fundamentals","G02":"Data Structures & Algorithms",
        "G03":"Data Structures & Algorithms","G04":"Machine Learning","G05":"Machine Learning",
        "G06":"Web Development","G07":"Digital Marketing","G08":"Database Design",
        "G09":"Cybersecurity Essentials","G10":"Cybersecurity Essentials",
    }
    instructors = {
        "G01":"Dr. Amira","G02":"Dr. Tarek","G03":"Dr. Tarek","G04":"Dr. Sara",
        "G05":"Dr. Sara","G06":"Dr. Khaled","G07":"Dr. Laila","G08":"Dr. Omar",
        "G09":"Dr. Hassan","G10":"Dr. Hassan",
    }
    att_rates = {
        "G01":81.2,"G02":79.4,"G03":75.6,"G04":83.1,"G05":70.2,
        "G06":78.9,"G07":60.2,"G08":82.5,"G09":76.0,"G10":65.4,
    }
    actual = {
        "G01":52,"G02":48,"G03":51,"G04":55,"G05":22,"G06":50,"G07":47,"G08":49,"G09":53,"G10":1
    }
    stated = {
        "G01":50,"G02":50,"G03":50,"G04":50,"G05":52,"G06":50,"G07":50,"G08":50,"G09":50,"G10":31
    }
    rows = []
    for g in groups:
        rows.append({
            "group_id": g,
            "course_name": courses.get(g, "Unknown"),
            "instructor": instructors.get(g, "Unknown"),
            "att_rate_pct": att_rates.get(g, 75.0),
            "actual_count": actual.get(g, 50),
            "stated_num_students": stated.get(g, 50),
        })
    return pd.DataFrame(rows)

def _demo_at_risk():
    return pd.DataFrame([
        {"student_id":"S0453","full_name":"Marwan ElBaz","group_id":"G07","overall_att":42.1,"avg_grade":51.3,"failed_concepts":22,"recent_att":38.0,"total_events":21,"risk_score":84.7},
        {"student_id":"S0201","full_name":"Rowan ElBaz","group_id":"G07","overall_att":44.5,"avg_grade":53.1,"failed_concepts":20,"recent_att":40.0,"total_events":19,"risk_score":83.2},
        {"student_id":"S0312","full_name":"Hossam Fathy","group_id":"G07","overall_att":48.0,"avg_grade":54.7,"failed_concepts":18,"recent_att":45.0,"total_events":24,"risk_score":79.5},
        {"student_id":"S0098","full_name":"Adel AbdelHamid","group_id":"G10","overall_att":50.2,"avg_grade":56.0,"failed_concepts":17,"recent_att":47.0,"total_events":28,"risk_score":76.1},
        {"student_id":"S0177","full_name":"Nada Gamal","group_id":"G07","overall_att":51.0,"avg_grade":57.3,"failed_concepts":16,"recent_att":49.0,"total_events":30,"risk_score":74.3},
        {"student_id":"S0224","full_name":"Seif Mahmoud","group_id":"G05","overall_att":55.4,"avg_grade":58.1,"failed_concepts":15,"recent_att":52.0,"total_events":33,"risk_score":71.8},
        {"student_id":"S0389","full_name":"Malak Sobhi","group_id":"G07","overall_att":57.0,"avg_grade":58.9,"failed_concepts":14,"recent_att":54.0,"total_events":35,"risk_score":69.4},
        {"student_id":"S0044","full_name":"Tarek Wahba","group_id":"G05","overall_att":58.3,"avg_grade":59.2,"failed_concepts":13,"recent_att":56.0,"total_events":37,"risk_score":67.2},
        {"student_id":"S0415","full_name":"Esraa Nour","group_id":"G07","overall_att":60.1,"avg_grade":59.7,"failed_concepts":13,"recent_att":57.0,"total_events":38,"risk_score":65.9},
        {"student_id":"S0062","full_name":"Sherif Adel","group_id":"G07","overall_att":61.0,"avg_grade":59.8,"failed_concepts":12,"recent_att":58.0,"total_events":40,"risk_score":64.1},
    ])

def _demo_concept_failures():
    # Failure rates are per-student percentages (students who failed / students assessed × 100)
    # Values are capped at 100 and validated to be realistic
    concepts = [
        ("C002-K05","Recursion","C002","Data Structures & Algorithms",85.3),
        ("C003-K12","Overfitting & Regularization","C003","Machine Learning",62.1),
        ("C003-K08","Model Evaluation","C003","Machine Learning",58.4),
        ("C005-K03","Funnel Analytics","C005","Digital Marketing",47.2),
        ("C005-K01","SEO Fundamentals","C005","Digital Marketing",45.8),
        ("C002-K11","Dynamic Programming","C002","Data Structures & Algorithms",44.1),
        ("C003-K15","Neural Networks","C003","Machine Learning",42.7),
        ("C002-K03","Trees & Graphs","C002","Data Structures & Algorithms",41.3),
        ("C006-K04","SQL Joins","C006","Database Design",39.5),
        ("C001-K07","OOP Concepts","C001","Python Fundamentals",37.2),
        ("C004-K09","React Hooks","C004","Web Development",35.6),
        ("C007-K02","Encryption Basics","C007","Cybersecurity Essentials",34.8),
        ("C003-K02","Feature Engineering","C003","Machine Learning",33.1),
        ("C002-K09","Sorting Algorithms","C002","Data Structures & Algorithms",31.4),
        ("C001-K05","List Comprehension","C001","Python Fundamentals",28.9),
    ]
    rows = []
    for cid, cname, course_id, course_name, fr in concepts:
        # Validate: failure_rate_pct must be between 0 and 100
        fr_validated = max(0.0, min(100.0, fr))
        rows.append({
            "concept_id": cid,
            "concept_name": cname,
            "course_id": course_id,
            "course_name": course_name,
            "failure_rate_pct": fr_validated,
        })
    return pd.DataFrame(rows)

def _demo_grade_trends():
    months = ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06"]
    groups = [f"G{str(i).zfill(2)}" for i in range(1, 11)]
    base = {"G01":73,"G02":71,"G03":70,"G04":75,"G05":68,"G06":72,"G07":58,"G08":74,"G09":71,"G10":62}
    rows = []
    np.random.seed(0)
    for g in groups:
        for i, m in enumerate(months):
            dip = -5 if m == "2026-03" else 0
            rows.append({"true_group":g,"month":m,"avg_score":round(base[g]+dip+np.random.normal(0,1.5),1)})
    return pd.DataFrame(rows)

def _demo_attendance_trends():
    months = ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06"]
    rates  = [79.1, 80.4, 62.2, 78.9, 81.3, 79.7]
    return pd.DataFrame({"month": months, "att_rate": rates})

def _demo_cluster_segments():
    np.random.seed(1)
    n = 500
    segs = np.random.choice(
        ["High Achievers","Average Engaged","Struggling","At-Risk Disengaged"],
        n, p=[0.37, 0.28, 0.21, 0.14]
    )
    att_map = {"High Achievers":(84,8),"Average Engaged":(77,10),"Struggling":(72,10),"At-Risk Disengaged":(61,10)}
    grd_map = {"High Achievers":(76,6),"Average Engaged":(70,8),"Struggling":(72,9),"At-Risk Disengaged":(57,7)}
    rows = []
    for i, seg in enumerate(segs):
        a_mu, a_sd = att_map[seg]; g_mu, g_sd = grd_map[seg]
        rows.append({
            "student_id": f"S{str(i+1).zfill(4)}",
            "full_name": f"Student {i+1}",
            "segment": seg,
            "att_rate": round(float(np.clip(np.random.normal(a_mu, a_sd), 30, 100)), 1),
            "avg_grade": round(float(np.clip(np.random.normal(g_mu, g_sd), 35, 98)), 1),
            "total_events": max(0, int(np.random.normal(60, 25))),
            "failed_concepts": max(0, int(np.random.normal(5 if "Risk" not in seg else 13, 3))),
        })
    return pd.DataFrame(rows)

DEMO_DATA = {
    "students_master":    _demo_students_master,
    "group_summaries":    _demo_group_summaries,
    "at_risk_students":   _demo_at_risk,
    "concept_failures":   _demo_concept_failures,
    "grade_trends":       _demo_grade_trends,
    "attendance_trends":  _demo_attendance_trends,
    "cluster_segments":   _demo_cluster_segments,
}

@st.cache_resource(show_spinner=False)
def get_db():
    if not MONGO_AVAILABLE:
        return None
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client[DB_NAME]
    except Exception:
        return None

@st.cache_data(ttl=300, show_spinner=False)
def load_collection(collection_name: str) -> pd.DataFrame:
    db = get_db()
    if db is not None:
        try:
            docs = list(db[collection_name].find({}, {"_id": 0}))
            if docs:
                df = pd.DataFrame(docs)
                # Validate concept failure rates from live DB
                if collection_name == "concept_failures" and "failure_rate_pct" in df.columns:
                    df["failure_rate_pct"] = df["failure_rate_pct"].clip(0, 100)
                return df
        except Exception:
            pass
    # Fallback to demo data
    if collection_name in DEMO_DATA:
        return DEMO_DATA[collection_name]()
    return pd.DataFrame()

def is_demo_mode():
    return get_db() is None

def get_theme():
    """Return 'light' or 'dark' based on session state."""
    return st.session_state.get("theme", "light")

# ── Shared UI helpers ────────────────────────────────────────────────────────
def plotly_layout(fig, title="", height=420):
    theme = get_theme()
    if theme == "dark":
        paper_bg   = "rgba(0,0,0,0)"
        plot_bg    = "rgba(0,0,0,0)"
        font_color = "#94A3B8"
        tick_color = "#64748B"
        grid_color = "rgba(77,163,255,0.06)"
        line_color = "rgba(77,163,255,0.1)"
        legend_bg  = "rgba(11,16,32,0.8)"
        legend_bc  = "rgba(77,163,255,0.2)"
        hover_bg   = "#0F1A33"
        hover_fc   = "#E2E8F0"
        title_color = "#CBD5E1"
    else:
        paper_bg   = "rgba(0,0,0,0)"
        plot_bg    = "rgba(248,250,252,0.8)"
        font_color = "#334155"
        tick_color = "#64748B"
        grid_color = "rgba(100,116,139,0.12)"
        line_color = "rgba(100,116,139,0.2)"
        legend_bg  = "rgba(255,255,255,0.95)"
        legend_bc  = "rgba(100,116,139,0.2)"
        hover_bg   = "#FFFFFF"
        hover_fc   = "#0F172A"
        title_color = "#0F172A"

    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=title_color, family="Inter"), x=0),
        height=height,
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(family="Inter", color=font_color, size=12),
        legend=dict(
            bgcolor=legend_bg, bordercolor=legend_bc,
            borderwidth=1, font=dict(size=11, color=font_color)
        ),
        xaxis=dict(
            gridcolor=grid_color, linecolor=line_color,
            tickfont=dict(color=tick_color, size=11),
            title_font=dict(color=font_color)
        ),
        yaxis=dict(
            gridcolor=grid_color, linecolor=line_color,
            tickfont=dict(color=tick_color, size=11),
            title_font=dict(color=font_color)
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(
            bgcolor=hover_bg, bordercolor=legend_bc,
            font=dict(family="Inter", color=hover_fc, size=12)
        ),
    )
    return fig

def chart_config():
    """Return Plotly config that enables interactive zoom/pan toolbar."""
    return {
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
        "scrollZoom": True,
        "toImageButtonOptions": {
            "format": "png",
            "filename": "kayfa_chart",
            "height": 600,
            "width": 1200,
            "scale": 2,
        },
    }

def csv_download_button(df: pd.DataFrame, label: str = "⬇ Export CSV", filename: str = "data.csv", key: str = None):
    """Render a themed CSV download button."""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    theme = get_theme()
    btn_bg = "#F1F5F9" if theme == "light" else "rgba(77,163,255,0.08)"
    btn_color = "#334155" if theme == "light" else "#94A3B8"
    btn_border = "1px solid #CBD5E1" if theme == "light" else "1px solid rgba(77,163,255,0.2)"
    st.download_button(
        label=label,
        data=buf.getvalue(),
        file_name=filename,
        mime="text/csv",
        key=key,
    )

def insight_box(what, why, action):
    theme = get_theme()
    if theme == "dark":
        bg = "linear-gradient(135deg, rgba(77,163,255,0.04) 0%, rgba(139,92,246,0.04) 100%)"
        border = "1px solid rgba(77,163,255,0.12)"
        left = "3px solid #4DA3FF"
        row_color = "#CBD5E1"
    else:
        bg = "linear-gradient(135deg, rgba(59,130,246,0.04) 0%, rgba(99,102,241,0.04) 100%)"
        border = "1px solid rgba(59,130,246,0.15)"
        left = "3px solid #3B82F6"
        row_color = "#334155"
    st.markdown(f"""
    <div style="background:{bg};border:{border};border-left:{left};border-radius:10px;
                padding:16px 20px;margin-top:12px;font-size:0.85rem;line-height:1.6;">
      <div style="margin-bottom:7px;color:{row_color}"><span style="font-weight:600;margin-right:6px;">🟡 What happened:</span>{what}</div>
      <div style="margin-bottom:7px;color:{row_color}"><span style="font-weight:600;margin-right:6px;">🧠 Why it happened:</span>{why}</div>
      <div style="color:{row_color}"><span style="font-weight:600;margin-right:6px;">🎯 Recommendation:</span>{action}</div>
    </div>
    """, unsafe_allow_html=True)

def kpi_card(icon, value, label, trend, trend_dir="neutral"):
    theme = get_theme()
    if theme == "dark":
        bg = "linear-gradient(135deg, rgba(15,26,51,0.9) 0%, rgba(11,16,32,0.9) 100%)"
        border = "1px solid rgba(77,163,255,0.18)"
        val_color = "#F1F5F9"
        label_color = "#64748B"
    else:
        bg = "linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)"
        border = "1px solid #E2E8F0"
        val_color = "#0F172A"
        label_color = "#64748B"

    trend_colors = {
        "up":      ("#22C55E" if theme == "dark" else "#16A34A"),
        "down":    ("#F87171" if theme == "dark" else "#DC2626"),
        "neutral": ("#94A3B8" if theme == "dark" else "#64748B"),
    }
    tc = trend_colors.get(trend_dir, trend_colors["neutral"])
    st.markdown(f"""
    <div style="background:{bg};border:{border};border-radius:14px;padding:20px 22px;
                position:relative;overflow:hidden;transition:all 0.3s ease;
                box-shadow:0 1px 3px rgba(0,0,0,0.06);">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;
                  background:linear-gradient(90deg,#3B82F6,#6366F1);"></div>
      <div style="font-size:1.5rem;margin-bottom:10px;">{icon}</div>
      <div style="font-size:2rem;font-weight:700;color:{val_color};line-height:1;">{value}</div>
      <div style="font-size:0.75rem;color:{label_color};font-weight:500;
                  text-transform:uppercase;letter-spacing:0.08em;margin-top:5px;">{label}</div>
      <div style="font-size:0.78rem;margin-top:8px;font-weight:500;color:{tc};">{trend}</div>
    </div>
    """, unsafe_allow_html=True)

def page_header(title, subtitle):
    theme = get_theme()
    if theme == "dark":
        bg = "linear-gradient(135deg, rgba(77,163,255,0.08) 0%, rgba(139,92,246,0.08) 100%)"
        border = "1px solid rgba(77,163,255,0.2)"
        h1_grad = "linear-gradient(135deg, #4DA3FF 0%, #8B5CF6 100%)"
        p_color = "#94A3B8"
    else:
        bg = "linear-gradient(135deg, rgba(59,130,246,0.06) 0%, rgba(99,102,241,0.06) 100%)"
        border = "1px solid rgba(59,130,246,0.15)"
        h1_grad = "linear-gradient(135deg, #2563EB 0%, #6366F1 100%)"
        p_color = "#64748B"
    st.markdown(f"""
    <div style="background:{bg};border:{border};border-radius:16px;
                padding:28px 32px;margin-bottom:28px;position:relative;overflow:hidden;">
      <div style="position:absolute;top:-50%;left:-20%;width:60%;height:200%;
                  background:radial-gradient(ellipse,rgba(59,130,246,0.06) 0%,transparent 70%);
                  pointer-events:none;"></div>
      <h1 style="font-size:1.9rem;font-weight:700;background:{h1_grad};
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                 margin:0 0 6px 0;">{title}</h1>
      <p style="color:{p_color};font-size:0.92rem;margin:0;font-weight:400;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def section_title(text):
    theme = get_theme()
    color = "#2563EB" if theme == "light" else "#4DA3FF"
    st.markdown(
        f'<div style="font-size:0.78rem;font-weight:600;color:{color};text-transform:uppercase;'
        f'letter-spacing:0.12em;margin-bottom:16px;margin-top:8px;">{text}</div>',
        unsafe_allow_html=True
    )

def chart_card_open(title_text):
    theme = get_theme()
    if theme == "dark":
        bg = "rgba(11,16,32,0.7)"
        border = "1px solid rgba(77,163,255,0.14)"
        h3_color = "#CBD5E1"
        bb = "1px solid rgba(77,163,255,0.1)"
    else:
        bg = "#FFFFFF"
        border = "1px solid #E2E8F0"
        h3_color = "#1E293B"
        bb = "1px solid #F1F5F9"
    st.markdown(
        f'<div style="background:{bg};border:{border};border-radius:16px;padding:24px;'
        f'margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
        f'<h3 style="font-size:1rem;font-weight:600;color:{h3_color};margin:0 0 16px 0;'
        f'border-bottom:{bb};padding-bottom:12px;">{title_text}</h3>',
        unsafe_allow_html=True
    )

def chart_card_close():
    st.markdown('</div>', unsafe_allow_html=True)
