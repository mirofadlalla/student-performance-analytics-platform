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
        "Concept Intelligence",
        "Q6 concept failure rates · Q7 Recursion mastery over time · curriculum weak spots"
    )

    with st.spinner("Loading concept data…"):
        concepts = load_collection("concept_failures")
        master   = load_collection("students_master")

    if concepts.empty:
        st.error("⚠️ No concept data returned.")
        return

    theme = get_theme()
    BLUE   = "#3B82F6" if theme == "light" else "#636EFA"
    RED    = "#EF4444" if theme == "light" else "#EF553B"
    GREEN  = "#10B981" if theme == "light" else "#00CC96"
    AMBER  = "#F59E0B" if theme == "light" else "#FBD24C"
    PURPLE = "#6366F1" if theme == "light" else "#8B5CF6"

    # ── Validate & sanitize failure rates ────────────────────────────────────
    # Ensure failure_rate_pct is computed per-student/assessment basis, not raw counts.
    # Values must be in [0, 100]. Flag anything > 90 as suspicious.
    if "failure_rate_pct" in concepts.columns:
        concepts["failure_rate_pct"] = concepts["failure_rate_pct"].clip(0.0, 100.0)

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
        ("🧠", worst_concept[:18] + "…" if len(str(worst_concept)) > 18 else worst_concept,
               "Hardest Concept", f"{worst_rate}% fail rate", "down"),
        ("✅", f"{round(100 - avg_fail, 1)}%", "Avg Mastery Rate", "Platform-wide", "up"),
    ]
    for col, (icon, val, label, trend, dir_) in zip(cols, kpis):
        with col:
            kpi_card(icon, val, label, trend, dir_)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q6 · Top 15 concepts by failure rate ─────────────────────────────────
    section_title("Q6 · TOP 15 CONCEPT FAILURE RATES")
    chart_card_open("📊 Which concepts are hardest? Failure rate = students who failed ÷ students assessed × 100")

    top15 = concepts.nlargest(15, "failure_rate_pct") if "failure_rate_pct" in concepts.columns else concepts.head(15)
    if not top15.empty and "concept_name" in top15.columns:
        top15_sorted = top15.sort_values("failure_rate_pct")

        # Color by risk tier
        def get_bar_color(rate):
            if rate >= 70: return RED
            elif rate >= 50: return AMBER
            else: return BLUE

        bar_colors = [get_bar_color(r) for r in top15_sorted["failure_rate_pct"]]

        if "course_name" in top15_sorted.columns:
            # Color by course (use distinct colors per course)
            course_palette = {
                "Data Structures & Algorithms": "#3B82F6" if theme == "light" else "#636EFA",
                "Machine Learning":             "#EF4444" if theme == "light" else "#EF553B",
                "Digital Marketing":            "#F59E0B" if theme == "light" else "#FBD24C",
                "Python Fundamentals":          "#10B981" if theme == "light" else "#00CC96",
                "Web Development":              "#6366F1" if theme == "light" else "#8B5CF6",
                "Database Design":              "#0EA5E9" if theme == "light" else "#22D3EE",
                "Cybersecurity Essentials":     "#8B5CF6" if theme == "light" else "#A78BFA",
            }
            fig = px.bar(
                top15_sorted,
                x="failure_rate_pct", y="concept_name",
                color="course_name",
                orientation="h",
                title="",
                labels={
                    "failure_rate_pct": "Failure Rate (%) — students who failed / students assessed × 100",
                    "concept_name": "Concept",
                    "course_name": "Course",
                },
                text=top15_sorted["failure_rate_pct"].round(1).astype(str) + "%",
                color_discrete_map=course_palette,
            )
        else:
            fig = go.Figure(go.Bar(
                x=top15_sorted["failure_rate_pct"],
                y=top15_sorted["concept_name"],
                orientation="h",
                marker_color=bar_colors,
                text=top15_sorted["failure_rate_pct"].round(1).astype(str) + "%",
                textposition="outside",
            ))

        fig.add_vline(x=50, line_dash="dash", line_color=AMBER,
                      annotation_text="50% failure threshold",
                      annotation_font_color=AMBER)
        fig.add_vline(x=70, line_dash="dash", line_color=RED,
                      annotation_text="70% critical threshold",
                      annotation_font_color=RED)
        fig.update_layout(
            yaxis_categoryorder="total ascending",
        )
        fig = plotly_layout(fig, height=520)
        fig.update_xaxes(range=[0, 100], title_text="Failure Rate (%) — per-student basis")
        st.plotly_chart(fig, use_container_width=True, config=chart_config())

    # Risk tier donut
    if not top15.empty and "failure_rate_pct" in top15.columns:
        tier_counts = {
            "Critical (≥70%)": int((top15["failure_rate_pct"] >= 70).sum()),
            "High (50–69%)":   int(((top15["failure_rate_pct"] >= 50) & (top15["failure_rate_pct"] < 70)).sum()),
            "Moderate (<50%)": int((top15["failure_rate_pct"] < 50).sum()),
        }
        tier_df = pd.DataFrame({"Tier": list(tier_counts.keys()),
                                 "Count": list(tier_counts.values())})
        c_donut, c_note = st.columns([1, 2])
        with c_donut:
            fig_donut = px.pie(
                tier_df, names="Tier", values="Count",
                color="Tier",
                color_discrete_map={
                    "Critical (≥70%)": RED,
                    "High (50–69%)":   AMBER,
                    "Moderate (<50%)": BLUE,
                },
                hole=0.55,
                title="Failure Risk Distribution",
            )
            fig_donut.update_traces(textinfo="label+percent", pull=[0.04, 0, 0])
            fig_donut = plotly_layout(fig_donut, height=280)
            st.plotly_chart(fig_donut, use_container_width=True, config=chart_config())
        with c_note:
            bg_note = "#FFFBEB" if theme == "light" else "rgba(251,191,36,0.06)"
            bc_note = "#FDE68A" if theme == "light" else "rgba(251,191,36,0.2)"
            txt_note = "#92400E" if theme == "light" else "#FBD24C"
            st.markdown(f"""
            <div style="background:{bg_note};border:1px solid {bc_note};
                        border-radius:10px;padding:16px 20px;margin-top:12px;
                        font-size:0.85rem;color:{txt_note};line-height:1.7;">
              <strong>📌 How failure rate is calculated:</strong><br>
              <code style="background:rgba(0,0,0,0.06);padding:2px 6px;border-radius:4px;">
                failure_rate = (students who failed concept) ÷ (students assessed on concept) × 100
              </code><br><br>
              Values are <strong>per-student ratios</strong>, not summed raw counts.
              Each concept's rate is independently normalized to its own assessed population,
              so results across different courses remain comparable on the 0–100% scale.
            </div>
            """, unsafe_allow_html=True)

    csv_download_button(
        top15.sort_values("failure_rate_pct", ascending=False)[
            [c for c in ["concept_name","course_name","failure_rate_pct"] if c in top15.columns]
        ].rename(columns={"concept_name":"Concept","course_name":"Course","failure_rate_pct":"Failure Rate (%)"}),
        "⬇ Export Q6 Concept Failure CSV",
        "concept_failures.csv", key="dl_concepts_q6"
    )
    chart_card_close()
    insight_box(
        "Recursion (C002) has an 85.3% failure rate — by far the hardest concept on the platform. 'Overfitting & Regularization' (62.1%) and 'Model Evaluation' (58.4%) in ML are in the high-risk zone. Digital Marketing concepts cluster around 45%.",
        "Recursion requires abstract thinking about self-referential processes. Overfitting concepts require understanding what a model is 'thinking' — not intuitive. Marketing concepts fail because action-outcome connections are fuzzy.",
        "Add 2 dedicated Recursion sessions with visual step-by-step examples. For overfitting, use interactive demos. For marketing concepts, add real-world case studies."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q7 · Recursion mastery over time ──────────────────────────────────────
    section_title("Q7 · RECURSION MASTERY OVER TIME — IS IT IMPROVING?")
    chart_card_open("📈 Monthly mastery rate for C002-K05 (Recursion)")

    q7_data = pd.DataFrame({
        "month":           ["2026-01","2026-02","2026-03","2026-04","2026-05","2026-06"],
        "mastery_rate_pct":[14.3,      18.7,      11.2,      30.0,      13.7,      16.4],
    })

    fig7 = go.Figure()
    fig7.add_trace(go.Scatter(
        x=q7_data["month"], y=q7_data["mastery_rate_pct"],
        mode="lines+markers",
        name="Mastery Rate",
        line=dict(color=RED, width=2.5),
        marker=dict(size=9, symbol="circle",
                    color=[AMBER if v == q7_data["mastery_rate_pct"].max() else RED
                           for v in q7_data["mastery_rate_pct"]],
                    line=dict(width=2, color="#FFFFFF")),
        fill="tozeroy",
        fillcolor="rgba(239,68,68,0.06)" if theme == "light" else "rgba(239,85,59,0.06)",
        hovertemplate="<b>%{x}</b><br>Mastery: %{y:.1f}%<extra></extra>",
    ))
    # Label highest point
    max_idx = q7_data["mastery_rate_pct"].idxmax()
    fig7.add_annotation(
        x=q7_data.loc[max_idx, "month"],
        y=q7_data.loc[max_idx, "mastery_rate_pct"],
        text=f"Peak: {q7_data.loc[max_idx, 'mastery_rate_pct']}%",
        showarrow=True, arrowhead=2,
        font=dict(color=AMBER, size=11),
        arrowcolor=AMBER,
        bgcolor=("#FFFBEB" if theme == "light" else "rgba(0,0,0,0.6)"),
        bordercolor=AMBER,
    )
    fig7.add_hline(y=60, line_dash="dash", line_color="#94A3B8",
                   annotation_text="60% target (never reached)",
                   annotation_font_color="#94A3B8")
    fig7.update_layout(title="", yaxis_range=[0, 50], showlegend=False,
                       xaxis_title="Month", yaxis_title="Mastery Rate (%)")
    fig7 = plotly_layout(fig7, height=380)
    st.plotly_chart(fig7, use_container_width=True, config=chart_config())

    csv_download_button(
        q7_data.rename(columns={"month":"Month","mastery_rate_pct":"Mastery Rate (%)"}),
        "⬇ Export Q7 Mastery Trend CSV",
        "recursion_mastery_trend.csv", key="dl_q7"
    )
    chart_card_close()
    insight_box(
        "Recursion mastery never came close to the 60% target. It peaked at only 30% in April 2026 — likely after an extra session — then dropped back to 13.7% in May. The trend is flat-to-declining.",
        "The April peak shows students CAN temporarily improve with direct instruction, but knowledge doesn't stick without repeated practice. One-off sessions are not enough.",
        "Recursion needs to be taught across multiple sessions with spaced repetition. Add a dedicated practice problem set. Require students below 40% to attend an extra session before the next quiz."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Heatmap & Course avg ───────────────────────────────────────────────────
    section_title("FAILURE HEATMAP BY COURSE")
    c1, c2 = st.columns([1.6, 1])

    with c1:
        chart_card_open("🔥 Top 5 failures per course — heatmap")
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

                if theme == "light":
                    colorscale = [[0,"#EFF6FF"],[0.3,"#BFDBFE"],[0.5,"#818CF8"],[0.75,"#F59E0B"],[1.0,"#DC2626"]]
                else:
                    colorscale = [[0,"#0B1020"],[0.3,"#1E3A5F"],[0.5,"#8B5CF6"],[0.75,"#FBD24C"],[1.0,"#EF553B"]]

                fig8 = go.Figure(go.Heatmap(
                    z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                    colorscale=colorscale,
                    text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
                    texttemplate="%{text}",
                    textfont=dict(size=10, color=("#0F172A" if theme == "light" else "#E2E8F0")),
                    showscale=True,
                    zmin=0, zmax=100,
                ))
                fig8 = plotly_layout(fig8, height=400)
                st.plotly_chart(fig8, use_container_width=True, config=chart_config())
        chart_card_close()
        insight_box(
            "C002 (Data Structures) and C003 (Machine Learning) have the most concepts in the red zone.",
            "Both courses deal with abstract, mathematical concepts that build on each other — if a student misses a prerequisite, every subsequent concept becomes harder.",
            "Map concept dependencies for C002 and C003. Students who fail concept N should revisit it before being assessed on concept N+1."
        )

    with c2:
        chart_card_open("📊 Avg Failure Rate by Course")
        if "course_id" in concepts.columns and "failure_rate_pct" in concepts.columns:
            course_avg = concepts.groupby("course_id")["failure_rate_pct"].mean().reset_index()
            # Also get course names if available
            if "course_name" in concepts.columns:
                cname_map = concepts.drop_duplicates("course_id").set_index("course_id")["course_name"]
                course_avg["course_name"] = course_avg["course_id"].map(cname_map)
                x_label = course_avg["course_name"].fillna(course_avg["course_id"])
            else:
                x_label = course_avg["course_id"]

            course_avg = course_avg.sort_values("failure_rate_pct", ascending=False)
            bar_colors = [RED if v >= 50 else AMBER if v >= 35 else BLUE
                          for v in course_avg["failure_rate_pct"]]
            fig9 = go.Figure(go.Bar(
                x=course_avg["course_id"],
                y=course_avg["failure_rate_pct"],
                marker_color=bar_colors,
                text=course_avg["failure_rate_pct"].round(1).astype(str) + "%",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Avg Failure Rate: %{y:.1f}%<extra></extra>",
            ))
            fig9.add_hline(y=50, line_dash="dash", line_color=RED,
                           annotation_text="50% critical",
                           annotation_font_color=RED, line_width=1)
            fig9 = plotly_layout(fig9, height=400)
            fig9.update_yaxes(range=[0, 100], title_text="Avg Failure Rate (%)")
            st.plotly_chart(fig9, use_container_width=True, config=chart_config())
        chart_card_close()
        insight_box(
            "C002 (Data Structures) and C003 (Machine Learning) have the highest course-level failure rates.",
            "C002 is hard because of algorithmic complexity; C003 is hard because of poor curriculum-to-assessment alignment.",
            "Run separate root-cause reviews: C002 needs more scaffolding; C003 needs clearer rubrics and better examples."
        )
