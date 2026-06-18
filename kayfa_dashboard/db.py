"""
db.py — Kayfa Analytics Dashboard
All data loaded from MongoDB Atlas. Zero hardcoded analytics values.
Collections expected:
  students, groups, grades, attendance, concepts, engagement, submissions
Derived/cached views are computed once per TTL from raw collections.
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats

try:
    import certifi
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

# ── Secrets ─────────────────────────────────────────────────────────────────
try:
    MONGO_URI = st.secrets["MONGO_URI"]
    DB_NAME   = st.secrets["DB_NAME"]
except Exception:
    st.error("Missing Streamlit secrets. Configure MONGO_URI and DB_NAME in App Settings → Secrets.")
    st.stop()

# ── Connection ───────────────────────────────────────────────────────────────
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

def is_demo_mode():
    return get_db() is None

# ── Raw collection loader ────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_raw(collection_name: str) -> pd.DataFrame:
    """Load a raw MongoDB collection as a DataFrame."""
    db = get_db()
    if db is None:
        return pd.DataFrame()
    try:
        docs = list(db[collection_name].find({}, {"_id": 0}))
        return pd.DataFrame(docs) if docs else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# ── Derived view: students_master ────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_students_master() -> pd.DataFrame:
    """
    Build master student table from raw students + grades + attendance + concepts + engagement + groups.
    Per-student aggregations:
      - att_rate_pct: % of attended sessions
      - avg_grade: mean of (score/max_score)*100 across all grade records
      - failed_concepts: count of concept records with mastery_status='failed' (or score<60)
      - late_submissions: count of is_late=True submissions
      - login_count: count of event_type='login' engagement events
      - total_events: total engagement events
    """
    students = load_raw("students")
    if students.empty:
        return pd.DataFrame()

    # Attendance rate
    att = load_raw("attendance")
    if not att.empty and "student_id" in att.columns and "status" in att.columns:
        att["attended"] = att["status"].str.lower().str.strip().isin(["attended", "present", "1", "true"])
        att_agg = att.groupby("student_id").agg(
            att_sessions=("attended", "count"),
            att_present=("attended", "sum"),
        ).reset_index()
        att_agg["att_rate_pct"] = (att_agg["att_present"] / att_agg["att_sessions"] * 100).round(1)
        students = students.merge(att_agg[["student_id", "att_rate_pct"]], on="student_id", how="left")
    else:
        students["att_rate_pct"] = np.nan

    # Average grade (normalised to 0-100)
    grades = load_raw("grades")
    if not grades.empty and "student_id" in grades.columns and "score" in grades.columns:
        grades["score"] = pd.to_numeric(grades["score"], errors="coerce")
        grades["max_score"] = pd.to_numeric(grades.get("max_score", pd.Series([100]*len(grades))), errors="coerce").fillna(100)
        grades["norm_score"] = (grades["score"] / grades["max_score"] * 100).clip(0, 100)
        grade_agg = grades.groupby("student_id")["norm_score"].mean().round(1).reset_index()
        grade_agg.columns = ["student_id", "avg_grade"]
        students = students.merge(grade_agg, on="student_id", how="left")
    else:
        students["avg_grade"] = np.nan

    # Failed concepts
    concepts = load_raw("concepts")
    if not concepts.empty and "student_id" in concepts.columns:
        if "mastery_status" in concepts.columns:
            concepts["_failed"] = concepts["mastery_status"].str.lower().str.strip() == "failed"
        elif "score" in concepts.columns:
            concepts["score"] = pd.to_numeric(concepts["score"], errors="coerce")
            concepts["_failed"] = concepts["score"] < 60
        else:
            concepts["_failed"] = False
        fc_agg = concepts.groupby("student_id")["_failed"].sum().reset_index()
        fc_agg.columns = ["student_id", "failed_concepts"]
        students = students.merge(fc_agg, on="student_id", how="left")
    else:
        students["failed_concepts"] = 0

    # Late submissions
    subs = load_raw("submissions")
    if not subs.empty and "student_id" in subs.columns and "is_late" in subs.columns:
        subs["is_late"] = subs["is_late"].astype(str).str.lower().isin(["true", "1", "yes"])
        late_agg = subs.groupby("student_id")["is_late"].sum().reset_index()
        late_agg.columns = ["student_id", "late_submissions"]
        students = students.merge(late_agg, on="student_id", how="left")
    else:
        students["late_submissions"] = 0

    # Engagement
    eng = load_raw("engagement")
    if not eng.empty and "student_id" in eng.columns:
        total_ev = eng.groupby("student_id").size().reset_index(name="total_events")
        students = students.merge(total_ev, on="student_id", how="left")
        if "event_type" in eng.columns:
            logins = eng[eng["event_type"].str.lower() == "login"].groupby("student_id").size().reset_index(name="login_count")
            students = students.merge(logins, on="student_id", how="left")
        else:
            students["login_count"] = np.nan
    else:
        students["total_events"] = 0
        students["login_count"] = 0

    # Group info
    groups = load_raw("groups")
    if not groups.empty and "group_id" in groups.columns and "group_id" in students.columns:
        gcols = ["group_id"]
        for c in ["course_name", "course_id", "instructor"]:
            if c in groups.columns:
                gcols.append(c)
        students = students.merge(groups[gcols].drop_duplicates("group_id"), on="group_id", how="left")

    # Fill numeric NAs
    for col in ["att_rate_pct", "avg_grade", "failed_concepts", "late_submissions", "total_events", "login_count"]:
        if col in students.columns:
            students[col] = pd.to_numeric(students[col], errors="coerce").fillna(0)

    return students

# ── Derived view: group_summaries ────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_group_summaries() -> pd.DataFrame:
    """
    Group-level aggregation from raw data.
    Returns: group_id, course_name, instructor, att_rate_pct, actual_count, stated_num_students, avg_grade
    """
    groups = load_raw("groups")
    master = load_students_master()

    if groups.empty:
        return pd.DataFrame()

    if not master.empty:
        actual = master.groupby("group_id").agg(
            actual_count=("student_id", "count"),
            att_rate_pct=("att_rate_pct", "mean"),
            avg_grade=("avg_grade", "mean"),
        ).reset_index()
        actual["att_rate_pct"] = actual["att_rate_pct"].round(1)
        actual["avg_grade"]    = actual["avg_grade"].round(1)
        groups = groups.merge(actual, on="group_id", how="left")
    else:
        groups["actual_count"] = 0
        groups["att_rate_pct"] = np.nan
        groups["avg_grade"]    = np.nan

    # stated_num_students — from groups table or compute from students
    if "num_students" in groups.columns and "stated_num_students" not in groups.columns:
        groups = groups.rename(columns={"num_students": "stated_num_students"})
    elif "stated_num_students" not in groups.columns:
        groups["stated_num_students"] = groups.get("actual_count", 0)

    return groups

# ── Derived view: at_risk_students ───────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_at_risk_students(top_n: int = 10) -> pd.DataFrame:
    """
    Compute composite risk score from live master data.
    Risk = 0.4*(100-att) + 0.35*(100-avg_grade) + 0.25*(failed_concepts/max_fc*100)
    """
    master = load_students_master()
    if master.empty:
        return pd.DataFrame()

    df = master.copy()
    df["att_rate_pct"]   = pd.to_numeric(df.get("att_rate_pct",   0), errors="coerce").fillna(0)
    df["avg_grade"]      = pd.to_numeric(df.get("avg_grade",      0), errors="coerce").fillna(0)
    df["failed_concepts"]= pd.to_numeric(df.get("failed_concepts", 0), errors="coerce").fillna(0)
    df["total_events"]   = pd.to_numeric(df.get("total_events",   0), errors="coerce").fillna(0)

    max_fc = max(df["failed_concepts"].max(), 1)

    df["risk_score"] = (
        0.40 * (100 - df["att_rate_pct"]) +
        0.35 * (100 - df["avg_grade"]) +
        0.25 * (df["failed_concepts"] / max_fc * 100)
    ).round(1)

    # Recent attendance: last 60 days via raw attendance
    att = load_raw("attendance")
    if not att.empty and "student_id" in att.columns and "session_date" in att.columns:
        att["session_date"] = pd.to_datetime(att["session_date"], errors="coerce")
        recent_cutoff = att["session_date"].max() - pd.Timedelta(days=60)
        recent = att[att["session_date"] >= recent_cutoff].copy()
        recent["attended"] = recent["status"].str.lower().str.strip().isin(["attended", "present", "1", "true"])
        recent_agg = recent.groupby("student_id").agg(
            r_sess=("attended", "count"), r_pres=("attended", "sum")
        ).reset_index()
        recent_agg["recent_att"] = (recent_agg["r_pres"] / recent_agg["r_sess"] * 100).round(1)
        df = df.merge(recent_agg[["student_id", "recent_att"]], on="student_id", how="left")
    else:
        df["recent_att"] = df["att_rate_pct"]

    cols = ["student_id", "full_name", "group_id", "att_rate_pct", "avg_grade",
            "failed_concepts", "recent_att", "total_events", "risk_score"]
    available = [c for c in cols if c in df.columns]
    result = df[available].rename(columns={"att_rate_pct": "overall_att"})
    return result.nlargest(top_n, "risk_score").reset_index(drop=True)

# ── Derived view: concept_failures ───────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_concept_failures() -> pd.DataFrame:
    """
    Per-concept failure rate from raw concepts collection.
    Returns: concept_id, concept_name, course_id, failure_rate_pct, total_students, failed_students
    """
    concepts = load_raw("concepts")
    if concepts.empty:
        return pd.DataFrame()

    if "mastery_status" in concepts.columns:
        concepts["_failed"] = concepts["mastery_status"].str.lower().str.strip() == "failed"
    elif "score" in concepts.columns:
        concepts["score"] = pd.to_numeric(concepts["score"], errors="coerce")
        concepts["_failed"] = concepts["score"] < 60
    else:
        return pd.DataFrame()

    group_cols = []
    for c in ["concept_id", "concept_name", "course_id"]:
        if c in concepts.columns:
            group_cols.append(c)

    if not group_cols:
        return pd.DataFrame()

    agg = concepts.groupby(group_cols).agg(
        total_students=("_failed", "count"),
        failed_students=("_failed", "sum"),
    ).reset_index()
    agg["failure_rate_pct"] = (agg["failed_students"] / agg["total_students"] * 100).round(1)
    return agg.sort_values("failure_rate_pct", ascending=False).reset_index(drop=True)

# ── Derived view: grade_trends ────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_grade_trends() -> pd.DataFrame:
    """
    Monthly average grade per group from raw grades.
    Returns: true_group, month (YYYY-MM), avg_score
    """
    grades = load_raw("grades")
    students = load_raw("students")
    if grades.empty or students.empty:
        return pd.DataFrame()

    # Find date column
    date_col = None
    for c in ["submitted_at", "graded_at", "date", "created_at"]:
        if c in grades.columns:
            date_col = c
            break
    if date_col is None:
        return pd.DataFrame()

    grades["_date"] = pd.to_datetime(grades[date_col], errors="coerce")
    grades = grades.dropna(subset=["_date"])
    grades["month"] = grades["_date"].dt.to_period("M").astype(str)

    grades["score"]     = pd.to_numeric(grades["score"],     errors="coerce")
    grades["max_score"] = pd.to_numeric(grades.get("max_score", pd.Series([100]*len(grades))), errors="coerce").fillna(100)
    grades["norm_score"]= (grades["score"] / grades["max_score"] * 100).clip(0, 100)

    # Join group_id via student_id
    if "group_id" not in grades.columns:
        sid_group = students[["student_id", "group_id"]].dropna().drop_duplicates("student_id")
        grades = grades.merge(sid_group, on="student_id", how="left")

    if "group_id" not in grades.columns:
        return pd.DataFrame()

    trend = grades.groupby(["group_id", "month"])["norm_score"].mean().round(1).reset_index()
    trend.columns = ["true_group", "month", "avg_score"]
    return trend.sort_values(["true_group", "month"]).reset_index(drop=True)

# ── Derived view: attendance_trends ──────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_attendance_trends() -> pd.DataFrame:
    """
    Monthly platform-wide attendance rate from raw attendance.
    Returns: month (YYYY-MM), att_rate
    """
    att = load_raw("attendance")
    if att.empty:
        return pd.DataFrame()

    date_col = None
    for c in ["session_date", "date", "created_at"]:
        if c in att.columns:
            date_col = c
            break
    if date_col is None:
        return pd.DataFrame()

    att["_date"] = pd.to_datetime(att[date_col], errors="coerce")
    att = att.dropna(subset=["_date"])
    att["month"] = att["_date"].dt.to_period("M").astype(str)
    att["attended"] = att["status"].str.lower().str.strip().isin(["attended", "present", "1", "true"])

    trend = att.groupby("month").agg(
        total=("attended", "count"),
        present=("attended", "sum"),
    ).reset_index()
    trend["att_rate"] = (trend["present"] / trend["total"] * 100).round(1)
    return trend[["month", "att_rate"]].sort_values("month").reset_index(drop=True)

# ── Derived view: cluster_segments ───────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_cluster_segments() -> pd.DataFrame:
    """
    K-Means (k=4) segmentation on att_rate_pct + avg_grade from master data.
    Segment labels assigned by centroid rank.
    """
    master = load_students_master()
    if master.empty:
        return pd.DataFrame()

    features = ["att_rate_pct", "avg_grade"]
    df = master.dropna(subset=features).copy()
    if len(df) < 4:
        return df

    try:
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans

        X = StandardScaler().fit_transform(df[features])
        km = KMeans(n_clusters=4, random_state=42, n_init=10)
        df["_cluster"] = km.fit_predict(X)

        # Label by centroid mean grade: highest→High Achievers, lowest→At-Risk
        centroids = df.groupby("_cluster")[["att_rate_pct", "avg_grade"]].mean()
        centroids["score"] = centroids["att_rate_pct"] + centroids["avg_grade"]
        rank_order = centroids["score"].rank(ascending=False).astype(int)
        label_map = {
            1: "High Achievers",
            2: "Average Engaged",
            3: "Struggling",
            4: "At-Risk Disengaged",
        }
        cluster_to_label = {c: label_map[r] for c, r in rank_order.items()}
        df["segment"] = df["_cluster"].map(cluster_to_label)
    except Exception:
        # fallback: rule-based segmentation
        def _seg(row):
            if row["att_rate_pct"] >= 80 and row["avg_grade"] >= 75:
                return "High Achievers"
            elif row["att_rate_pct"] >= 70 and row["avg_grade"] >= 60:
                return "Average Engaged"
            elif row["att_rate_pct"] >= 60:
                return "Struggling"
            return "At-Risk Disengaged"
        df["segment"] = df.apply(_seg, axis=1)

    seg_cols = ["student_id", "full_name", "group_id", "segment", "att_rate_pct", "avg_grade",
                "total_events", "failed_concepts"]
    available = [c for c in seg_cols if c in df.columns]
    return df[available].rename(columns={"att_rate_pct": "att_rate"}).reset_index(drop=True)

# ── Derived view: audit_log ───────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_audit_log() -> pd.DataFrame:
    """Load audit log from MongoDB. Falls back to empty DataFrame (not fake data)."""
    return load_raw("audit_log")

# ── Unified load_collection router ───────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_collection(name: str) -> pd.DataFrame:
    """
    Public API for pages. Routes to the correct derived view.
    Never returns hardcoded data — returns empty DataFrame if MongoDB unreachable.
    """
    routes = {
        "students_master":   load_students_master,
        "group_summaries":   load_group_summaries,
        "at_risk_students":  load_at_risk_students,
        "concept_failures":  load_concept_failures,
        "grade_trends":      load_grade_trends,
        "attendance_trends": load_attendance_trends,
        "cluster_segments":  load_cluster_segments,
        "audit_log":         load_audit_log,
    }
    fn = routes.get(name)
    if fn:
        return fn()
    return load_raw(name)

# ── Compute Pearson r dynamically ─────────────────────────────────────────────
def pearson_r(df: pd.DataFrame, col_x: str, col_y: str) -> tuple[float, float]:
    """Returns (r, p_value) computed from live data."""
    sub = df[[col_x, col_y]].dropna()
    if len(sub) < 3:
        return float("nan"), float("nan")
    r, p = scipy_stats.pearsonr(sub[col_x], sub[col_y])
    return round(r, 3), p

# ── Platform average helper ───────────────────────────────────────────────────
def platform_avg(df: pd.DataFrame, col: str) -> float:
    if df.empty or col not in df.columns:
        return float("nan")
    return round(df[col].mean(), 1)

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

def page_header(title, subtitle):
    st.markdown(f"""
    <div class="page-header">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)
