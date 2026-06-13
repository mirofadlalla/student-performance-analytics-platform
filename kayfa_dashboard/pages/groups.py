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
        "Group Performance",
        "Group comparison leaderboard · attendance ranking · grade trends · underperformance alerts"
    )

    with st.spinner("Loading group data…"):
        grp_sum  = load_collection("group_summaries")
        grade_tr = load_collection("grade_trends")
        master   = load_collection("students_master")

    if grp_sum.empty:
        st.error("⚠️ No group data returned.")
        return

    # ── KPIs ────────────────────────────────────────────────────────────────
    section_title("GROUP ECOSYSTEM OVERVIEW")
    total_groups = len(grp_sum)
    best_att_row = grp_sum.loc[grp_sum["att_rate_pct"].idxmax()] if "att_rate_pct" in grp_sum.columns else None
    worst_att_row = grp_sum.loc[grp_sum["att_rate_pct"].idxmin()] if "att_rate_pct" in grp_sum.columns else None
    platform_att = round(grp_sum["att_rate_pct"].mean(), 1) if "att_rate_pct" in grp_sum.columns else 0
    below_avg = int((grp_sum["att_rate_pct"] < platform_att).sum()) if "att_rate_pct" in grp_sum.columns else 0

    cols = st.columns(5)
    kpis = [
        ("🏫", str(total_groups), "Active Groups", "Production cohort", "neutral"),
        ("🥇", best_att_row["group_id"] if best_att_row is not None else "N/A", "Best Attendance", f"{best_att_row['att_rate_pct']:.1f}% rate" if best_att_row is not None else "", "up"),
        ("🔴", worst_att_row["group_id"] if worst_att_row is not None else "N/A", "Lowest Attendance", f"{worst_att_row['att_rate_pct']:.1f}% rate" if worst_att_row is not None else "", "down"),
        ("📉", str(below_avg), "Groups Below Avg", "Att. < platform mean", "down"),
        ("📊", f"{platform_att}%", "Platform Avg Att.", "All groups", "neutral"),
    ]
    for col, (icon, val, label, trend, dir_) in zip(cols, kpis):
        with col:
            kpi_card(icon, val, label, trend, dir_)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Attendance Leaderboard ───────────────────────────────────────────────
    section_title("GROUP ATTENDANCE LEADERBOARD")
    st.markdown('<div class="chart-card"><h3>📊 Attendance Rate per Group — Ranked</h3>', unsafe_allow_html=True)

    if "att_rate_pct" in grp_sum.columns and "group_id" in grp_sum.columns:
        gb = grp_sum.sort_values("att_rate_pct").copy()
        gb["below_avg"] = gb["att_rate_pct"] < platform_att
        gb["color"] = gb["below_avg"].map({True: RED, False: BLUE})

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=gb["group_id"], y=gb["att_rate_pct"],
            marker_color=gb["color"].tolist(),
            text=gb["att_rate_pct"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=11, color="#94A3B8"),
            hovertemplate="<b>%{x}</b><br>Attendance: %{y:.1f}%<extra></extra>",
        ))
        fig.add_hline(y=platform_att, line_dash="dash", line_color=AMBER, line_width=1.5,
                      annotation_text=f"Platform avg: {platform_att:.1f}%",
                      annotation_font_color=AMBER, annotation_font_size=12)
        fig = plotly_layout(fig, height=340)
        fig.update_yaxes(range=[0, 100], title_text="Attendance Rate (%)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "G07 (60.2%) and G10 (65.4%) are the most attendance-challenged groups.",
        "G07 may have scheduling conflicts or an engagement issue with the current instructor.",
        "Audit G07 session times. Survey students about barriers. Consider schedule adjustment."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Grade trend + Group table ────────────────────────────────────
    c1, c2 = st.columns([1.4, 1])

    with c1:
        section_title("GRADE TRENDS BY GROUP")
        st.markdown('<div class="chart-card"><h3>📈 Monthly Average Grade per Group</h3>', unsafe_allow_html=True)
        if not grade_tr.empty and "month" in grade_tr.columns:
            fig = px.line(
                grade_tr.sort_values("month"),
                x="month", y="avg_score", color="true_group",
                markers=True,
                labels={"month": "Month", "avg_score": "Avg Score", "true_group": "Group"},
                color_discrete_sequence=px.colors.qualitative.Plotly,
            )
            fig.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1,
                          annotation_text="Pass threshold 60", annotation_font_color=RED)
            fig = plotly_layout(fig, height=360)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "Most groups recovered after the March dip. G07 remained below the pass threshold throughout.",
            "G07's core issue is systemic — not seasonal — unlike the platform-wide March dip.",
            "Implement weekly grade check-ins specifically for G07. Consider instructor support."
        )

    with c2:
        section_title("GROUP SUMMARY TABLE")
        st.markdown('<div class="chart-card"><h3>🏫 Group Details</h3>', unsafe_allow_html=True)
        if not grp_sum.empty:
            show_cols = ["group_id", "course_name", "instructor", "actual_count", "att_rate_pct"]
            avail = [c for c in show_cols if c in grp_sum.columns]
            display = grp_sum[avail].copy()
            rename_g = {
                "group_id": "Group",
                "course_name": "Course",
                "instructor": "Instructor",
                "actual_count": "Students",
                "att_rate_pct": "Att. %",
            }
            display = display.rename(columns=rename_g)
            if "Att. %" in display.columns:
                display["Att. %"] = display["Att. %"].round(1)
            st.dataframe(
                display.sort_values("Att. %") if "Att. %" in display.columns else display,
                use_container_width=True,
                hide_index=True,
                height=360,
                column_config={
                    "Att. %": st.column_config.ProgressColumn("Att. %", min_value=0, max_value=100, format="%.1f"),
                }
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Scatter: Attendance vs Grade per group ───────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_title("ATTENDANCE vs GRADE — GROUP VIEW")
    st.markdown('<div class="chart-card"><h3>🔗 Group-Level Attendance vs Grade Scatter</h3>', unsafe_allow_html=True)

    if not master.empty and "att_rate_pct" in master.columns and "avg_grade" in master.columns and "group_id" in master.columns:
        grp_agg = master.groupby("group_id").agg(
            avg_att=("att_rate_pct", "mean"),
            avg_grade=("avg_grade", "mean"),
            count=("student_id", "count") if "student_id" in master.columns else ("avg_grade", "count"),
        ).reset_index()

        fig = px.scatter(
            grp_agg,
            x="avg_att", y="avg_grade",
            size="count" if "count" in grp_agg.columns else None,
            color="group_id",
            text="group_id",
            labels={"avg_att": "Avg Attendance (%)", "avg_grade": "Avg Grade", "group_id": "Group"},
            color_discrete_sequence=px.colors.qualitative.Bold,
            size_max=40,
        )
        fig.update_traces(textposition="top center", textfont=dict(size=11, color="#94A3B8"))
        fig.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1)
        fig.add_vline(x=75, line_dash="dot", line_color=AMBER, line_width=1)
        fig = plotly_layout(fig, height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "Groups cluster into two zones: high-att/high-grade and low-att/low-grade.",
        "Attendance is the primary driver of group-level grade performance (r=0.468).",
        "Any group falling below 70% attendance AND 65 avg grade requires immediate academic intervention."
    )

    # ── Group headcount discrepancy ──────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 Stated vs Actual Group Headcount", expanded=False):
        section_title("HEADCOUNT DISCREPANCY AUDIT")
        if "stated_num_students" in grp_sum.columns and "actual_count" in grp_sum.columns:
            disc = grp_sum[["group_id", "stated_num_students", "actual_count"]].copy()
            disc["Discrepancy"] = disc["stated_num_students"] - disc["actual_count"]
            disc = disc.sort_values("Discrepancy", ascending=False)

            fig = go.Figure()
            fig.add_trace(go.Bar(x=disc["group_id"], y=disc["stated_num_students"],
                name="Stated", marker_color=PURPLE, opacity=0.7))
            fig.add_trace(go.Bar(x=disc["group_id"], y=disc["actual_count"],
                name="Actual", marker_color=BLUE))
            fig.update_layout(barmode="group")
            fig = plotly_layout(fig, height=300)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            insight_box(
                "G10 and G05 show a 30-student deficit between stated and actual counts.",
                "Database records were not updated after group restructuring or student transfers.",
                "Sync the groups table with actual student roster data. Audit G77 and GZZ."
            )
