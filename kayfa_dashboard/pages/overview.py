import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import (load_collection, plotly_layout, insight_box, kpi_card,
                page_header, section_title, chart_config, csv_download_button,
                chart_card_open, chart_card_close, get_theme)

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

    theme = get_theme()
    BLUE   = "#3B82F6" if theme == "light" else "#636EFA"
    RED    = "#EF4444" if theme == "light" else "#EF553B"
    GREEN  = "#10B981" if theme == "light" else "#00CC96"
    AMBER  = "#F59E0B" if theme == "light" else "#FBD24C"
    PURPLE = "#6366F1" if theme == "light" else "#8B5CF6"

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

    # ── Q9 · Attendance & Engagement over time ──────────────────────────────
    section_title("Q9 · PLATFORM ATTENDANCE & ENGAGEMENT — 6-MONTH TREND")
    chart_card_open("📈 Monthly Attendance Rate + Engagement Events")

    if not att_trends.empty and "month" in att_trends.columns and "att_rate" in att_trends.columns:
        att_sorted = att_trends.sort_values("month")
        eng_monthly = pd.DataFrame({
            "month":  ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06"],
            "events": [5241, 5487, 3983, 5312, 5628, 5103],
        })

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Monthly Attendance Rate (%)", "Monthly Engagement Events"),
            shared_xaxes=True,
            vertical_spacing=0.14,
        )
        fig.add_trace(go.Scatter(
            x=att_sorted["month"], y=att_sorted["att_rate"],
            mode="lines+markers", name="Attendance %",
            line=dict(color=BLUE, width=2.5),
            marker=dict(size=8, symbol="circle"),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.06)" if theme == "light" else "rgba(99,102,241,0.06)",
        ), row=1, col=1)
        fig.add_trace(go.Bar(
            x=eng_monthly["month"], y=eng_monthly["events"],
            name="Total Events",
            marker_color=PURPLE,
            marker_line_width=0,
        ), row=2, col=1)
        fig.add_hline(y=77.3, line_dash="dot", line_color=AMBER, line_width=1.5,
                      annotation_text="Platform avg 77.3%",
                      annotation_font_color=AMBER, row=1, col=1)

        fig = plotly_layout(fig, title="", height=520)
        fig.update_xaxes(gridcolor=("rgba(100,116,139,0.1)" if theme == "light" else "rgba(77,163,255,0.06)"),
                         tickfont=dict(color="#64748B"))
        fig.update_yaxes(gridcolor=("rgba(100,116,139,0.1)" if theme == "light" else "rgba(77,163,255,0.06)"),
                         tickfont=dict(color="#64748B"))
        st.plotly_chart(fig, use_container_width=True, config=chart_config())

    # CSV export
    if not att_trends.empty:
        csv_download_button(att_trends, "⬇ Export Attendance Trends CSV",
                            "attendance_trends.csv", key="dl_att_trends")

    chart_card_close()
    insight_box(
        "A synchronized dip happened in March 2026 — attendance fell to 62.2% and engagement events dropped to 3,983 (the lowest month).",
        "Both attendance and engagement collapsed at the same time, which rules out a platform problem. This points to an external event — most likely a national holiday period or a mid-term exam season.",
        "Pre-schedule makeup sessions every February for March coverage. Set up automated SMS/email reminders 48 hours before sessions during high-risk months. Track regional school calendars to predict future dips."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q15 · Grade trends per group ─────────────────────────────────────────
    section_title("Q15 · AVERAGE GRADE PER GROUP — MONTHLY TREND")
    chart_card_open("📉 Group Grade Trends — Which groups are trending up or down?")

    if not grade_tr.empty and "month" in grade_tr.columns and "avg_score" in grade_tr.columns:
        grade_tr_sorted = grade_tr.sort_values("month")
        color_seq = (px.colors.qualitative.Plotly if theme == "dark"
                     else px.colors.qualitative.Safe)
        fig = px.line(
            grade_tr_sorted, x="month", y="avg_score", color="true_group",
            markers=True,
            title="",
            labels={"month": "Month", "avg_score": "Avg Score", "true_group": "Group"},
            color_discrete_sequence=color_seq,
        )
        fig.add_hline(y=60, line_dash="dot", line_color=RED,
                      annotation_text="Pass threshold (60)",
                      annotation_font_color=RED)
        fig = plotly_layout(fig, height=500)
        st.plotly_chart(fig, use_container_width=True, config=chart_config())

    if not grade_tr.empty:
        csv_download_button(grade_tr, "⬇ Export Grade Trends CSV",
                            "grade_trends.csv", key="dl_grade_trends")

    chart_card_close()
    insight_box(
        "Most groups recovered after the March dip, but G07 stayed below the 60-point pass threshold for nearly the entire term. G08 showed the most improvement.",
        "G07's problem is systemic — not seasonal. It was already weak before March and didn't recover afterward. G10 has a tiny student population, making its average unstable.",
        "G07 needs an immediate academic intervention plan: assign a dedicated tutor, run weekly grade check-ins, and escalate to the academic lead."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q4 · Attendance vs Grade scatter ─────────────────────────────────────
    section_title("Q4 · ATTENDANCE RATE vs AVERAGE GRADE — CORRELATION")
    chart_card_open("🔗 Attendance Rate vs Average Grade — Pearson r = 0.468 (p < 0.001)")

    if not master.empty and "att_rate_pct" in master.columns and "avg_grade" in master.columns:
        plot_df = master[["att_rate_pct", "avg_grade"]].dropna()
        fig = px.scatter(
            plot_df, x="att_rate_pct", y="avg_grade",
            trendline="ols",
            title="",
            labels={"att_rate_pct": "Attendance Rate (%)", "avg_grade": "Average Grade"},
            opacity=0.45,
            color_discrete_sequence=[BLUE],
        )
        fig.add_hline(y=60, line_dash="dot", line_color=RED,
                      annotation_text="Pass threshold (60)",
                      annotation_font_color=RED)
        fig = plotly_layout(fig, height=420)
        st.plotly_chart(fig, use_container_width=True, config=chart_config())

    chart_card_close()
    insight_box(
        "There is a moderate positive correlation (r = 0.468, p < 0.001) between attendance rate and average grade across all 500 students.",
        "Students who attend more sessions get more direct instruction, practice, and feedback — which naturally leads to better grades. Attendance is a leading indicator.",
        "Make attendance the primary KPI to watch. Trigger an instructor alert whenever a student drops below 70% attendance. Act on attendance data early — don't wait for grade results."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q14 · At-risk bar chart (no table) ───────────────────────────────────
    section_title("Q14 · TOP 10 AT-RISK STUDENTS — COMPOSITE RISK SCORE")
    chart_card_open("🚨 Students an instructor should contact first")

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

        if "Risk Score" in display_df.columns and "Student" in display_df.columns:
            bar_df = display_df.sort_values("Risk Score")
            color_scale = ("Reds" if theme == "dark" else
                           [[0,"#FEE2E2"],[0.5,"#FCA5A5"],[1,"#DC2626"]])
            fig = px.bar(
                bar_df, x="Risk Score", y="Student",
                orientation="h",
                color="Risk Score",
                color_continuous_scale=color_scale,
                title="",
                labels={"Student": "", "Risk Score": "Risk Score"},
                text=bar_df["Risk Score"].round(1),
                hover_data=["Group", "Attendance %", "Avg Grade", "Failed Concepts"]
                           if "Group" in bar_df.columns else None,
            )
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig.update_layout(
                yaxis_categoryorder="total ascending",
                coloraxis_showscale=False,
            )
            fig = plotly_layout(fig, height=400)
            st.plotly_chart(fig, use_container_width=True, config=chart_config())

        # Risk breakdown sub-charts
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if "Attendance %" in display_df.columns and "Student" in display_df.columns:
            with c1:
                fig_att = px.bar(
                    display_df.sort_values("Attendance %"),
                    x="Attendance %", y="Student", orientation="h",
                    title="Attendance % — At-Risk Students",
                    color="Attendance %",
                    color_continuous_scale=[[0,"#DC2626"],[0.5,"#F59E0B"],[1,"#10B981"]],
                    text=display_df.sort_values("Attendance %")["Attendance %"].round(1),
                )
                fig_att.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig_att.update_layout(coloraxis_showscale=False, yaxis_categoryorder="total ascending")
                fig_att.add_vline(x=70, line_dash="dot", line_color=AMBER,
                                  annotation_text="70% threshold")
                fig_att = plotly_layout(fig_att, height=320)
                st.plotly_chart(fig_att, use_container_width=True, config=chart_config())

        if "Avg Grade" in display_df.columns and "Student" in display_df.columns:
            with c2:
                fig_grd = px.bar(
                    display_df.sort_values("Avg Grade"),
                    x="Avg Grade", y="Student", orientation="h",
                    title="Avg Grade — At-Risk Students",
                    color="Avg Grade",
                    color_continuous_scale=[[0,"#DC2626"],[0.5,"#F59E0B"],[1,"#10B981"]],
                    text=display_df.sort_values("Avg Grade")["Avg Grade"].round(1),
                )
                fig_grd.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                fig_grd.update_layout(coloraxis_showscale=False, yaxis_categoryorder="total ascending")
                fig_grd.add_vline(x=60, line_dash="dot", line_color=RED,
                                  annotation_text="Pass threshold")
                fig_grd = plotly_layout(fig_grd, height=320)
                st.plotly_chart(fig_grd, use_container_width=True, config=chart_config())

        csv_download_button(display_df, "⬇ Export At-Risk Students CSV",
                            "at_risk_students.csv", key="dl_at_risk")

    chart_card_close()
    insight_box(
        "Marwan ElBaz (S0453) and Rowan ElBaz (S0201) are the highest-risk students with scores above 83. The top 10 list is dominated by G07 students.",
        "The risk score combines 5 signals: overall attendance (30%), grade (35%), failed concepts (×2), recent attendance (20%), and engagement events (15%). Students at the top are failing on all 5 dimensions simultaneously.",
        "Schedule 1:1 instructor calls within 48 hours for the top 3 students. For G07 students, this is a group-level structural problem — escalate the entire group to academic leadership."
    )
