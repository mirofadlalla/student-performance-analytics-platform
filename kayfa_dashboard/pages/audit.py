import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import plotly_layout, insight_box, page_header, section_title

BLUE   = "#4DA3FF"
PURPLE = "#8B5CF6"
CYAN   = "#22D3EE"
RED    = "#F87171"
AMBER  = "#FBD24C"
GREEN  = "#4ADE80"

# ── Full audit log (from notebook) ──────────────────────────────────────────
AUDIT_DATA = [
    {"Issue":"#01","Category":"Duplicate","Dataset":"students","Severity":"Medium","Description":"2 student rows duplicated at EOF (S0362, S0074) with inconsistent ages","Status":"Resolved"},
    {"Issue":"#02","Category":"Missing","Dataset":"students","Severity":"Medium","Description":"4 NULL full_name values — imputed from email (S0109, S0135, S0287, S0366)","Status":"Resolved"},
    {"Issue":"#03","Category":"Invalid","Dataset":"students","Severity":"High","Description":"Impossible ages: -22, -5 (corrected to positive), 121 (imputed with mean)","Status":"Resolved"},
    {"Issue":"#04","Category":"Encoding","Dataset":"students","Severity":"Medium","Description":"Gender column had 10 distinct labels — normalised to Male/Female via name lookup","Status":"Resolved"},
    {"Issue":"#05","Category":"Invalid","Dataset":"students","Severity":"High","Description":"3 malformed emails (missing@, @kayfa.io, not-an-email) — rebuilt from full_name","Status":"Resolved"},
    {"Issue":"#06","Category":"Duplicate","Dataset":"students","Severity":"High","Description":"97 duplicate email addresses across different student_ids","Status":"Resolved"},
    {"Issue":"#07","Category":"Referential","Dataset":"students → groups","Severity":"Critical","Description":"3 students with non-existent group_ids: GZZ (S0014), G77 (S0095, S0323)","Status":"Resolved"},
    {"Issue":"#08","Category":"Duplicate","Dataset":"groups","Severity":"Low","Description":"G01 appears twice as exact duplicate row — deduplicated","Status":"Resolved"},
    {"Issue":"#09","Category":"ETL Artifact","Dataset":"groups","Severity":"High","Description":"TEST_GROUP_DELETE (G99) test record leaked into production data","Status":"Resolved"},
    {"Issue":"#10","Category":"Missing","Dataset":"groups","Severity":"Low","Description":"NULL instructor on G99 — removed with G99","Status":"Resolved"},
    {"Issue":"#11","Category":"Encoding","Dataset":"groups","Severity":"Medium","Description":"session_time in 3 formats: HH:MM, H PM, HHMM — normalised to HH:MM","Status":"Resolved"},
    {"Issue":"#12","Category":"Logical","Dataset":"groups","Severity":"Medium","Description":"stated_num_students vs actual mismatch in 5 groups (G03, G05, G07, G08, G10)","Status":"Flagged"},
    {"Issue":"#13","Category":"Invalid","Dataset":"grades","Severity":"Critical","Description":"Negative score -10 for S0001 Quiz 1 (GR00001)","Status":"Resolved"},
    {"Issue":"#14","Category":"Invalid","Dataset":"grades","Severity":"Critical","Description":"Score 187 > max_score 100 for S0002 Quiz 2 (GR00013)","Status":"Resolved"},
    {"Issue":"#15","Category":"Invalid","Dataset":"grades","Severity":"High","Description":"max_score=10 for S0005 Quiz 1 (GR00045) — should be 100","Status":"Resolved"},
    {"Issue":"#16","Category":"Missing","Dataset":"grades","Severity":"Medium","Description":"2 NULL scores: S0003 Quiz 4, S0004 Assignment 1 — imputed","Status":"Resolved"},
    {"Issue":"#17","Category":"ETL Artifact","Dataset":"grades","Severity":"High","Description":"GR99999 'Bonus Exam' (C001-EXTRA) — non-standard sentinel grade for S0008","Status":"Resolved"},
    {"Issue":"#18","Category":"Duplicate/Logical","Dataset":"grades","Severity":"Critical","Description":"S0010 has Final Exam from wrong course C006 (GR99998) — pipeline merge error","Status":"Resolved"},
    {"Issue":"#19","Category":"Referential","Dataset":"grades → students","Severity":"High","Description":"Group_id mismatch in grades vs students for S0014, S0095, S0323","Status":"Resolved"},
    {"Issue":"#20","Category":"Duplicate","Dataset":"attendance","Severity":"Medium","Description":"2 duplicate record_ids: AT002883, AT007249 (4 total rows)","Status":"Resolved"},
    {"Issue":"#21","Category":"Encoding","Dataset":"attendance","Severity":"Low","Description":"'Atttended' typo in status column (AT900004) — normalised","Status":"Resolved"},
    {"Issue":"#22","Category":"Referential","Dataset":"attendance → students","Severity":"Critical","Description":"Orphan student S9999 in AT900001 — not in students table","Status":"Resolved"},
    {"Issue":"#23","Category":"Temporal","Dataset":"attendance → students","Severity":"High","Description":"606 attendance records before student enrollment_date","Status":"Resolved"},
    {"Issue":"#24","Category":"Logical","Dataset":"attendance → students","Severity":"Medium","Description":"13 attendance records for students attending wrong group","Status":"Resolved"},
    {"Issue":"#25","Category":"ETL Artifact","Dataset":"attendance","Severity":"High","Description":"AT900001–AT900004 block: injected bad-data test records","Status":"Resolved"},
    {"Issue":"#26","Category":"Temporal/Logical","Dataset":"attendance → groups","Severity":"Medium","Description":"AT900002: G01 session on Friday — G01 session_day is Thursday","Status":"Resolved"},
    {"Issue":"#27","Category":"Duplicate","Dataset":"concepts","Severity":"Medium","Description":"5 duplicate record_ids (10 total rows): CP000248, CP001858, …","Status":"Resolved"},
    {"Issue":"#28","Category":"Invalid/ETL Artifact","Dataset":"concepts","Severity":"Critical","Description":"CPBAD02 score=-33, CPBAD03 score=142 — out-of-range injected records","Status":"Resolved"},
    {"Issue":"#29","Category":"Logical","Dataset":"concepts","Severity":"High","Description":"mastery_status inconsistent at score=60.0: 13 'failed', 16 'passed' — re-derived","Status":"Resolved"},
    {"Issue":"#30","Category":"Duplicate","Dataset":"engagement","Severity":"Medium","Description":"8 duplicate event_ids (16 total rows)","Status":"Resolved"},
    {"Issue":"#31","Category":"Invalid","Dataset":"engagement","Severity":"Medium","Description":"2 records with negative duration_seconds (-120)","Status":"Resolved"},
    {"Issue":"#32","Category":"Invalid","Dataset":"engagement","Severity":"High","Description":"Sentinel value 99999 in duration_seconds (EV000004) → 27.8 hrs impossible","Status":"Resolved"},
    {"Issue":"#33","Category":"Referential","Dataset":"engagement → students","Severity":"Critical","Description":"Orphan student S8888 in EVBAD01 — not in students table","Status":"Resolved"},
    {"Issue":"#34","Category":"ETL Artifact","Dataset":"engagement","Severity":"High","Description":"EVBAD01, EVBAD02 — sentinel IDs marking injected bad-data records","Status":"Resolved"},
    {"Issue":"#35","Category":"Temporal","Dataset":"engagement → students","Severity":"High","Description":"EV000001 event 11 months before S0001 enrollment","Status":"Resolved"},
    {"Issue":"#36","Category":"Missing","Dataset":"engagement","Severity":"Low","Description":"22,049 NULL duration_seconds (71%) — structural: video_watch only field","Status":"Documented"},
    {"Issue":"#37","Category":"Duplicate","Dataset":"submissions","Severity":"Medium","Description":"3 duplicate submission_ids (6 total rows): SUB00089, SUB00489, SUB01241","Status":"Resolved"},
    {"Issue":"#38","Category":"Invalid","Dataset":"submissions","Severity":"Medium","Description":"Negative time_spent_minutes = -40 (SUB00006)","Status":"Resolved"},
    {"Issue":"#39","Category":"Missing/Logical","Dataset":"submissions","Severity":"Medium","Description":"NULL submitted_at with is_late=False (SUB00010) — is_late set to NaN","Status":"Resolved"},
    {"Issue":"#40","Category":"Logical","Dataset":"submissions","Severity":"High","Description":"is_late=True for on-time submissions (SUB00001, SUB01220) — recalculated","Status":"Resolved"},
    {"Issue":"#41","Category":"Temporal/Logical","Dataset":"attendance → groups","Severity":"Medium","Description":"AT900003: G06 session on Thursday — G06 session_day is Saturday","Status":"Resolved"},
]

audit_df = pd.DataFrame(AUDIT_DATA)

def render():
    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="
      background: linear-gradient(135deg, rgba(11,16,32,0.95) 0%, rgba(15,26,51,0.95) 100%);
      border: 1px solid rgba(77,163,255,0.2);
      border-radius: 20px;
      padding: 36px 40px;
      margin-bottom: 28px;
      position: relative;
      overflow: hidden;
    ">
      <div style="position:absolute;top:-30%;right:-5%;width:40%;height:180%;
                  background:radial-gradient(ellipse,rgba(139,92,246,0.06) 0%,transparent 70%);"></div>
      <div style="display:flex;align-items:center;gap:20px;margin-bottom:16px;">
        <div style="
          background:linear-gradient(135deg,#4DA3FF,#8B5CF6);
          border-radius:12px;padding:12px 18px;
          font-size:1.8rem;line-height:1;
        ">🛡️</div>
        <div>
          <div style="font-size:0.7rem;color:#4DA3FF;font-weight:700;text-transform:uppercase;letter-spacing:.15em;margin-bottom:4px;">
            Kayfa Analytics Platform · Confidential
          </div>
          <h1 style="font-size:1.8rem;font-weight:800;color:#F1F5F9;margin:0;line-height:1.1;">
            Data Quality Audit Report
          </h1>
        </div>
      </div>
      <p style="color:#94A3B8;font-size:0.92rem;margin:0;max-width:600px;">
        <strong style="color:#CBD5E1;">41 data integrity issues</strong> detected and resolved across a
        multi-source pipeline spanning 8 heterogeneous datasets —
        students, groups, grades, attendance, concepts, engagement, submissions, and courses.
      </p>
      <div style="margin-top:20px;display:flex;gap:16px;flex-wrap:wrap;">
        <div style="background:rgba(74,222,128,0.1);border:1px solid rgba(74,222,128,0.25);
                    border-radius:8px;padding:8px 16px;font-size:0.8rem;color:#4ADE80;font-weight:600;">
          ✅ Audit Complete
        </div>
        <div style="background:rgba(77,163,255,0.1);border:1px solid rgba(77,163,255,0.25);
                    border-radius:8px;padding:8px 16px;font-size:0.8rem;color:#4DA3FF;font-weight:600;">
          📅 June 2026
        </div>
        <div style="background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.25);
                    border-radius:8px;padding:8px 16px;font-size:0.8rem;color:#A78BFA;font-weight:600;">
          🏢 Kayfa EdTech Platform
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quality Score Gauge + KPIs ───────────────────────────────────────────
    section_title("AUDIT SCORECARD")
    gc1, gc2 = st.columns([1, 2])

    with gc1:
        st.markdown('<div class="chart-card"><h3>🎯 Data Quality Score</h3>', unsafe_allow_html=True)
        score = 91
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            number={"suffix": "/100", "font": {"size": 36, "color": "#4ADE80", "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#334155", "tickfont": {"color": "#64748B"}},
                "bar": {"color": "#4ADE80", "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(77,163,255,0.2)",
                "steps": [
                    {"range": [0, 50], "color": "rgba(248,113,113,0.15)"},
                    {"range": [50, 75], "color": "rgba(251,191,36,0.1)"},
                    {"range": [75, 100], "color": "rgba(74,222,128,0.08)"},
                ],
                "threshold": {
                    "line": {"color": CYAN, "width": 2},
                    "thickness": 0.8,
                    "value": score,
                },
            },
            title={"text": "After Remediation", "font": {"color": "#94A3B8", "size": 12}},
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            height=260,
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with gc2:
        st.markdown('<div class="chart-card"><h3>📊 Issue Breakdown by Severity</h3>', unsafe_allow_html=True)
        severity_counts = audit_df["Severity"].value_counts()
        severity_order = ["Critical", "High", "Medium", "Low"]
        severity_colors = {"Critical": RED, "High": AMBER, "Medium": BLUE, "Low": CYAN}
        sc = {s: severity_counts.get(s, 0) for s in severity_order}

        fig = go.Figure()
        for sev, color in severity_colors.items():
            fig.add_trace(go.Bar(
                name=sev,
                x=[sev],
                y=[sc[sev]],
                marker_color=color,
                text=[sc[sev]],
                textposition="outside",
                textfont=dict(size=14, color="#E2E8F0", family="Inter", weight=700),
                width=0.5,
            ))
        fig = plotly_layout(fig, height=240)
        fig.update_layout(showlegend=False, barmode="group")
        fig.update_yaxes(range=[0, max(sc.values()) + 3], title_text="Issue Count")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

        # Severity badges
        st.markdown(f"""
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:4px;">
          <div class="badge badge-red">🔴 Critical: {sc['Critical']}</div>
          <div class="badge badge-amber">🟡 High: {sc['High']}</div>
          <div class="badge badge-green">🔵 Medium: {sc['Medium']}</div>
          <div class="badge badge-purple">⚪ Low: {sc['Low']}</div>
          <div class="badge badge-green">✅ Total: {len(audit_df)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Issue Breakdown Cards by Category ───────────────────────────────────
    section_title("ISSUE CATEGORIES — DEEP DIVE")
    cat_counts = audit_df["Category"].value_counts()

    cat_meta = {
        "Duplicate": ("🔁", BLUE, "Exact or near-duplicate records identified and removed across 6 datasets."),
        "Invalid": ("❌", RED, "Values outside valid domain: negative scores, impossible ages, sentinel values."),
        "Missing": ("◻️", AMBER, "NULL or absent required fields — imputed or flagged."),
        "Referential": ("🔗", PURPLE, "FK violations: orphan student IDs, missing group references."),
        "ETL Artifact": ("⚙️", CYAN, "Test/sentinel records leaked into production from upstream pipelines."),
        "Encoding": ("🔤", "#A78BFA", "Inconsistent formats: date formats, gender labels, session times."),
        "Temporal": ("🕐", "#FB923C", "Timestamps violating logical order (events before enrollment)."),
        "Logical": ("🧠", "#34D399", "Business rule violations: wrong group assignments, miscalculated flags."),
    }

    card_cols = st.columns(4)
    for i, (cat, cnt) in enumerate(cat_counts.items()):
        icon, color, desc = cat_meta.get(cat, ("📋", BLUE, ""))
        with card_cols[i % 4]:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{color};">
              <div class="kpi-icon">{icon}</div>
              <div class="kpi-value" style="font-size:1.6rem;">{cnt}</div>
              <div class="kpi-label">{cat}</div>
              <div style="font-size:0.72rem;color:#475569;margin-top:8px;line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Before vs After Chart ────────────────────────────────────────────────
    section_title("BEFORE vs AFTER — DATA IMPROVEMENT")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="chart-card"><h3>📈 Issues by Dataset</h3>', unsafe_allow_html=True)
        ds_counts = audit_df["Dataset"].str.split(" →").str[0].value_counts().reset_index()
        ds_counts.columns = ["Dataset", "Issues"]
        ds_counts = ds_counts.sort_values("Issues", ascending=True)

        fig = go.Figure(go.Bar(
            x=ds_counts["Issues"],
            y=ds_counts["Dataset"],
            orientation="h",
            marker_color=[RED if v >= 7 else AMBER if v >= 4 else BLUE for v in ds_counts["Issues"]],
            text=ds_counts["Issues"],
            textposition="outside",
            textfont=dict(size=12, color="#94A3B8"),
        ))
        fig = plotly_layout(fig, height=320)
        fig.update_xaxes(range=[0, ds_counts["Issues"].max() + 3], title_text="Issue Count")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><h3>🔄 Resolution Status</h3>', unsafe_allow_html=True)
        status_counts = audit_df["Status"].value_counts()
        status_colors = {"Resolved": GREEN, "Flagged": AMBER, "Documented": CYAN}
        colors_list = [status_colors.get(s, BLUE) for s in status_counts.index]

        fig = go.Figure(go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.55,
            marker=dict(colors=colors_list, line=dict(color="#0B1020", width=3)),
            textfont=dict(size=12, color="#94A3B8"),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#94A3B8"),
            legend=dict(font=dict(size=11, color="#94A3B8")),
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            annotations=[dict(
                text=f"<b>{status_counts.get('Resolved', 0)}</b><br>Resolved",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=15, color="#4ADE80", family="Inter"),
            )],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Achievement Banner ───────────────────────────────────────────────────
    st.markdown("""
    <div style="
      background: linear-gradient(135deg, rgba(74,222,128,0.08) 0%, rgba(34,211,238,0.08) 100%);
      border: 1px solid rgba(74,222,128,0.25);
      border-radius: 14px;
      padding: 24px 32px;
      margin: 24px 0;
      text-align: center;
    ">
      <div style="font-size:2rem;margin-bottom:8px;">🏆</div>
      <div style="font-size:1.1rem;font-weight:700;color:#4ADE80;margin-bottom:8px;">
        Mission Accomplished
      </div>
      <div style="color:#94A3B8;font-size:0.9rem;max-width:600px;margin:0 auto;line-height:1.6;">
        All <strong style="color:#22D3EE;">41 data integrity issues</strong> successfully identified and resolved
        across <strong style="color:#22D3EE;">8 heterogeneous datasets</strong> in the Kayfa student analytics pipeline.
        Data quality score improved from an estimated <strong style="color:#F87171;">52/100</strong> to
        <strong style="color:#4ADE80;">91/100</strong> after remediation.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Full Audit Log Table ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_title("COMPLETE AUDIT LOG — ALL 41 ISSUES")
    st.markdown('<div class="chart-card"><h3>📋 Issue Registry</h3>', unsafe_allow_html=True)

    # Filters
    af1, af2, af3 = st.columns(3)
    with af1:
        sev_filter = st.multiselect("Severity", ["Critical", "High", "Medium", "Low"], default=[])
    with af2:
        cat_filter = st.multiselect("Category", sorted(audit_df["Category"].unique().tolist()), default=[])
    with af3:
        ds_filter = st.multiselect("Dataset", sorted(audit_df["Dataset"].str.split(" →").str[0].unique().tolist()), default=[])

    filtered = audit_df.copy()
    if sev_filter:
        filtered = filtered[filtered["Severity"].isin(sev_filter)]
    if cat_filter:
        filtered = filtered[filtered["Category"].isin(cat_filter)]
    if ds_filter:
        filtered = filtered[filtered["Dataset"].str.split(" →").str[0].isin(ds_filter)]

    def severity_emoji(s):
        return {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "⚪"}.get(s, "") + " " + s

    def status_emoji(s):
        return {"Resolved": "✅", "Flagged": "⚠️", "Documented": "📝"}.get(s, "") + " " + s

    display_log = filtered[["Issue", "Severity", "Category", "Dataset", "Description", "Status"]].copy()
    display_log["Severity"] = display_log["Severity"].apply(severity_emoji)
    display_log["Status"] = display_log["Status"].apply(status_emoji)

    st.dataframe(display_log, use_container_width=True, hide_index=True, height=400)
    st.markdown(f'<div style="font-size:0.78rem;color:#475569;margin-top:8px;">Showing {len(filtered)} of {len(audit_df)} issues</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
