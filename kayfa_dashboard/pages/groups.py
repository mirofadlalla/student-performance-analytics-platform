import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import load_collection, plotly_layout, insight_box, kpi_card, page_header, section_title

BLUE   = "#636EFA"
RED    = "#EF553B"
GREEN  = "#00CC96"
AMBER  = "#FBD24C"
PURPLE = "#8B5CF6"
CYAN   = "#22D3EE"

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

    total_groups  = len(grp_sum)
    platform_att  = round(grp_sum["att_rate_pct"].mean(), 1) if "att_rate_pct" in grp_sum.columns else 0
    best_att_row  = grp_sum.loc[grp_sum["att_rate_pct"].idxmax()] if "att_rate_pct" in grp_sum.columns else None
    worst_att_row = grp_sum.loc[grp_sum["att_rate_pct"].idxmin()] if "att_rate_pct" in grp_sum.columns else None
    below_avg     = int((grp_sum["att_rate_pct"] < platform_att).sum()) if "att_rate_pct" in grp_sum.columns else 0

    section_title("GROUP ECOSYSTEM OVERVIEW")
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

    # ── Q1 · Attendance per group bar chart (matches notebook) ────────────────
    section_title("Q1 · ATTENDANCE RATE PER GROUP")
    st.markdown('<div class="chart-card"><h3>📊 Which groups sit well below the platform average?</h3>', unsafe_allow_html=True)

    if "att_rate_pct" in grp_sum.columns and "group_id" in grp_sum.columns:
        gb = grp_sum.sort_values("att_rate_pct", ascending=False).copy()
        # Notebook uses simple bar — no color differentiation beyond plotly default
        fig = px.bar(
            gb, x="group_id", y="att_rate_pct",
            title="Attendance Rate per Group (%)",
            labels={"group_id": "Group", "att_rate_pct": "Attendance Rate (%)"},
            text=gb["att_rate_pct"].round(1).astype(str) + "%",
            color="att_rate_pct",
            color_continuous_scale=["#EF553B", "#FBD24C", "#636EFA"],
        )
        fig.add_hline(
            y=platform_att, line_dash="dash", line_color=AMBER, line_width=1.5,
            annotation_text=f"Platform avg: {platform_att:.1f}%",
            annotation_font_color=AMBER,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False, yaxis_range=[0, 100])
        fig = plotly_layout(fig, height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "G07 (60.2%) and G10 (65.4%) are the two groups sitting well below the platform average of 77.3%. G07 is 17 points below the mean — the most concerning gap on the platform.",
        "G07 likely has a scheduling problem, instructor engagement issue, or a course that is too difficult without sufficient support. G10's low attendance may simply be because it only has 1 student — a structural problem, not a behavior problem.",
        "Audit G07's session time and day immediately. Run a 5-minute student survey to identify the barrier. For G10, consider merging the single student into another group (see Q13 below)."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q12 · Stated vs Actual headcount (matches notebook grouped bar) ───────
    section_title("Q12 · STATED vs ACTUAL GROUP SIZES")
    st.markdown('<div class="chart-card"><h3>📋 Self-reported counts vs real student counts — where are the gaps?</h3>', unsafe_allow_html=True)

    if "stated_num_students" in grp_sum.columns and "actual_count" in grp_sum.columns and "group_id" in grp_sum.columns:
        q12 = grp_sum[["group_id", "stated_num_students", "actual_count"]].copy()
        q12["discrepancy"] = q12["stated_num_students"] - q12["actual_count"]
        q12 = q12.sort_values("discrepancy", ascending=False)

        # Notebook uses grouped bar: lightblue for stated, #636EFA for actual
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=q12["group_id"], y=q12["stated_num_students"],
            name="Stated Count", marker_color="lightblue",
        ))
        fig.add_trace(go.Bar(
            x=q12["group_id"], y=q12["actual_count"],
            name="Actual Count", marker_color=BLUE,
        ))
        fig.update_layout(
            barmode="group",
            title="Stated vs Actual Group Sizes",
            xaxis_title="Group",
            yaxis_title="Number of Students",
        )
        fig = plotly_layout(fig, height=380)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Show flagged groups table
        flagged = q12[q12["discrepancy"].abs() > 5]
        if not flagged.empty:
            st.markdown("**Groups to investigate (discrepancy > 5 students):**")
            st.dataframe(
                flagged.rename(columns={
                    "group_id": "Group",
                    "stated_num_students": "Stated",
                    "actual_count": "Actual",
                    "discrepancy": "Gap",
                }),
                use_container_width=True, hide_index=True, height=180,
            )

    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "G10 and G05 both have a ~30-student deficit between what was recorded and the actual enrollment. G10 is listed for 31 students but only has 1.",
        "The groups table uses self-reported headcounts that were never synced with the actual student enrollment records. This is a data pipeline gap — the two systems (group management and student enrollment) are not connected.",
        "Set up an automated nightly sync that overwrites stated_num_students with the real count from students.csv. Flag any group where the discrepancy is greater than 5 students for a manual audit."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q13 · Non-viable group ────────────────────────────────────────────────
    section_title("Q13 · NON-VIABLE GROUP ANALYSIS")
    st.markdown('<div class="chart-card"><h3>⚠️ G10 — 1 student group · What should happen?</h3>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);
                    border-radius:10px;padding:16px;margin-top:8px;">
          <div style="font-size:0.75rem;color:#F87171;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">Non-Viable Group Identified</div>
          <div style="font-size:2rem;font-weight:800;color:#F87171;">G10</div>
          <div style="font-size:0.85rem;color:#CBD5E1;margin-top:4px;">Course: C007 · Cybersecurity Essentials</div>
          <div style="font-size:0.85rem;color:#CBD5E1;">Students: <strong style="color:#F87171;">1</strong> (Adel AbdelHamid)</div>
          <div style="font-size:0.85rem;color:#CBD5E1;margin-top:8px;">A group of 1 cannot function — no peer learning, no group dynamics, and the instructor is teaching a session for a single student.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.25);
                    border-radius:10px;padding:16px;margin-top:8px;">
          <div style="font-size:0.75rem;color:#FBD24C;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">Finding & Recommendation</div>
          <div style="font-size:0.9rem;color:#CBD5E1;line-height:1.6;">
            No other group currently runs C007, so a direct same-course merge is not possible.<br><br>
            Adel's concept profile shows strength in C006 foundational skills (Database Design).<br><br>
            <strong style="color:#FBD24C;">Recommended action:</strong> Transition Adel to G08 or G09 (both offer related courses) with a custom catch-up plan. Alternatively, create a self-paced C007 path for individual students.
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "G10 has only 1 enrolled student (Adel AbdelHamid) despite being listed for 31 students. No other group runs the same course (C007 Cybersecurity Essentials), so a direct merge is not possible.",
        "This is a data integrity + operational failure. The group was created, a course was assigned, but students were never properly enrolled. The instructor has been running sessions for a single student.",
        "Close G10 as an active group. Move Adel to G08 or G09 with a custom learning path. Audit all groups with fewer than 5 students every semester to catch this earlier."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q15 grade trends (already shown in Overview — link here) ─────────────
    section_title("Q15 · GRADE TRENDS BY GROUP")
    st.markdown('<div class="chart-card"><h3>📈 Monthly Average Grade per Group</h3>', unsafe_allow_html=True)

    if not grade_tr.empty and "month" in grade_tr.columns:
        fig = px.line(
            grade_tr.sort_values("month"),
            x="month", y="avg_score", color="true_group",
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
        "G07 stayed below the 60-point pass threshold for almost the entire term. G08 improved the most (+1.76 pts). G10, GZZ, and G77 showed the sharpest declines (-7 to -10 pts).",
        "G07's issue is structural — low attendance leads to low grades, and neither is improving. G10/GZZ/G77 have 1-3 students, so a single poor exam result moves their group average significantly.",
        "Treat G07 as a priority intervention group. For GZZ and G77, merge or close before the next cohort — small groups produce unreliable metrics and waste instructor resources."
    )
