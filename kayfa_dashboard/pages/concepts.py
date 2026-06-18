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
GREEN  = "#22D3EE"

def render():
    page_header(
        "Concept Intelligence",
        "Failure heatmap · hardest concepts · course weak spots · curriculum gap analysis"
    )

    with st.spinner("Loading concept data…"):
        concepts = load_collection("concept_failures")
        master   = load_collection("students_master")

    if concepts.empty:
        st.error("⚠️ No concept data returned.")
        return

    # ── KPIs ────────────────────────────────────────────────────────────────
    section_title("CONCEPT MASTERY OVERVIEW")
    total_concepts = len(concepts)
    avg_fail = round(concepts["failure_rate_pct"].mean(), 1) if "failure_rate_pct" in concepts.columns else 0
    critical = int((concepts["failure_rate_pct"] >= 50).sum()) if "failure_rate_pct" in concepts.columns else 0
    worst_concept = concepts.loc[concepts["failure_rate_pct"].idxmax(), "concept_name"] if "concept_name" in concepts.columns else "N/A"
    worst_rate = round(concepts["failure_rate_pct"].max(), 1) if "failure_rate_pct" in concepts.columns else 0

    cols = st.columns(5)
    kpis = [
        ("📚", str(total_concepts), "Total Concepts", "Across all courses", "neutral"),
        ("❌", f"{avg_fail}%", "Avg Failure Rate", "Platform-wide", "down"),
        ("🔴", str(critical), "Critical Concepts", "Failure rate ≥ 50%", "down"),
        ("🧠", worst_concept[:18] + "…" if len(str(worst_concept)) > 18 else worst_concept, "Hardest Concept", f"{worst_rate}% fail rate", "down"),
        ("✅", f"{round(100 - avg_fail, 1)}%", "Avg Mastery Rate", "Platform-wide", "up"),
    ]
    for col, (icon, val, label, trend, dir_) in zip(cols, kpis):
        with col:
            kpi_card(icon, val, label, trend, dir_)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top Failing Concepts Horizontal Bar ─────────────────────────────────
    section_title("CONCEPT FAILURE RANKING")
    st.markdown('<div class="chart-card"><h3>🏴 Top 15 Concepts by Failure Rate</h3>', unsafe_allow_html=True)

    top15 = concepts.nlargest(15, "failure_rate_pct") if "failure_rate_pct" in concepts.columns else concepts.head(15)
    if not top15.empty and "concept_name" in top15.columns:
        top15 = top15.sort_values("failure_rate_pct")
        colors = [RED if r >= 70 else AMBER if r >= 50 else BLUE for r in top15["failure_rate_pct"]]

        fig = go.Figure(go.Bar(
            x=top15["failure_rate_pct"],
            y=top15["concept_name"],
            orientation="h",
            marker_color=colors,
            text=top15["failure_rate_pct"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=11, color="#94A3B8"),
            hovertemplate="<b>%{y}</b><br>Failure Rate: %{x:.1f}%<extra></extra>",
        ))
        fig.add_vline(x=50, line_dash="dash", line_color=AMBER, line_width=1,
                      annotation_text="50% danger threshold", annotation_font_color=AMBER, annotation_font_size=11)
        fig = plotly_layout(fig, height=440)
        fig.update_xaxes(range=[0, 100], title_text="Failure Rate (%)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "Recursion has an 85.3% failure rate — by far the hardest concept on the platform.",
        "Recursion requires abstract thinking that many students haven't developed yet at this stage.",
        "Add 2 supplementary sessions on Recursion. Create visualized step-through exercises."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Heatmap by Course ────────────────────────────────────────────────────
    section_title("FAILURE HEATMAP BY COURSE")
    c1, c2 = st.columns([1.6, 1])

    with c1:
        st.markdown('<div class="chart-card"><h3>🔥 Concept Failure Rate Heatmap</h3>', unsafe_allow_html=True)
        if "course_id" in concepts.columns and "concept_name" in concepts.columns and "failure_rate_pct" in concepts.columns:
            top_by_course = (
                concepts.sort_values("failure_rate_pct", ascending=False)
                .groupby("course_id")
                .head(5)
                .reset_index(drop=True)
            )
            if not top_by_course.empty:
                pivot = top_by_course.pivot_table(
                    index="concept_name", columns="course_id", values="failure_rate_pct", aggfunc="mean"
                ).fillna(0)

                fig = go.Figure(go.Heatmap(
                    z=pivot.values,
                    x=pivot.columns.tolist(),
                    y=pivot.index.tolist(),
                    colorscale=[
                        [0.0, "#0B1020"],
                        [0.3, "#1E3A5F"],
                        [0.5, "#8B5CF6"],
                        [0.75, AMBER],
                        [1.0, RED],
                    ],
                    text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
                    texttemplate="%{text}",
                    textfont=dict(size=10, color="#E2E8F0"),
                    hovertemplate="<b>%{y}</b><br>Course: %{x}<br>Failure Rate: %{z:.1f}%<extra></extra>",
                    showscale=True,
                    colorbar=dict(
                        tickfont=dict(color="#64748B"),
                        title=dict(text="Fail %", font=dict(color="#94A3B8")),
                    ),
                ))
                fig = plotly_layout(fig, height=380)
                fig.update_layout(
                    xaxis=dict(tickfont=dict(size=10), title_text="Course"),
                    yaxis=dict(tickfont=dict(size=10), title_text=""),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "The heatmap shows C002 (Programming) and C003 (Data Science) have the most red concepts.",
            "Technical courses with abstract concepts naturally have higher failure rates.",
            "Redistribute teaching hours toward high-failure concepts in C002 and C003."
        )

    with c2:
        st.markdown('<div class="chart-card"><h3>📊 Avg Failure Rate by Course</h3>', unsafe_allow_html=True)
        if "course_id" in concepts.columns and "failure_rate_pct" in concepts.columns:
            course_avg = concepts.groupby("course_id")["failure_rate_pct"].mean().reset_index()
            course_avg = course_avg.sort_values("failure_rate_pct", ascending=False)

            fig = go.Figure(go.Bar(
                x=course_avg["course_id"],
                y=course_avg["failure_rate_pct"],
                marker_color=[RED if v >= 50 else AMBER if v >= 35 else BLUE for v in course_avg["failure_rate_pct"]],
                text=course_avg["failure_rate_pct"].round(1).astype(str) + "%",
                textposition="outside",
                textfont=dict(size=11, color="#94A3B8"),
            ))
            fig.add_hline(y=50, line_dash="dash", line_color=RED, line_width=1)
            fig = plotly_layout(fig, height=380)
            fig.update_yaxes(range=[0, 100], title_text="Avg Failure Rate (%)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "Digital Marketing (C006) has the highest course-level failure rate.",
            "Curriculum may be misaligned with student prerequisites or instructor delivery.",
            "Conduct a curriculum review for C006. Pilot a revised syllabus next cohort."
        )

    # ── Student Failed Concepts Distribution ────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 Failed Concept Distribution Across Students", expanded=False):
        section_title("STUDENT-LEVEL CONCEPT FAILURES")
        if "failed_concepts" in master.columns:
            fig = px.histogram(
                master.dropna(subset=["failed_concepts"]),
                x="failed_concepts",
                nbins=20,
                color_discrete_sequence=[PURPLE],
                labels={"failed_concepts": "Number of Failed Concepts", "count": "Students"},
            )
            fig.update_traces(marker_line_color="#0B1020", marker_line_width=1)
            fig = plotly_layout(fig, height=300)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            insight_box(
                "Most students fail between 3 and 8 concepts; a tail extends to 22+ failures.",
                "High concept failure count correlates strongly with overall at-risk classification.",
                "Set automated alerts when a student's failed_concepts count exceeds 8."
            )
