import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
        "Executive Overview",
        "Real-time cohort health · platform attendance · grade correlation · at-risk signals"
    )

    # ── Load data ───────────────────────────────────────────────────────────
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

    # ── Derive KPIs ─────────────────────────────────────────────────────────
    total_students = len(master)
    avg_grade      = round(master["avg_grade"].mean(), 1) if "avg_grade" in master.columns else "N/A"
    avg_att        = round(master["att_rate_pct"].mean(), 1) if "att_rate_pct" in master.columns else "N/A"
    at_risk_count  = len(at_risk)

    passed_pct = 0
    if "avg_grade" in master.columns:
        passed_pct = round((master["avg_grade"] >= 60).sum() / total_students * 100, 1)

    # ── KPI Strip ───────────────────────────────────────────────────────────
    section_title("KEY PERFORMANCE INDICATORS")
    cols = st.columns(5)
    kpis = [
        ("👥", str(total_students), "Total Students", "Active cohort", "neutral"),
        ("📊", f"{avg_grade}", "Platform Avg Grade", "↑ vs 60 pass threshold", "up"),
        ("📅", f"{avg_att}%", "Avg Attendance Rate", "Platform-wide", "neutral"),
        ("⚠️", str(at_risk_count), "At-Risk Students", "↓ Need intervention", "down"),
        ("✅", f"{passed_pct}%", "Students Passing", "≥ 60 avg grade", "up"),
    ]
    for col, (icon, val, label, trend, dir_) in zip(cols, kpis):
        with col:
            kpi_card(icon, val, label, trend, dir_)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Attendance trend + Grade trend ───────────────────────────────
    section_title("PLATFORM TRENDS")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="chart-card"><h3>📈 Monthly Attendance Rate</h3>', unsafe_allow_html=True)
        if not att_trends.empty and "month" in att_trends.columns:
            att_trends = att_trends.sort_values("month")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=att_trends["month"], y=att_trends["att_rate"],
                mode="lines+markers",
                line=dict(color=BLUE, width=2.5),
                marker=dict(size=7, color=BLUE, line=dict(color="#0B1020", width=2)),
                fill="tozeroy",
                fillcolor="rgba(77,163,255,0.06)",
                name="Attendance %",
            ))
            fig.add_hline(y=77.3, line_dash="dot", line_color=AMBER, line_width=1,
                          annotation_text="Platform avg 77.3%", annotation_font_color=AMBER,
                          annotation_font_size=11)
            fig = plotly_layout(fig, height=300)
            fig.update_yaxes(range=[50, 100], title_text="Attendance %")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "Platform attendance dipped to 62.2% in March 2026.",
            "External seasonal factor — likely a national exam period or holiday break.",
            "Pre-schedule makeup sessions in March. Send SMS reminders 48 hrs before sessions."
        )

    with c2:
        st.markdown('<div class="chart-card"><h3>📉 Average Grade by Group · Monthly</h3>', unsafe_allow_html=True)
        if not grade_tr.empty:
            grade_tr = grade_tr.sort_values("month")
            fig = px.line(
                grade_tr, x="month", y="avg_score", color="true_group",
                markers=True,
                color_discrete_sequence=px.colors.qualitative.Plotly,
            )
            fig.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1,
                          annotation_text="Pass threshold 60", annotation_font_color=RED,
                          annotation_font_size=11)
            fig = plotly_layout(fig, height=300)
            fig.update_yaxes(title_text="Avg Score")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "G07 stayed below the 60-point pass threshold for most of the term.",
            "G07 has the platform's lowest attendance (60.2%) and highest concept failure rate.",
            "Assign a dedicated tutor to G07. Escalate to academic lead within 7 days."
        )

    # ── Row 2: Segment donut + At-risk table ────────────────────────────────
    section_title("COHORT HEALTH INTELLIGENCE")
    c3, c4 = st.columns([1, 1.6])

    with c3:
        st.markdown('<div class="chart-card"><h3>🎯 Student Segments</h3>', unsafe_allow_html=True)
        if not segments.empty and "segment" in segments.columns:
            seg_counts = segments["segment"].value_counts().reset_index()
            seg_counts.columns = ["segment", "count"]
            color_map = {
                "High Achievers": CYAN,
                "Average Engaged": BLUE,
                "Struggling": AMBER,
                "At-Risk Disengaged": RED,
            }
            colors = [color_map.get(s, PURPLE) for s in seg_counts["segment"]]
            fig = go.Figure(go.Pie(
                labels=seg_counts["segment"],
                values=seg_counts["count"],
                hole=0.6,
                marker=dict(colors=colors, line=dict(color="#0B1020", width=2)),
                textfont=dict(size=11, color="#94A3B8"),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#94A3B8"),
                legend=dict(font=dict(size=11, color="#94A3B8")),
                margin=dict(l=10, r=10, t=10, b=10),
                height=260,
                annotations=[dict(
                    text=f"<b>{total_students}</b><br>Students",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14, color="#E2E8F0", family="Inter"),
                )],
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "68 students are classified as At-Risk Disengaged.",
            "Low attendance (61.5%), low grades (57.6), and 13+ failed concepts signal dropout risk.",
            "Trigger an automated re-engagement campaign for this segment immediately."
        )

    with c4:
        st.markdown('<div class="chart-card"><h3>🚨 Top At-Risk Students — Composite Risk Score</h3>', unsafe_allow_html=True)
        if not at_risk.empty:
            display_cols = ["full_name", "group_id", "overall_att", "avg_grade", "failed_concepts", "risk_score"]
            available = [c for c in display_cols if c in at_risk.columns]
            display_df = at_risk[available].copy()

            # rename for display
            rename_map = {
                "full_name": "Student",
                "group_id": "Group",
                "overall_att": "Attendance %",
                "avg_grade": "Avg Grade",
                "failed_concepts": "Failed Concepts",
                "risk_score": "Risk Score",
            }
            display_df = display_df.rename(columns=rename_map)
            if "Risk Score" in display_df.columns:
                display_df["Risk Score"] = display_df["Risk Score"].round(1)
            if "Attendance %" in display_df.columns:
                display_df["Attendance %"] = display_df["Attendance %"].round(1)
            if "Avg Grade" in display_df.columns:
                display_df["Avg Grade"] = display_df["Avg Grade"].round(1)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Risk Score": st.column_config.ProgressColumn(
                        "Risk Score", min_value=0, max_value=100, format="%.1f"
                    )
                },
                height=260,
            )
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "Marwan ElBaz and Rowan ElBaz (G07) have risk scores above 83 — highest in the cohort.",
            "Both show 20-22 failed concepts and below-50% attendance in the last 60 days.",
            "Schedule 1:1 instructor calls within 48 hours. Consider temporary grade recovery plan."
        )

    # ── Row 3: Attendance vs Grade correlation ──────────────────────────────
    section_title("CORRELATION INTELLIGENCE")
    st.markdown('<div class="chart-card"><h3>🔗 Attendance Rate vs Average Grade — Pearson r = 0.468 (p &lt; 0.001)</h3>', unsafe_allow_html=True)
    if not master.empty and "att_rate_pct" in master.columns and "avg_grade" in master.columns:
        plot_df = master[["att_rate_pct", "avg_grade", "group_id"]].dropna()
        fig = px.scatter(
            plot_df, x="att_rate_pct", y="avg_grade",
            color="group_id" if "group_id" in plot_df.columns else None,
            trendline="ols",
            opacity=0.55,
            labels={"att_rate_pct": "Attendance Rate (%)", "avg_grade": "Average Grade", "group_id": "Group"},
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )
        fig.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1)
        fig = plotly_layout(fig, height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "Moderate positive correlation (r=0.468) between attendance and grades across all 500 students.",
        "Students who attend more sessions have more exposure to instruction and active learning.",
        "Make attendance the primary leading KPI. Intervene when a student drops below 70%."
    )
