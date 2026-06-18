import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import load_collection, plotly_layout, insight_box, kpi_card, page_header, section_title

BLUE   = "#4DA3FF"
PURPLE = "#8B5CF6"
CYAN   = "#22D3EE"
RED    = "#F87171"
AMBER  = "#FBD24C"

def render():
    page_header(
        "Student Intelligence",
        "Ranked student profiles · risk segmentation · performance filters · individual drill-down"
    )

    with st.spinner("Loading student data…"):
        master   = load_collection("students_master")
        segments = load_collection("cluster_segments")
        at_risk  = load_collection("at_risk_students")

    if master.empty:
        st.error("⚠️ No data returned from MongoDB Atlas.")
        return

    # ── KPIs ────────────────────────────────────────────────────────────────
    section_title("STUDENT COHORT OVERVIEW")
    total = len(master)
    avg_g = round(master["avg_grade"].mean(), 1) if "avg_grade" in master else 0
    avg_a = round(master["att_rate_pct"].mean(), 1) if "att_rate_pct" in master else 0
    hi_perf = int((master["avg_grade"] >= 75).sum()) if "avg_grade" in master else 0
    struggling = int((master["avg_grade"] < 60).sum()) if "avg_grade" in master else 0

    cols = st.columns(5)
    kpis = [
        ("👥", str(total), "Total Students", "Active cohort", "neutral"),
        ("🏆", str(hi_perf), "High Performers", "Grade ≥ 75", "up"),
        ("⚠️", str(struggling), "Failing Students", "Grade < 60", "down"),
        ("📊", f"{avg_g}", "Platform Avg Grade", "All students", "neutral"),
        ("📅", f"{avg_a}%", "Platform Avg Att.", "All students", "neutral"),
    ]
    for col, (icon, val, label, trend, dir_) in zip(cols, kpis):
        with col:
            kpi_card(icon, val, label, trend, dir_)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters ─────────────────────────────────────────────────────────────
    section_title("FILTERS & SEARCH")
    fc1, fc2, fc3, fc4 = st.columns(4)

    with fc1:
        search = st.text_input("🔍 Search student name", placeholder="e.g. Omar…")
    with fc2:
        groups_list = ["All"] + sorted(master["group_id"].dropna().unique().tolist()) if "group_id" in master.columns else ["All"]
        sel_group = st.selectbox("Group", groups_list)
    with fc3:
        risk_options = ["All", "High Risk", "Medium Risk", "Low Risk"]
        sel_risk = st.selectbox("Risk Level", risk_options)
    with fc4:
        perf_options = ["All", "High Performer (≥75)", "On Track (60-74)", "Failing (<60)"]
        sel_perf = st.selectbox("Performance Tier", perf_options)

    # ── Apply filters ────────────────────────────────────────────────────────
    df = master.copy()
    if search:
        df = df[df["full_name"].str.contains(search, case=False, na=False)] if "full_name" in df.columns else df
    if sel_group != "All" and "group_id" in df.columns:
        df = df[df["group_id"] == sel_group]
    if sel_perf != "All" and "avg_grade" in df.columns:
        if "≥75" in sel_perf:
            df = df[df["avg_grade"] >= 75]
        elif "60-74" in sel_perf:
            df = df[(df["avg_grade"] >= 60) & (df["avg_grade"] < 75)]
        elif "<60" in sel_perf:
            df = df[df["avg_grade"] < 60]

    # Add risk tier
    if "avg_grade" in df.columns and "att_rate_pct" in df.columns:
        def risk_tier(row):
            if row["avg_grade"] < 60 or row["att_rate_pct"] < 65:
                return "🔴 High Risk"
            elif row["avg_grade"] < 70 or row["att_rate_pct"] < 75:
                return "🟡 Medium Risk"
            return "🟢 Low Risk"
        df["Risk Level"] = df.apply(risk_tier, axis=1)
        if sel_risk != "All":
            df = df[df["Risk Level"].str.contains(sel_risk.split()[1], na=False)]

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Ranked Table ─────────────────────────────────────────────────────────
    section_title(f"STUDENT ROSTER — {len(df)} students")
    st.markdown('<div class="chart-card"><h3>🎓 Student Performance Roster</h3>', unsafe_allow_html=True)

    cols_to_show = ["full_name", "group_id", "course_name", "att_rate_pct", "avg_grade",
                    "failed_concepts", "late_submissions", "Risk Level"]
    available = [c for c in cols_to_show if c in df.columns]
    display_df = df[available].copy().sort_values("avg_grade", ascending=False) if "avg_grade" in df.columns else df[available].copy()

    rename_map = {
        "full_name": "Student",
        "group_id": "Group",
        "course_name": "Course",
        "att_rate_pct": "Attendance %",
        "avg_grade": "Avg Grade",
        "failed_concepts": "Failed Concepts",
        "late_submissions": "Late Submissions",
    }
    display_df = display_df.rename(columns=rename_map)
    for col_ in ["Attendance %", "Avg Grade"]:
        if col_ in display_df.columns:
            display_df[col_] = display_df[col_].round(1)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=340,
        column_config={
            "Avg Grade": st.column_config.ProgressColumn("Avg Grade", min_value=0, max_value=100, format="%.1f"),
            "Attendance %": st.column_config.ProgressColumn("Attendance %", min_value=0, max_value=100, format="%.1f"),
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Row: Segment scatter + Risk distribution ─────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_title("SEGMENTATION & RISK INTELLIGENCE")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="chart-card"><h3>🎯 Student Segments — Attendance vs Grade</h3>', unsafe_allow_html=True)
        if not segments.empty and "att_rate" in segments.columns and "avg_grade" in segments.columns:
            color_map = {
                "High Achievers": CYAN,
                "Average Engaged": BLUE,
                "Struggling": AMBER,
                "At-Risk Disengaged": RED,
            }
            fig = px.scatter(
                segments.dropna(subset=["att_rate", "avg_grade", "segment"]),
                x="att_rate", y="avg_grade",
                color="segment",
                color_discrete_map=color_map,
                hover_data=["full_name", "total_events", "failed_concepts"] if "full_name" in segments.columns else None,
                opacity=0.7,
                labels={"att_rate": "Attendance Rate (%)", "avg_grade": "Average Grade", "segment": "Segment"},
            )
            fig.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1)
            fig.add_vline(x=70, line_dash="dot", line_color=AMBER, line_width=1)
            fig = plotly_layout(fig, height=320)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "4 distinct student segments identified via K-Means clustering.",
            "Attendance and grade together predict segment membership with high confidence.",
            "Target the 'At-Risk Disengaged' cluster (bottom-left) for immediate outreach."
        )

    with c2:
        st.markdown('<div class="chart-card"><h3>📊 Grade Distribution</h3>', unsafe_allow_html=True)
        if "avg_grade" in master.columns:
            fig = px.histogram(
                master.dropna(subset=["avg_grade"]),
                x="avg_grade",
                nbins=20,
                color_discrete_sequence=[BLUE],
                labels={"avg_grade": "Average Grade", "count": "Students"},
            )
            fig.add_vline(x=60, line_dash="dot", line_color=RED, line_width=1.5,
                          annotation_text="Pass threshold", annotation_font_color=RED)
            fig.update_traces(marker_line_color="#0B1020", marker_line_width=1)
            fig = plotly_layout(fig, height=320)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "Grade distribution is roughly bell-shaped, centered around 70.",
            "Most students are performing in the on-track range (60-80).",
            "Focus curriculum improvement on the left tail — students scoring below 55."
        )

    # ── Drill down expander ──────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔍 Student Profile Drill-Down", expanded=False):
        student_names = sorted(master["full_name"].dropna().unique().tolist()) if "full_name" in master.columns else []
        sel_student = st.selectbox("Select a student", student_names)
        if sel_student:
            row = master[master["full_name"] == sel_student].iloc[0]
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                st.metric("Avg Grade", f"{row.get('avg_grade', 'N/A'):.1f}" if pd.notna(row.get('avg_grade')) else "N/A")
            with sc2:
                st.metric("Attendance", f"{row.get('att_rate_pct', 'N/A'):.1f}%" if pd.notna(row.get('att_rate_pct')) else "N/A")
            with sc3:
                st.metric("Failed Concepts", int(row.get("failed_concepts", 0)))
            with sc4:
                st.metric("Late Submissions", int(row.get("late_submissions", 0)))
            st.markdown("**Student Details**")
            detail_cols = ["student_id", "full_name", "group_id", "course_name", "instructor", "gender", "age"]
            detail_available = [c for c in detail_cols if c in row.index]
            st.json({col: str(row.get(col, "N/A")) for col in detail_available})
