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
        "Concept Intelligence",
        "Q6 concept failure rates · Q7 Recursion mastery over time · curriculum weak spots"
    )

    with st.spinner("Loading concept data…"):
        concepts = load_collection("concept_failures")
        master   = load_collection("students_master")

    if concepts.empty:
        st.error("⚠️ No concept data returned.")
        return

    total_concepts = len(concepts)
    avg_fail    = round(concepts["failure_rate_pct"].mean(), 1) if "failure_rate_pct" in concepts.columns else 0
    critical    = int((concepts["failure_rate_pct"] >= 50).sum()) if "failure_rate_pct" in concepts.columns else 0
    worst_concept = concepts.loc[concepts["failure_rate_pct"].idxmax(), "concept_name"] if "concept_name" in concepts.columns else "N/A"
    worst_rate  = round(concepts["failure_rate_pct"].max(), 1) if "failure_rate_pct" in concepts.columns else 0

    section_title("CONCEPT MASTERY OVERVIEW")
    cols = st.columns(5)
    kpis = [
        ("📚", str(total_concepts), "Total Concepts",   "Across all courses", "neutral"),
        ("❌", f"{avg_fail}%",      "Avg Failure Rate", "Platform-wide",      "down"),
        ("🔴", str(critical),       "Critical Concepts","Failure rate ≥ 50%", "down"),
        ("🧠", worst_concept[:18] + "…" if len(str(worst_concept)) > 18 else worst_concept, "Hardest Concept", f"{worst_rate}% fail rate", "down"),
        ("✅", f"{round(100 - avg_fail, 1)}%", "Avg Mastery Rate", "Platform-wide", "up"),
    ]
    for col, (icon, val, label, trend, dir_) in zip(cols, kpis):
        with col:
            kpi_card(icon, val, label, trend, dir_)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q6 · Top 15 concepts by failure rate — HORIZONTAL BAR colored by course ──
    section_title("Q6 · TOP 15 CONCEPT FAILURE RATES")
    st.markdown('<div class="chart-card"><h3>📊 Which concepts are hardest? Which course is the biggest weak spot?</h3>', unsafe_allow_html=True)

    top15 = concepts.nlargest(15, "failure_rate_pct") if "failure_rate_pct" in concepts.columns else concepts.head(15)
    if not top15.empty and "concept_name" in top15.columns:
        top15_sorted = top15.sort_values("failure_rate_pct")

        # Notebook uses px.bar with color=course_name — match this
        if "course_name" in top15_sorted.columns:
            fig = px.bar(
                top15_sorted,
                x="failure_rate_pct", y="concept_name",
                color="course_name",
                orientation="h",
                title="Top 15 Concepts by Failure Rate",
                labels={
                    "failure_rate_pct": "Failure Rate (%)",
                    "concept_name": "Concept",
                    "course_name": "Course",
                },
                text=top15_sorted["failure_rate_pct"].round(1).astype(str) + "%",
            )
            fig.update_layout(yaxis_categoryorder="total ascending")
        else:
            # Fallback: single color bars
            fig = go.Figure(go.Bar(
                x=top15_sorted["failure_rate_pct"],
                y=top15_sorted["concept_name"],
                orientation="h",
                marker_color=[RED if r >= 70 else AMBER if r >= 50 else BLUE for r in top15_sorted["failure_rate_pct"]],
                text=top15_sorted["failure_rate_pct"].round(1).astype(str) + "%",
                textposition="outside",
            ))

        fig.add_vline(x=50, line_dash="dash", line_color="gray",
                      annotation_text="50% failure threshold")
        fig = plotly_layout(fig, height=480)
        fig.update_xaxes(range=[0, 100], title_text="Failure Rate (%)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Print table like notebook
    if "concept_name" in top15.columns and "failure_rate_pct" in top15.columns:
        show_cols = [c for c in ["concept_name","course_name","failure_rate_pct"] if c in top15.columns]
        st.dataframe(
            top15.sort_values("failure_rate_pct", ascending=False)[show_cols].rename(columns={
                "concept_name":"Concept","course_name":"Course","failure_rate_pct":"Failure Rate (%)"
            }).round(1),
            use_container_width=True, hide_index=True, height=220,
        )
    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "Recursion (C002) has an 85.3% failure rate — by far the hardest concept on the platform. 'Overfitting & Regularization' and 'Model Evaluation' in Cybersecurity/ML courses show 50–60% failure. Digital Marketing concepts (Funnel Analytics, SEO) cluster around 45%.",
        "Recursion requires abstract thinking about self-referential processes — a genuine cognitive leap that many students hit a wall on. Overfitting concepts are hard because they require understanding what a model is 'thinking', which is not intuitive. Marketing concepts are high-failure because the connection between action and outcome is fuzzy and hard to test.",
        "Add 2 dedicated Recursion sessions with visual, step-by-step examples (draw the call stack on a whiteboard). For overfitting, use interactive demos where students can see a model overfit live. For marketing concepts, add real-world case studies that make the abstract metrics concrete."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q7 · Recursion mastery over time — LINE CHART like notebook ───────────
    section_title("Q7 · RECURSION MASTERY OVER TIME — IS IT IMPROVING?")
    st.markdown('<div class="chart-card"><h3>📈 Monthly mastery rate for C002-K05 (Recursion)</h3>', unsafe_allow_html=True)

    # Notebook data from Q7 output
    q7_data = pd.DataFrame({
        "month":           ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06"],
        "mastery_rate_pct":[14.3,      18.7,      11.2,      30.0,      13.7,      16.4],
    })

    fig7 = px.line(
        q7_data, x="month", y="mastery_rate_pct",
        markers=True,
        title="Monthly Mastery Rate — Recursion (C002-K05)",
        labels={"month": "Month", "mastery_rate_pct": "Mastery Rate (%)"},
        color_discrete_sequence=[RED],
    )
    fig7.add_hline(y=60, line_dash="dash", line_color="gray",
                   annotation_text="60% target")
    fig7.update_layout(yaxis_range=[0, 50])
    fig7 = plotly_layout(fig7, height=360)
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})

    st.dataframe(q7_data.rename(columns={"month":"Month","mastery_rate_pct":"Mastery Rate (%)"}),
                 use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    insight_box(
        "Recursion mastery never came close to the 60% target. It peaked at only 30% in April 2026 — likely after an extra session — then dropped back to 13.7% in May. The trend is flat-to-declining, not improving.",
        "The April peak after a probable extra session shows that students CAN temporarily improve with direct instruction, but the knowledge doesn't stick without repeated practice and reinforcement. One-off sessions are not enough for this concept.",
        "Recursion needs to be taught across multiple sessions with spaced repetition. After the first introduction, bring it back in exercises every 2-3 weeks. Add a dedicated practice problem set. Track mastery at each assessment and require students below 40% to attend an extra session before the next quiz."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Heatmap ────────────────────────────────────────────────────────────────
    section_title("FAILURE HEATMAP BY COURSE")
    c1, c2 = st.columns([1.6, 1])

    with c1:
        st.markdown('<div class="chart-card"><h3>🔥 Top 5 failures per course — heatmap</h3>', unsafe_allow_html=True)
        if "course_id" in concepts.columns and "concept_name" in concepts.columns:
            top_by_course = (
                concepts.sort_values("failure_rate_pct", ascending=False)
                .groupby("course_id").head(5).reset_index(drop=True)
            )
            if not top_by_course.empty:
                pivot = top_by_course.pivot_table(
                    index="concept_name", columns="course_id",
                    values="failure_rate_pct", aggfunc="mean",
                ).fillna(0)
                fig8 = go.Figure(go.Heatmap(
                    z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                    colorscale=[[0,"#0B1020"],[0.3,"#1E3A5F"],[0.5,PURPLE],[0.75,AMBER],[1.0,RED]],
                    text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
                    texttemplate="%{text}", textfont=dict(size=10, color="#E2E8F0"),
                    showscale=True,
                ))
                fig8 = plotly_layout(fig8, height=380)
                st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "C002 (Data Structures) and C003 (Machine Learning) have the most concepts in the red zone.",
            "Both courses deal with abstract, mathematical concepts that build on each other — if a student misses a prerequisite concept, every subsequent one becomes harder.",
            "Map concept dependencies for C002 and C003. Students who fail concept N should be required to revisit it before being assessed on concept N+1."
        )

    with c2:
        st.markdown('<div class="chart-card"><h3>📊 Avg Failure Rate by Course</h3>', unsafe_allow_html=True)
        if "course_id" in concepts.columns and "failure_rate_pct" in concepts.columns:
            course_avg = concepts.groupby("course_id")["failure_rate_pct"].mean().reset_index()
            course_avg = course_avg.sort_values("failure_rate_pct", ascending=False)
            fig9 = go.Figure(go.Bar(
                x=course_avg["course_id"], y=course_avg["failure_rate_pct"],
                marker_color=[RED if v >= 50 else AMBER if v >= 35 else BLUE for v in course_avg["failure_rate_pct"]],
                text=course_avg["failure_rate_pct"].round(1).astype(str) + "%",
                textposition="outside",
            ))
            fig9.add_hline(y=50, line_dash="dash", line_color=RED, line_width=1)
            fig9 = plotly_layout(fig9, height=380)
            fig9.update_yaxes(range=[0, 100], title_text="Avg Failure Rate (%)")
            st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        insight_box(
            "Digital Marketing (C005) and Data Structures (C002) have the highest course-level failure rates.",
            "These two courses have very different root causes — C002 is hard because of complexity, C005 is hard because of poor curriculum-to-assessment alignment.",
            "Run separate root-cause reviews for C002 (needs more scaffolding) and C005 (needs clearer rubrics and better examples)."
        )
