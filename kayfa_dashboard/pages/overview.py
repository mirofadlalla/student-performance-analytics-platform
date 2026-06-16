import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import load_collection, plotly_layout, insight_box, kpi_card, page_header, section_title

BLUE   = "#636EFA"   # notebook default plotly blue
RED    = "#EF553B"   # notebook red
GREEN  = "#00CC96"   # notebook green
AMBER  = "#FBD24C"
PURPLE = "#8B5CF6"
CYAN   = "#22D3EE"

def render():
    page_header(
        "Executive Overview",
        "Platform attendance · grade trends · engagement · at-risk signals — all 15 questions"
    )

    with st.spinner("Loading platform data…"):
        master     = load_collection("students_master")
        att_trends = load_collection("attendance_trends")
        grade_tr   = load_collection("grade_trends")
        at_risk    = load_collection("at_risk_students")
        segments   = load_collection("cluster_segments")
        grp_sum    = load_collection("group_summaries")

    if master.empty:
        st.error("⚠️ Could not reach MongoDB Atlas. Check your connection.")
        return

    total_students = len(master)
    avg_grade      = round(master["avg_grade"].mean(), 1) if "avg_grade" in master.columns else "N/A"
    avg_att        = round(master["att_rate_pct"].mean(), 1) if "att_rate_pct" in master.columns else "N/A"
    at_risk_count  = len(at_risk)
    passed_pct     = round((master["avg_grade"] >= 60).sum() / total_students * 100, 1) if "avg_grade" in master.columns else 0

    section_title("KEY PERFORMANCE INDICATORS")
    cols = st.columns(5)
    kpis = [
        ("👥", str(total_students), "Total Students",      "Active cohort",            "neutral"),
        ("📊", f"{avg_grade}",      "Platform Avg Grade",  "↑ vs 60 pass threshold",   "up"),
        ("📅", f"{avg_att}%",       "Avg Attendance Rate", "Platform-wide · Q1",       "neutral"),
        ("⚠️", str(at_risk_count), "At-Risk Students",    "↓ Need intervention · Q14","down"),
        ("✅", f"{passed_pct}%",    "Students Passing",    "≥ 60 avg grade",           "up"),
    ]
    for col, (icon, val, label, trend, dir_) in zip(cols, kpis):
        with col:
            kpi_card(icon, val, label, trend, dir_)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q9 · Attendance & Engagement over time (dual-panel — exactly like notebook) ──
    section_title("Q9 · PLATFORM ATTENDANCE & ENGAGEMENT — 6-MONTH TREND")
    st.markdown('<div class="chart-card"><h3>📈 Monthly Attendance Rate + Engagement Events</h3>', unsafe_allow_html=True)

    if not att_trends.empty and "month" in att_trends.columns and "att_rate" in att_trends.columns:
        att_sorted = att_trends.sort_values("month")

        # Notebook uses make_subplots with 2 rows — line on top, bar on bottom
        eng_monthly = pd.DataFrame({
            "month":  ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06"],
            "events": [5241, 5487, 3983, 5312, 5628, 5103],
        })

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Monthly Attendance Rate (%)", "Monthly Engagement Events"),
            shared_xaxes=True,
            vertical_spacing=0.12,
        )
        fig.add_trace(go.Scatter(
            x=att_sorted["month"], y=att_sorted["att_rate"],
            mode="lines+markers", name="Attendance %",
            line=dict(color=BLUE, width=2),
            marker=dict(size=7),
        ), row=1, col=1)
        fig.add_trace(go.Bar(
            x=eng_monthly["month"], y=eng_monthly["events"],
            name="Total Events", marker_color=RED,
        ), row=2, col=1)
        fig.add_hline(y=77.3, line_dash="dot", line_color=AMBER, line_width=1,
                      annotation_text="Platform avg 77.3%", annotation_font_color=AMBER,
                      row=1, col=1)
        fig.update_layout(
            height=500, title="Platform Attendance & Engagement — 6-Month Trend",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#94A3B8"),
            legend=dict(bgcolor="rgba(11,16,32,0.8)", bordercolor="rgba(77,163,255,0.2)", borderwidth=1),
            margin=dict(l=20, r=20, t=60, b=20),
            hoverlabel=dict(bgcolor="#0F1A33", font=dict(family="Inter", color="#E2E8F0")),
        )
        fig.update_xaxes(gridcolor="rgba(77,163,255,0.06)", tickfont=dict(color="#64748B"))
        fig.update_yaxes(gridcolor="rgba(77,163,255,0.06)", tickfont=dict(color="#64748B"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "A synchronized dip happened in March 2026 — attendance fell to 62.2% and engagement events dropped to 3,983 (the lowest month).",
        "Both attendance and engagement collapsed at the same time, which rules out a platform problem. This points to an external event — most likely a national holiday period or a mid-term exam season that pulled students away from the platform.",
        "Pre-schedule makeup sessions every February for March coverage. Set up automated SMS/email reminders 48 hours before sessions during high-risk months. Track regional school calendars to predict future dips."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q15 · Grade trends per group (exactly like notebook) ─────────────────
    section_title("Q15 · AVERAGE GRADE PER GROUP — MONTHLY TREND")
    st.markdown('<div class="chart-card"><h3>📉 Group Grade Trends — Which groups are trending up or down?</h3>', unsafe_allow_html=True)

    if not grade_tr.empty and "month" in grade_tr.columns and "avg_score" in grade_tr.columns:
        grade_tr_sorted = grade_tr.sort_values("month")
        fig = px.line(
            grade_tr_sorted, x="month", y="avg_score", color="true_group",
            markers=True,
            title="Average Grade per Group — Monthly Trend",
            labels={"month": "Month", "avg_score": "Avg Score", "true_group": "Group"},
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )
        fig.add_hline(y=60, line_dash="dot", line_color="red",
                      annotation_text="Pass threshold (60)")
        fig.update_layout(height=500)
        fig = plotly_layout(fig, height=500)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "Most groups recovered after the March dip, but G07 stayed below the 60-point pass threshold for nearly the entire term. G08 showed the most improvement. G10, GZZ, and G77 showed the sharpest declines.",
        "G07's problem is systemic — not seasonal. It was already weak before March and didn't recover afterward. G10, GZZ, and G77 have tiny student populations (1-3 students), which makes their averages unstable and easily skewed by one bad assessment.",
        "G07 needs an immediate academic intervention plan: assign a dedicated tutor, run weekly grade check-ins, and escalate to the academic lead. G10 should be considered for a merge (see Group Performance page)."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q4 · Attendance vs Grade scatter (matches notebook exactly) ──────────
    section_title("Q4 · ATTENDANCE RATE vs AVERAGE GRADE — CORRELATION")
    st.markdown('<div class="chart-card"><h3>🔗 Attendance Rate vs Average Grade — Pearson r = 0.468 (p &lt; 0.001)</h3>', unsafe_allow_html=True)

    if not master.empty and "att_rate_pct" in master.columns and "avg_grade" in master.columns:
        plot_df = master[["att_rate_pct", "avg_grade"]].dropna()
        fig = px.scatter(
            plot_df, x="att_rate_pct", y="avg_grade",
            trendline="ols",
            title="Attendance Rate vs Average Grade  (r = 0.468, p < 0.001)",
            labels={"att_rate_pct": "Attendance Rate (%)", "avg_grade": "Average Grade"},
            opacity=0.5,
            color_discrete_sequence=[BLUE],
        )
        fig.add_hline(y=60, line_dash="dot", line_color="red", annotation_text="Pass threshold (60)")
        fig = plotly_layout(fig, height=400)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "There is a moderate positive correlation (r = 0.468, p < 0.001) between attendance rate and average grade across all 500 students.",
        "Students who attend more sessions get more direct instruction, practice, and feedback — which naturally leads to better grades. Attendance is a leading indicator: it predicts grades before the final exam.",
        "Make attendance the primary KPI to watch. Trigger an instructor alert whenever a student drops below 70% attendance. Do not wait for grade results — act on attendance data early."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q14 At-risk table ────────────────────────────────────────────────────
    section_title("Q14 · TOP 10 AT-RISK STUDENTS — COMPOSITE RISK SCORE")
    st.markdown('<div class="chart-card"><h3>🚨 Students an instructor should contact first</h3>', unsafe_allow_html=True)

    if not at_risk.empty:
        display_cols = ["full_name", "group_id", "overall_att", "avg_grade", "failed_concepts", "risk_score"]
        available    = [c for c in display_cols if c in at_risk.columns]
        display_df   = at_risk[available].copy()
        rename_map   = {
            "full_name": "Student", "group_id": "Group",
            "overall_att": "Attendance %", "avg_grade": "Avg Grade",
            "failed_concepts": "Failed Concepts", "risk_score": "Risk Score",
        }
        display_df = display_df.rename(columns=rename_map)
        for col_ in ["Attendance %", "Avg Grade", "Risk Score"]:
            if col_ in display_df.columns:
                display_df[col_] = display_df[col_].round(1)

        # Also render as a bar chart (like notebook)
        if "Risk Score" in display_df.columns and "Student" in display_df.columns:
            bar_df = display_df.sort_values("Risk Score")
            fig = px.bar(
                bar_df, x="Risk Score", y="Student",
                orientation="h",
                color="Risk Score",
                color_continuous_scale="Reds",
                title="Top 10 At-Risk Students — Composite Risk Score",
                labels={"Student": "", "Risk Score": "Risk Score"},
            )
            fig.update_layout(yaxis_categoryorder="total ascending")
            fig = plotly_layout(fig, height=360)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Risk Score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%.1f")
            },
            height=280,
        )
    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "Marwan ElBaz (S0453) and Rowan ElBaz (S0201) are the highest-risk students with scores above 83. The top 10 list is dominated by G07 students.",
        "The risk score combines 5 signals: overall attendance (30%), grade (35%), failed concepts (scaled by 2x), recent attendance (20%), and engagement events (15%). Students at the top of this list are failing on all 5 dimensions simultaneously.",
        "Schedule 1:1 instructor calls within 48 hours for the top 3 students. For G07 students, this is a group-level structural problem — a single tutor intervention won't be enough. Escalate the entire group to academic leadership."
    )
