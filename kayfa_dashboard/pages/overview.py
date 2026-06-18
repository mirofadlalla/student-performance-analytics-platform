import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import (load_collection, plotly_layout, insight_box, kpi_card,
                page_header, section_title, pearson_r, platform_avg)

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

    with st.spinner("Loading platform data…"):
        master     = load_collection("students_master")
        att_trends = load_collection("attendance_trends")
        grade_tr   = load_collection("grade_trends")
        at_risk    = load_collection("at_risk_students")
        segments   = load_collection("cluster_segments")
        grp_sum    = load_collection("group_summaries")

    if master.empty:
        st.error("⚠️ Could not reach MongoDB Atlas. Check your connection and secrets.")
        return

    # ── KPIs (all computed from live data) ─────────────────────────────────
    total_students = len(master)
    avg_grade      = platform_avg(master, "avg_grade")
    avg_att        = platform_avg(master, "att_rate_pct")
    at_risk_count  = len(at_risk)
    passed_pct     = round((master["avg_grade"] >= 60).sum() / total_students * 100, 1) if "avg_grade" in master.columns and total_students > 0 else 0

    section_title("KEY PERFORMANCE INDICATORS")
    cols = st.columns(5)
    kpis = [
        ("👥", str(total_students),    "Total Students",     "Active cohort",              "neutral"),
        ("📊", f"{avg_grade}",          "Platform Avg Grade", "↑ vs 60 pass threshold",     "up"),
        ("📅", f"{avg_att}%",           "Avg Attendance Rate","Platform-wide",              "neutral"),
        ("⚠️", str(at_risk_count),      "At-Risk Students",   "↓ Need intervention",        "down"),
        ("✅", f"{passed_pct}%",        "Students Passing",   "≥ 60 avg grade",             "up"),
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
        if not att_trends.empty and "month" in att_trends.columns and "att_rate" in att_trends.columns:
            att_trends = att_trends.sort_values("month")
            plat_att_avg = round(att_trends["att_rate"].mean(), 1)
            # Find the dip month dynamically
            dip_row = att_trends.loc[att_trends["att_rate"].idxmin()]
            dip_month = dip_row["month"]
            dip_val   = round(dip_row["att_rate"], 1)

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
            fig.add_hline(y=plat_att_avg, line_dash="dot", line_color=AMBER, line_width=1,
                          annotation_text=f"Period avg {plat_att_avg}%",
                          annotation_font_color=AMBER, annotation_font_size=11)
            fig = plotly_layout(fig, height=300)
            fig.update_yaxes(range=[max(0, att_trends["att_rate"].min()-10), 100], title_text="Attendance %")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            insight_box(
                f"Platform attendance dipped to {dip_val}% in {dip_month}.",
                "Possible external factor — seasonal exam period or holiday break.",
                "Pre-schedule makeup sessions around low-attendance periods. Send SMS reminders 48 hrs before sessions."
            )
        else:
            st.info("No attendance trend data available.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><h3>📉 Average Grade by Group · Monthly</h3>', unsafe_allow_html=True)
        if not grade_tr.empty and "month" in grade_tr.columns and "avg_score" in grade_tr.columns:
            grade_tr = grade_tr.sort_values("month")
            # Find worst group dynamically
            grp_avg = grade_tr.groupby("true_group")["avg_score"].mean()
            worst_grp = grp_avg.idxmin() if not grp_avg.empty else "N/A"
            worst_grp_att = round(grp_sum.loc[grp_sum["group_id"] == worst_grp, "att_rate_pct"].values[0], 1) if (
                not grp_sum.empty and "group_id" in grp_sum.columns and worst_grp in grp_sum["group_id"].values
            ) else None

            fig = px.line(
                grade_tr, x="month", y="avg_score", color="true_group",
                markers=True,
                color_discrete_sequence=px.colors.qualitative.Plotly,
                labels={"true_group": "Group", "avg_score": "Avg Score", "month": "Month"},
            )
            fig.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1,
                          annotation_text="Pass threshold 60", annotation_font_color=RED,
                          annotation_font_size=11)
            fig = plotly_layout(fig, height=300)
            fig.update_yaxes(title_text="Avg Score")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            below_threshold = grade_tr[grade_tr["avg_score"] < 60]["true_group"].unique().tolist()
            below_str = ", ".join(below_threshold[:3]) if below_threshold else "None"
            att_note = f" and lowest attendance ({worst_grp_att}%)" if worst_grp_att else ""
            insight_box(
                f"{below_str or 'Some groups'} stayed below the 60-point pass threshold for part of the term.",
                f"{worst_grp} has the lowest avg grade{att_note} and the highest concept failure rate.",
                f"Assign a dedicated tutor to {worst_grp}. Escalate to academic lead within 7 days."
            )
        else:
            st.info("No grade trend data available.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 2: Segment donut + At-risk table ────────────────────────────────
    section_title("COHORT HEALTH INTELLIGENCE")
    c3, c4 = st.columns([1, 1.6])

    with c3:
        st.markdown('<div class="chart-card"><h3>🎯 Student Segments (K-Means)</h3>', unsafe_allow_html=True)
        if not segments.empty and "segment" in segments.columns:
            seg_counts = segments["segment"].value_counts().reset_index()
            seg_counts.columns = ["segment", "count"]
            color_map = {
                "High Achievers":     CYAN,
                "Average Engaged":    BLUE,
                "Struggling":         AMBER,
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
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#94A3B8"),
                legend=dict(font=dict(size=11, color="#94A3B8")),
                margin=dict(l=10, r=10, t=10, b=10), height=260,
                annotations=[dict(
                    text=f"<b>{total_students}</b><br>Students",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=14, color="#E2E8F0", family="Inter"),
                )],
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            atrisk_seg = segments[segments["segment"] == "At-Risk Disengaged"]
            n_atrisk   = len(atrisk_seg)
            att_col    = "att_rate" if "att_rate" in atrisk_seg.columns else None
            grd_col    = "avg_grade" if "avg_grade" in atrisk_seg.columns else None
            fc_col     = "failed_concepts" if "failed_concepts" in atrisk_seg.columns else None
            avg_att_ar = round(atrisk_seg[att_col].mean(), 1) if att_col else "N/A"
            avg_grd_ar = round(atrisk_seg[grd_col].mean(), 1) if grd_col else "N/A"
            avg_fc_ar  = round(atrisk_seg[fc_col].mean(), 1) if fc_col else "N/A"

            insight_box(
                f"{n_atrisk} students are classified as At-Risk Disengaged.",
                f"Low attendance ({avg_att_ar}%), low grades ({avg_grd_ar}), and {avg_fc_ar}+ failed concepts signal dropout risk.",
                "Trigger an automated re-engagement campaign for this segment immediately."
            )
        else:
            st.info("No segment data available.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="chart-card"><h3>🚨 Top At-Risk Students — Composite Risk Score</h3>', unsafe_allow_html=True)
        if not at_risk.empty:
            display_cols = ["full_name", "group_id", "overall_att", "avg_grade", "failed_concepts", "risk_score"]
            available = [c for c in display_cols if c in at_risk.columns]
            display_df = at_risk[available].copy().rename(columns={
                "full_name": "Student", "group_id": "Group",
                "overall_att": "Attendance %", "avg_grade": "Avg Grade",
                "failed_concepts": "Failed Concepts", "risk_score": "Risk Score",
            })
            for col_ in ["Risk Score", "Attendance %", "Avg Grade"]:
                if col_ in display_df.columns:
                    display_df[col_] = display_df[col_].round(1)

            st.dataframe(
                display_df, use_container_width=True, hide_index=True,
                column_config={
                    "Risk Score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%.1f")
                },
                height=260,
            )
            # Dynamic insight from top 2
            if len(at_risk) >= 2:
                top1 = at_risk.iloc[0]
                top2 = at_risk.iloc[1]
                insight_box(
                    f"{top1.get('full_name','Top student')} ({top1.get('group_id','')}) has the highest risk score at {top1.get('risk_score', 'N/A')}.",
                    f"Shows {top1.get('failed_concepts','N/A')} failed concepts and {top1.get('overall_att','N/A')}% overall attendance.",
                    "Schedule 1:1 instructor calls within 48 hours. Consider a temporary grade recovery plan."
                )
        else:
            st.info("No at-risk data computed.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 3: Attendance vs Grade scatter with live Pearson r ──────────────
    section_title("CORRELATION INTELLIGENCE")
    if not master.empty and "att_rate_pct" in master.columns and "avg_grade" in master.columns:
        r_val, p_val = pearson_r(master, "att_rate_pct", "avg_grade")
        p_str = "< 0.001" if p_val < 0.001 else f"= {p_val:.3f}"
        st.markdown(
            f'<div class="chart-card"><h3>🔗 Attendance Rate vs Average Grade — Pearson r = {r_val} (p {p_str})</h3>',
            unsafe_allow_html=True
        )
        plot_df = master[["att_rate_pct", "avg_grade", "group_id"]].dropna()
        fig = px.scatter(
            plot_df, x="att_rate_pct", y="avg_grade",
            color="group_id" if "group_id" in plot_df.columns else None,
            trendline="ols", opacity=0.55,
            labels={"att_rate_pct": "Attendance Rate (%)", "avg_grade": "Average Grade", "group_id": "Group"},
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )
        fig.add_hline(y=60, line_dash="dot", line_color=RED, line_width=1)
        fig = plotly_layout(fig, height=360)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

        corr_str = "strong" if abs(r_val) >= 0.6 else "moderate" if abs(r_val) >= 0.4 else "weak"
        insight_box(
            f"{corr_str.capitalize()} positive correlation (r={r_val}) between attendance and grades across {total_students} students.",
            "Students who attend more sessions have more exposure to instruction and active learning.",
            "Make attendance the primary leading KPI. Intervene when a student drops below 70%."
        )
