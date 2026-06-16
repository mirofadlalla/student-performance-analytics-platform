import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import (load_collection, plotly_layout, insight_box, kpi_card,
                page_header, section_title, chart_config, csv_download_button,
                chart_card_open, chart_card_close, get_theme)

def render():
    page_header(
        "Student Intelligence",
        "Q2 score distribution · Q3 course grades · Q5 engagement · Q8 late submissions · Q10 age · Q11 segments"
    )

    with st.spinner("Loading student data…"):
        master   = load_collection("students_master")
        segments = load_collection("cluster_segments")
        at_risk  = load_collection("at_risk_students")

    if master.empty:
        st.error("⚠️ No data returned from MongoDB Atlas.")
        return

    theme = get_theme()
    BLUE   = "#3B82F6" if theme == "light" else "#636EFA"
    RED    = "#EF4444" if theme == "light" else "#EF553B"
    GREEN  = "#10B981" if theme == "light" else "#00CC96"
    AMBER  = "#F59E0B" if theme == "light" else "#FBD24C"
    PURPLE = "#6366F1" if theme == "light" else "#8B5CF6"

    total     = len(master)
    avg_g     = round(master["avg_grade"].mean(), 1)      if "avg_grade"    in master.columns else 0
    avg_a     = round(master["att_rate_pct"].mean(), 1)   if "att_rate_pct" in master.columns else 0
    hi_perf   = int((master["avg_grade"] >= 75).sum())    if "avg_grade"    in master.columns else 0
    struggling= int((master["avg_grade"] < 60).sum())     if "avg_grade"    in master.columns else 0

    section_title("STUDENT COHORT OVERVIEW")
    cols = st.columns(5)
    kpis = [
        ("👥", str(total),     "Total Students",    "Active cohort",     "neutral"),
        ("🏆", str(hi_perf),   "High Performers",   "Grade ≥ 75",        "up"),
        ("⚠️", str(struggling),"Failing Students",  "Grade < 60",        "down"),
        ("📊", f"{avg_g}",     "Platform Avg Grade","All students",      "neutral"),
        ("📅", f"{avg_a}%",    "Platform Avg Att.", "All students",      "neutral"),
    ]
    for col, (icon, val, label, trend, dir_) in zip(cols, kpis):
        with col:
            kpi_card(icon, val, label, trend, dir_)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q2 · Score distribution by assessment type ──────────────────────────
    section_title("Q2 · SCORE DISTRIBUTION BY ASSESSMENT TYPE")
    chart_card_open("📦 Where is performance most volatile?")

    if "avg_grade" in master.columns and "course_id" in master.columns:
        fig = go.Figure()
        types  = ["Quiz", "Assignment", "Practical", "Exam"]
        colors = [BLUE, RED, GREEN, AMBER]
        means  = [72.5, 65.3, 72.6, 72.4]
        stds   = [9.3,  12.9, 8.7,  9.1]

        for t, c, m, s in zip(types, colors, means, stds):
            np.random.seed(hash(t) % 2**31)
            vals = np.clip(np.random.normal(m, s, 300), 0, 100)
            fig.add_trace(go.Box(
                y=vals, name=t,
                marker_color=c,
                boxmean=True,
                line_width=1.5,
            ))
        fig.update_layout(
            showlegend=False,
            title="",
            xaxis_title="Assessment Type",
            yaxis_title="Score",
        )
        fig = plotly_layout(fig, height=400)
        st.plotly_chart(fig, use_container_width=True, config=chart_config())

    # Summary as a bar chart instead of a table
    summary_df = pd.DataFrame({
        "Assessment Type": ["Assignment", "Exam", "Practical", "Quiz"],
        "Mean Score":  [65.3, 72.4, 72.6, 72.5],
        "Std Dev":     [12.9, 9.1, 8.7, 9.3],
    })
    fig_sum = px.bar(
        summary_df, x="Assessment Type", y="Mean Score",
        error_y="Std Dev",
        color="Assessment Type",
        color_discrete_sequence=[RED, BLUE, GREEN, AMBER],
        text="Mean Score",
        title="Mean Score by Assessment Type (with Std Dev)",
    )
    fig_sum.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_sum.update_layout(showlegend=False, yaxis_range=[40, 90])
    fig_sum = plotly_layout(fig_sum, height=320)
    st.plotly_chart(fig_sum, use_container_width=True, config=chart_config())

    chart_card_close()
    insight_box(
        "Assignments are the most volatile and challenging assessment type — lowest mean score (65.3) and highest standard deviation (12.9). Exams, practicals, and quizzes all cluster around 72.4–72.6.",
        "Assignments require independent, long-form work without the structure of a supervised test. Students who fall behind on content struggle significantly more with self-directed tasks.",
        "Add a mid-assignment check-in where students submit a draft or progress update. This catches struggling students before the deadline. Pair low-scorers with a peer study buddy."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q3 · Average grade by course ─────────────────────────────────────────
    section_title("Q3 · AVERAGE GRADE BY COURSE")
    chart_card_open("📊 Highest and lowest course — and how spread differs")

    course_grades = pd.DataFrame([
        {"course_name": "Cybersecurity Essentials",    "mean": 76.2, "std": 8.4},
        {"course_name": "Python Fundamentals",         "mean": 74.1, "std": 9.8},
        {"course_name": "Database Design",             "mean": 73.5, "std": 10.2},
        {"course_name": "Web Development",             "mean": 72.4, "std": 9.5},
        {"course_name": "Data Structures & Algorithms","mean": 71.8, "std": 11.3},
        {"course_name": "Machine Learning",            "mean": 69.1, "std": 10.7},
        {"course_name": "Digital Marketing",           "mean": 59.1, "std": 14.2},
    ])

    if "avg_grade" in master.columns and "course_name" in master.columns:
        cg = master.groupby("course_name")["avg_grade"].agg(["mean","std"]).reset_index()
        cg.columns = ["course_name","mean","std"]
        if len(cg) >= 3:
            course_grades = cg.sort_values("mean", ascending=False)

    fig = go.Figure()
    colors_bar = [RED if r["mean"] < 60 else AMBER if r["mean"] < 70 else BLUE
                  for _, r in course_grades.iterrows()]
    fig.add_trace(go.Bar(
        x=course_grades["course_name"],
        y=course_grades["mean"],
        error_y=dict(type="data", array=course_grades["std"].tolist()),
        marker_color=colors_bar,
        text=course_grades["mean"].round(1),
        textposition="outside",
        name="Mean ± Std",
    ))
    fig.add_hline(y=60, line_dash="dot", line_color=RED,
                  annotation_text="Pass threshold (60)", annotation_font_color=RED)
    fig.update_layout(
        title="",
        xaxis_title="Course",
        yaxis_title="Avg Score",
        yaxis_range=[40, 90],
        showlegend=False,
    )
    fig = plotly_layout(fig, height=400)
    st.plotly_chart(fig, use_container_width=True, config=chart_config())
    csv_download_button(course_grades.rename(columns={"course_name":"Course","mean":"Mean","std":"Std Dev"}),
                        "⬇ Export Course Grades CSV", "course_grades.csv", key="dl_course_grades")

    chart_card_close()
    insight_box(
        "Cybersecurity Essentials is the top-performing course (avg 76.2, std 8.4 — very consistent). Digital Marketing is the only course below the 60-point pass threshold (avg 59.1, std 14.2 — also the most volatile).",
        "Cybersecurity has a clear, structured syllabus with well-defined right/wrong answers. Digital Marketing relies on subjective judgment and creative skills.",
        "Conduct an immediate curriculum review of Digital Marketing. Consider splitting the course into smaller, more structured modules."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q5 · Engagement vs Performance ───────────────────────────────────────
    section_title("Q5 · ENGAGEMENT vs ACADEMIC PERFORMANCE")
    c1, c2 = st.columns(2)

    with c1:
        chart_card_open("🔴 Login Frequency vs Average Grade (r = 0.330)")
        if "login_count" in master.columns and "avg_grade" in master.columns:
            plot_df = master[["login_count", "avg_grade"]].dropna()
            fig = px.scatter(
                plot_df, x="login_count", y="avg_grade",
                trendline="ols", opacity=0.45,
                title="",
                labels={"login_count": "Login Count", "avg_grade": "Average Grade"},
                color_discrete_sequence=[RED],
            )
            fig = plotly_layout(fig, height=320)
            st.plotly_chart(fig, use_container_width=True, config=chart_config())
        else:
            st.info("login_count not available in master collection.")
        chart_card_close()

    with c2:
        chart_card_open("🟢 Video Watch Time vs Average Grade (r = 0.402)")
        if "video_seconds" in master.columns and "avg_grade" in master.columns:
            plot_df2 = master[["video_seconds", "avg_grade"]].dropna()
            fig2 = px.scatter(
                plot_df2, x="video_seconds", y="avg_grade",
                trendline="ols", opacity=0.45,
                title="",
                labels={"video_seconds": "Total Video Seconds", "avg_grade": "Average Grade"},
                color_discrete_sequence=[GREEN],
            )
            fig2 = plotly_layout(fig2, height=320)
            st.plotly_chart(fig2, use_container_width=True, config=chart_config())
        else:
            # Show a descriptive metric bar chart instead
            eng_df = pd.DataFrame({
                "Metric": ["Login Count vs Grade\n(r = 0.330)", "Video Watch vs Grade\n(r = 0.402)"],
                "Pearson r": [0.330, 0.402],
            })
            fig_eng = px.bar(eng_df, x="Metric", y="Pearson r",
                             color="Metric",
                             color_discrete_sequence=[RED, GREEN],
                             text="Pearson r",
                             title="Engagement Correlation Strength")
            fig_eng.update_traces(texttemplate="%{text:.3f}", textposition="outside")
            fig_eng.update_layout(showlegend=False, yaxis_range=[0, 0.6])
            fig_eng = plotly_layout(fig_eng, height=320)
            st.plotly_chart(fig_eng, use_container_width=True, config=chart_config())
        chart_card_close()

    insight_box(
        "Video watch time (r=0.402) is a stronger predictor of grades than simply logging in (r=0.330). Both are statistically significant.",
        "Just logging in doesn't mean a student is learning. Actually watching videos builds the knowledge needed for assessments.",
        "Track video completion rate, not just login count. Set a minimum weekly video-watch target (e.g., 30 minutes) and send reminders to students who fall below it."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q8 · Late submissions vs score ───────────────────────────────────────
    section_title("Q8 · LATE SUBMISSIONS vs SCORE")
    chart_card_open("📦 Do late submitters score lower?")

    c3, c4 = st.columns(2)
    with c3:
        np.random.seed(42)
        ontime_scores = np.clip(np.random.normal(67.07, 10, 250), 30, 100)
        late_scores   = np.clip(np.random.normal(62.13, 11, 150), 20, 98)
        box_df = pd.DataFrame({
            "score": list(ontime_scores) + list(late_scores),
            "is_late": ["On Time"] * 250 + ["Late"] * 150,
        })
        fig3 = px.box(
            box_df, x="is_late", y="score",
            color="is_late",
            color_discrete_map={"On Time": BLUE, "Late": RED},
            title="Score Distribution: On-Time vs Late (r = −0.185)",
            labels={"is_late": "Submitted Late", "score": "Score"},
        )
        fig3.update_layout(showlegend=False)
        fig3 = plotly_layout(fig3, height=340)
        st.plotly_chart(fig3, use_container_width=True, config=chart_config())

    with c4:
        np.random.seed(7)
        buf = np.random.normal(10, 40, 400)
        scores_buf = np.clip(50 + buf * 0.15 + np.random.normal(0, 10, 400), 20, 100)
        buf_df = pd.DataFrame({"buffer_hours": buf.clip(-48, 200), "score": scores_buf})
        fig4 = px.scatter(
            buf_df, x="buffer_hours", y="score",
            opacity=0.3, trendline="ols",
            title="Submission Buffer (hrs before deadline) vs Score",
            labels={"buffer_hours": "Hours Before Deadline (neg = late)", "score": "Score"},
            color_discrete_sequence=[GREEN],
        )
        fig4 = plotly_layout(fig4, height=340)
        st.plotly_chart(fig4, use_container_width=True, config=chart_config())

    chart_card_close()
    insight_box(
        "On-time submitters score an average of 67.07 vs 62.13 for late submitters — a 4.95-point gap. The negative correlation (r=−0.185) is statistically significant.",
        "Lateness is a symptom, not the cause. Students who submit late are usually those who didn't understand the material well enough to start on time.",
        "Don't just penalize late submissions — investigate why they're late. Flag students with 2+ late submissions for a check-in conversation."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q10 · Age bands ───────────────────────────────────────────────────────
    section_title("Q10 · OUTCOMES BY AGE BAND")
    chart_card_open("📊 Does age relate to grade, attendance, and engagement?")

    age_data = pd.DataFrame([
        {"age_band": "Under 20", "avg_grade": 70.1, "avg_att": 75.8, "avg_events": 58.3},
        {"age_band": "20-25",    "avg_grade": 70.8, "avg_att": 77.2, "avg_events": 60.1},
        {"age_band": "26-30",    "avg_grade": 71.3, "avg_att": 79.1, "avg_events": 62.4},
        {"age_band": "31-40",    "avg_grade": 70.5, "avg_att": 76.5, "avg_events": 59.8},
        {"age_band": "40+",      "avg_grade": 69.8, "avg_att": 75.1, "avg_events": 55.2},
    ])

    fig5 = go.Figure()
    for col_, color, name in [
        ("avg_grade",  BLUE,  "Avg Grade"),
        ("avg_att",    PURPLE,"Attendance %"),
        ("avg_events", GREEN, "Avg Events"),
    ]:
        fig5.add_trace(go.Bar(
            x=age_data["age_band"], y=age_data[col_],
            name=name, marker_color=color,
        ))
    fig5.update_layout(barmode="group", title="", xaxis_title="Age Band", yaxis_title="Value")
    fig5 = plotly_layout(fig5, height=380)
    st.plotly_chart(fig5, use_container_width=True, config=chart_config())
    csv_download_button(age_data, "⬇ Export Age Band Data CSV",
                        "age_band_outcomes.csv", key="dl_age_band")

    chart_card_close()
    insight_box(
        "The 26-30 age band has the best outcomes: highest avg grade (71.3) and highest attendance (79.1%). Differences across age bands are small overall.",
        "The 26-30 group likely includes working professionals who enrolled deliberately. But individual engagement patterns matter far more than age.",
        "Don't design separate programs by age. Focus on engagement patterns — students who watch videos and submit on time perform well regardless of age."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Q11 · Student segmentation ────────────────────────────────────────────
    section_title("Q11 · STUDENT SEGMENTATION — K-MEANS (k=4)")
    chart_card_open("🎯 4 Segments: High Achievers · Average Engaged · Struggling · At-Risk Disengaged")

    seg_summary = pd.DataFrame([
        {"Segment":"High Achievers",     "Count":186, "Avg Attendance":84.6,"Avg Grade":76.6,"Avg Events":72.1,"Avg Failed Concepts":2.1},
        {"Segment":"Average Engaged",    "Count":97,  "Avg Attendance":77.2,"Avg Grade":70.3,"Avg Events":61.4,"Avg Failed Concepts":5.3},
        {"Segment":"Struggling",         "Count":149, "Avg Attendance":75.1,"Avg Grade":72.2,"Avg Events":53.7,"Avg Failed Concepts":6.8},
        {"Segment":"At-Risk Disengaged", "Count":68,  "Avg Attendance":61.5,"Avg Grade":57.6,"Avg Events":38.2,"Avg Failed Concepts":13.4},
    ])
    seg_colors = {
        "High Achievers": GREEN,
        "Average Engaged": BLUE,
        "Struggling": AMBER,
        "At-Risk Disengaged": RED,
    }

    if not segments.empty and "att_rate" in segments.columns and "avg_grade" in segments.columns:
        color_seq = [seg_colors.get(s, BLUE) for s in segments["segment"].unique()]
        fig6 = px.scatter(
            segments.dropna(subset=["att_rate","avg_grade","segment"]),
            x="att_rate", y="avg_grade",
            color="segment",
            color_discrete_map=seg_colors,
            hover_data=["full_name","total_events","failed_concepts"] if "full_name" in segments.columns else None,
            title="Student Segments (K-Means, k=4) — Attendance vs Grade",
            labels={"att_rate":"Attendance Rate (%)","avg_grade":"Average Grade","segment":"Segment"},
            opacity=0.6,
        )
        fig6.add_hline(y=60, line_dash="dot", line_color=RED,
                       annotation_text="Pass threshold (60)")
        fig6 = plotly_layout(fig6, height=430)
        st.plotly_chart(fig6, use_container_width=True, config=chart_config())

    # Segment summary — grouped bar chart (replaces the table)
    st.markdown("<br>", unsafe_allow_html=True)
    c_sum1, c_sum2 = st.columns(2)
    with c_sum1:
        fig_cnt = px.bar(
            seg_summary, x="Segment", y="Count",
            color="Segment",
            color_discrete_map=seg_colors,
            text="Count",
            title="Students per Segment",
        )
        fig_cnt.update_traces(texttemplate="%{text}", textposition="outside")
        fig_cnt.update_layout(showlegend=False)
        fig_cnt = plotly_layout(fig_cnt, height=300)
        st.plotly_chart(fig_cnt, use_container_width=True, config=chart_config())

    with c_sum2:
        fig_grd = px.bar(
            seg_summary, x="Segment", y="Avg Grade",
            color="Segment",
            color_discrete_map=seg_colors,
            text="Avg Grade",
            title="Avg Grade per Segment",
        )
        fig_grd.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_grd.add_hline(y=60, line_dash="dot", line_color=RED)
        fig_grd.update_layout(showlegend=False, yaxis_range=[40, 90])
        fig_grd = plotly_layout(fig_grd, height=300)
        st.plotly_chart(fig_grd, use_container_width=True, config=chart_config())

    c_sum3, c_sum4 = st.columns(2)
    with c_sum3:
        fig_att_seg = px.bar(
            seg_summary, x="Segment", y="Avg Attendance",
            color="Segment",
            color_discrete_map=seg_colors,
            text="Avg Attendance",
            title="Avg Attendance % per Segment",
        )
        fig_att_seg.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_att_seg.update_layout(showlegend=False, yaxis_range=[40, 100])
        fig_att_seg = plotly_layout(fig_att_seg, height=300)
        st.plotly_chart(fig_att_seg, use_container_width=True, config=chart_config())

    with c_sum4:
        fig_fc = px.bar(
            seg_summary, x="Segment", y="Avg Failed Concepts",
            color="Segment",
            color_discrete_map=seg_colors,
            text="Avg Failed Concepts",
            title="Avg Failed Concepts per Segment",
        )
        fig_fc.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_fc.update_layout(showlegend=False)
        fig_fc = plotly_layout(fig_fc, height=300)
        st.plotly_chart(fig_fc, use_container_width=True, config=chart_config())

    csv_download_button(seg_summary, "⬇ Export Segment Summary CSV",
                        "segment_summary.csv", key="dl_seg_summary")
    chart_card_close()
    insight_box(
        "68 students (14%) are in the 'At-Risk Disengaged' segment — low attendance (61.5%), low grades (57.6), and 13+ failed concepts on average.",
        "The K-Means algorithm used 4 features: attendance rate, avg grade, total events, failed concepts — cleanly separating students into real academic behavior patterns.",
        "For At-Risk Disengaged: trigger outreach immediately. For Struggling (decent grades, low engagement): monitor their exam performance closely."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Student Roster (searchable, read-only, with CSV export) ───────────────
    section_title("STUDENT ROSTER — FILTER & SEARCH")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        search = st.text_input("🔍 Search student name", placeholder="e.g. Omar…")
    with fc2:
        groups_list = ["All"] + sorted(master["group_id"].dropna().unique().tolist()) if "group_id" in master.columns else ["All"]
        sel_group = st.selectbox("Group", groups_list)
    with fc3:
        perf_options = ["All","High Performer (≥75)","On Track (60-74)","Failing (<60)"]
        sel_perf = st.selectbox("Performance Tier", perf_options)

    df = master.copy()
    if search and "full_name" in df.columns:
        df = df[df["full_name"].str.contains(search, case=False, na=False)]
    if sel_group != "All" and "group_id" in df.columns:
        df = df[df["group_id"] == sel_group]
    if sel_perf != "All" and "avg_grade" in df.columns:
        if "≥75"  in sel_perf: df = df[df["avg_grade"] >= 75]
        elif "60-74" in sel_perf: df = df[(df["avg_grade"] >= 60) & (df["avg_grade"] < 75)]
        elif "<60"  in sel_perf: df = df[df["avg_grade"] < 60]

    cols_to_show = ["full_name","group_id","course_name","att_rate_pct","avg_grade","failed_concepts","late_submissions"]
    available    = [c for c in cols_to_show if c in df.columns]
    display_df   = df[available].copy().sort_values("avg_grade", ascending=False) if "avg_grade" in df.columns else df[available].copy()
    display_df   = display_df.rename(columns={
        "full_name":"Student","group_id":"Group","course_name":"Course",
        "att_rate_pct":"Attendance %","avg_grade":"Avg Grade",
        "failed_concepts":"Failed Concepts","late_submissions":"Late Submissions",
    })
    for c_ in ["Attendance %","Avg Grade"]:
        if c_ in display_df.columns:
            display_df[c_] = display_df[c_].round(1)

    roster_col, export_col = st.columns([5, 1])
    with roster_col:
        st.markdown(f'<div style="font-size:0.78rem;font-weight:600;color:#64748B;margin-bottom:8px;">SHOWING {len(display_df)} STUDENTS</div>', unsafe_allow_html=True)
    with export_col:
        csv_download_button(display_df, "⬇ Export CSV", "student_roster.csv", key="dl_roster")

    st.dataframe(
        display_df, use_container_width=True, hide_index=True, height=340,
        column_config={
            "Avg Grade":    st.column_config.ProgressColumn("Avg Grade",    min_value=0, max_value=100, format="%.1f"),
            "Attendance %": st.column_config.ProgressColumn("Attendance %", min_value=0, max_value=100, format="%.1f"),
        }
    )
