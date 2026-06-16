import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import (load_collection, plotly_layout, insight_box, kpi_card,
                page_header, section_title, chart_config, csv_download_button,
                chart_card_open, chart_card_close, get_theme)

def render():
    page_header(
        "Group Performance",
        "Q1 attendance per group · Q12 headcount discrepancy · Q13 non-viable group · Q15 grade trends"
    )

    with st.spinner("Loading group data…"):
        grp_sum  = load_collection("group_summaries")
        grade_tr = load_collection("grade_trends")
        master   = load_collection("students_master")

    if grp_sum.empty:
        st.error("⚠️ No group data returned.")
        return

    theme = get_theme()
    BLUE   = "#3B82F6" if theme == "light" else "#636EFA"
    RED    = "#EF4444" if theme == "light" else "#EF553B"
    GREEN  = "#10B981" if theme == "light" else "#00CC96"
    AMBER  = "#F59E0B" if theme == "light" else "#FBD24C"
    PURPLE = "#6366F1" if theme == "light" else "#8B5CF6"

    total_groups  = len(grp_sum)
    platform_att  = round(grp_sum["att_rate_pct"].mean(), 1) if "att_rate_pct" in grp_sum.columns else 0
    best_att_row  = grp_sum.loc[grp_sum["att_rate_pct"].idxmax()] if "att_rate_pct" in grp_sum.columns else None
    worst_att_row = grp_sum.loc[grp_sum["att_rate_pct"].idxmin()] if "att_rate_pct" in grp_sum.columns else None
    below_avg     = int((grp_sum["att_rate_pct"] < platform_att).sum()) if "att_rate_pct" in grp_sum.columns else 0

    section_title("GROUP ECOSYSTEM OVERVIEW")
    cols = st.columns(5)
    kpis = [
        ("🏫", str(total_groups), "Active Groups", "Production cohort", "neutral"),
        ("🥇", best_att_row["group_id"] if best_att_row is not None else "N/A", "Best Attendance",
         f"{best_att_row['att_rate_pct']:.1f}% rate" if best_att_row is not None else "", "up"),
        ("🔴", worst_att_row["group_id"] if worst_att_row is not None else "N/A", "Lowest Attendance",
         f"{worst_att_row['att_rate_pct']:.1f}% rate" if worst_att_row is not None else "", "down"),
        ("📉", str(below_avg), "Groups Below Avg", "Att. < platform mean", "down"),
        ("📊", f"{platform_att}%", "Platform Avg Att.", "All groups", "neutral"),
    ]
    for col, (icon, val, label, trend, dir_) in zip(cols, kpis):
        with col:
            kpi_card(icon, val, label, trend, dir_)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q1 · Attendance per group ─────────────────────────────────────────────
    section_title("Q1 · ATTENDANCE RATE PER GROUP")
    chart_card_open("📊 Which groups sit well below the platform average?")

    if "att_rate_pct" in grp_sum.columns and "group_id" in grp_sum.columns:
        gb = grp_sum.sort_values("att_rate_pct", ascending=False).copy()
        bar_colors = [RED if v < 65 else AMBER if v < platform_att else GREEN
                      for v in gb["att_rate_pct"]]
        fig = go.Figure(go.Bar(
            x=gb["group_id"],
            y=gb["att_rate_pct"],
            marker_color=bar_colors,
            text=gb["att_rate_pct"].round(1).astype(str) + "%",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Attendance: %{y:.1f}%<extra></extra>",
        ))
        fig.add_hline(
            y=platform_att, line_dash="dash", line_color=AMBER, line_width=1.5,
            annotation_text=f"Platform avg: {platform_att:.1f}%",
            annotation_font_color=AMBER,
        )
        fig.update_layout(title="", xaxis_title="Group", yaxis_title="Attendance Rate (%)",
                          yaxis_range=[0, 105], showlegend=False)
        fig = plotly_layout(fig, height=400)
        st.plotly_chart(fig, use_container_width=True, config=chart_config())
        csv_download_button(
            gb[["group_id","course_name","instructor","att_rate_pct"]].rename(columns={
                "group_id":"Group","course_name":"Course",
                "instructor":"Instructor","att_rate_pct":"Attendance Rate (%)"}),
            "⬇ Export Group Attendance CSV", "group_attendance.csv", key="dl_grp_att"
        )

    chart_card_close()
    insight_box(
        "G07 (60.2%) and G10 (65.4%) are the two groups sitting well below the platform average of 77.3%. G07 is 17 points below the mean — the most concerning gap.",
        "G07 likely has a scheduling problem, instructor engagement issue, or a course that is too difficult. G10's low attendance may simply be because it only has 1 student.",
        "Audit G07's session time and day immediately. Run a 5-minute student survey to identify the barrier. For G10, consider merging the single student into another group."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q12 · Stated vs Actual headcount ─────────────────────────────────────
    section_title("Q12 · STATED vs ACTUAL GROUP SIZES")
    chart_card_open("📋 Self-reported counts vs real student counts — where are the gaps?")

    if "stated_num_students" in grp_sum.columns and "actual_count" in grp_sum.columns:
        q12 = grp_sum[["group_id","stated_num_students","actual_count"]].copy()
        q12["discrepancy"] = q12["stated_num_students"] - q12["actual_count"]
        q12 = q12.sort_values("discrepancy", ascending=False)

        # Grouped bar — stated vs actual
        c_left, c_right = st.columns([1.6, 1])

        with c_left:
            fig_grouped = go.Figure()
            fig_grouped.add_trace(go.Bar(
                x=q12["group_id"], y=q12["stated_num_students"],
                name="Stated Count",
                marker_color="rgba(59, 130, 246, 0.4)" if theme == "light" else "rgba(99, 110, 250, 0.4)",
                text=q12["stated_num_students"],
                textposition="outside",
            ))
            fig_grouped.add_trace(go.Bar(
                x=q12["group_id"], y=q12["actual_count"],
                name="Actual Count",
                marker_color=BLUE,
                text=q12["actual_count"],
                textposition="outside",
            ))
            fig_grouped.update_layout(
                barmode="group",
                title="",
                xaxis_title="Group",
                yaxis_title="Number of Students",
                showlegend=True,
            )
            fig_grouped = plotly_layout(fig_grouped, height=400)
            st.plotly_chart(fig_grouped, use_container_width=True, config=chart_config())

        with c_right:
            # Diverging bar chart for discrepancy
            disc_colors = [RED if v > 5 else AMBER if v > 0 else GREEN
                           for v in q12["discrepancy"]]
            fig_disc = go.Figure(go.Bar(
                x=q12["discrepancy"],
                y=q12["group_id"],
                orientation="h",
                marker_color=disc_colors,
                text=q12["discrepancy"].apply(lambda x: f"+{x}" if x > 0 else str(x)),
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Gap: %{x} students<extra></extra>",
            ))
            fig_disc.add_vline(x=0, line_color=("#94A3B8" if theme == "light" else "#64748B"),
                               line_width=1)
            fig_disc.add_vline(x=5, line_dash="dot", line_color=AMBER,
                               annotation_text="Threshold (+5)",
                               annotation_font_color=AMBER)
            fig_disc.update_layout(
                title="Discrepancy: Stated − Actual",
                xaxis_title="Gap (students)",
                yaxis_title="",
                yaxis_categoryorder="total ascending",
            )
            fig_disc = plotly_layout(fig_disc, height=400)
            st.plotly_chart(fig_disc, use_container_width=True, config=chart_config())

        csv_download_button(
            q12.rename(columns={"group_id":"Group","stated_num_students":"Stated",
                                 "actual_count":"Actual","discrepancy":"Gap (Stated−Actual)"}),
            "⬇ Export Headcount Discrepancy CSV",
            "headcount_discrepancy.csv", key="dl_headcount"
        )

    chart_card_close()
    insight_box(
        "G10 and G05 both have a ~30-student deficit between what was recorded and the actual enrollment. G10 is listed for 31 students but only has 1.",
        "The groups table uses self-reported headcounts that were never synced with the actual student enrollment records — the two systems are not connected.",
        "Set up an automated nightly sync that overwrites stated_num_students with the real count. Flag any group where the discrepancy is greater than 5 students for a manual audit."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q13 · Non-viable group ────────────────────────────────────────────────
    section_title("Q13 · NON-VIABLE GROUP ANALYSIS")
    chart_card_open("⚠️ G10 — 1 student group · What should happen?")

    col1, col2 = st.columns(2)
    border_red  = "#FCA5A5" if theme == "light" else "rgba(248,113,113,0.25)"
    border_amb  = "#FDE68A" if theme == "light" else "rgba(251,191,36,0.25)"
    bg_red      = "rgba(239,68,68,0.06)" if theme == "light" else "rgba(248,113,113,0.08)"
    bg_amb      = "rgba(245,158,11,0.06)" if theme == "light" else "rgba(251,191,36,0.08)"
    txt_red     = "#DC2626" if theme == "light" else "#F87171"
    txt_amb     = "#CA8A04" if theme == "light" else "#FBD24C"
    txt_body    = "#334155" if theme == "light" else "#CBD5E1"

    with col1:
        st.markdown(f"""
        <div style="background:{bg_red};border:1px solid {border_red};
                    border-radius:12px;padding:20px;margin-top:8px;">
          <div style="font-size:0.75rem;color:{txt_red};font-weight:700;
                      text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">Non-Viable Group Identified</div>
          <div style="font-size:2.5rem;font-weight:800;color:{txt_red};">G10</div>
          <div style="font-size:0.85rem;color:{txt_body};margin-top:4px;">Course: C007 · Cybersecurity Essentials</div>
          <div style="font-size:0.85rem;color:{txt_body};">Students: <strong style="color:{txt_red};">1</strong> (Adel AbdelHamid)</div>
          <div style="font-size:0.85rem;color:{txt_body};margin-top:10px;">A group of 1 cannot function — no peer learning, no group dynamics, and the instructor is teaching a session for a single student.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:{bg_amb};border:1px solid {border_amb};
                    border-radius:12px;padding:20px;margin-top:8px;">
          <div style="font-size:0.75rem;color:{txt_amb};font-weight:700;
                      text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">Finding & Recommendation</div>
          <div style="font-size:0.9rem;color:{txt_body};line-height:1.7;">
            No other group currently runs C007, so a direct same-course merge is not possible.<br><br>
            Adel's concept profile shows strength in C006 foundational skills (Database Design).<br><br>
            <strong style="color:{txt_amb};">Recommended action:</strong> Transition Adel to G08 or G09 with a custom catch-up plan. Alternatively, create a self-paced C007 path for individual students.
          </div>
        </div>
        """, unsafe_allow_html=True)

    chart_card_close()
    insight_box(
        "G10 has only 1 enrolled student (Adel AbdelHamid) despite being listed for 31 students. No other group runs the same course (C007).",
        "This is a data integrity + operational failure. The group was created, a course was assigned, but students were never properly enrolled.",
        "Close G10 as an active group. Move Adel to G08 or G09 with a custom learning path. Audit all groups with fewer than 5 students every semester."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q15 · Grade trends ─────────────────────────────────────────────────────
    section_title("Q15 · GRADE TRENDS BY GROUP")
    chart_card_open("📈 Monthly Average Grade per Group")

    if not grade_tr.empty and "month" in grade_tr.columns:
        color_seq = (px.colors.qualitative.Plotly if theme == "dark"
                     else px.colors.qualitative.Safe)
        fig = px.line(
            grade_tr.sort_values("month"),
            x="month", y="avg_score", color="true_group",
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
        csv_download_button(grade_tr, "⬇ Export Grade Trends CSV",
                            "grade_trends_groups.csv", key="dl_grade_grp")

    chart_card_close()
    insight_box(
        "G07 stayed below the 60-point pass threshold for almost the entire term. G08 improved the most (+1.76 pts). G10, GZZ, and G77 showed the sharpest declines.",
        "G07's issue is structural — low attendance leads to low grades, and neither is improving. G10/GZZ/G77 have 1-3 students, so a single poor exam result moves the group average significantly.",
        "Treat G07 as a priority intervention group. For GZZ and G77, merge or close before the next cohort."
    )
