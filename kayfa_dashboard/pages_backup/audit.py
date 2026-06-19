import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import load_collection, plotly_layout, insight_box, page_header, section_title

BLUE   = "#4DA3FF"
PURPLE = "#8B5CF6"
CYAN   = "#22D3EE"
RED    = "#F87171"
AMBER  = "#FBD24C"
GREEN  = "#4ADE80"

def render():
    # ── Load audit log from MongoDB ──────────────────────────────────────────
    with st.spinner("Loading audit data…"):
        audit_df = load_collection("audit_log")

    # If MongoDB has no audit_log collection, show a clear message
    if audit_df.empty:
        st.warning(
            "⚠️ No audit log found in MongoDB. "
            "Please upload your audit log to the `audit_log` collection with fields: "
            "Issue, Category, Dataset, Severity, Description, Status."
        )
        # Show schema helper
        st.markdown("""
        **Expected document schema in `audit_log` collection:**
        ```json
        {
          "Issue": "#01",
          "Category": "Duplicate",
          "Dataset": "students",
          "Severity": "High",
          "Description": "2 duplicate student rows at EOF",
          "Status": "Resolved"
        }
        ```
        """)
        return

    # ── Ensure expected columns exist ────────────────────────────────────────
    expected_cols = ["Issue", "Category", "Dataset", "Severity", "Description", "Status"]
    missing_cols = [c for c in expected_cols if c not in audit_df.columns]
    if missing_cols:
        st.error(f"Audit log is missing columns: {missing_cols}. Check your MongoDB collection schema.")
        st.dataframe(audit_df.head(5))
        return

    total_issues    = len(audit_df)
    resolved_count  = int((audit_df["Status"] == "Resolved").sum())
    critical_count  = int((audit_df["Severity"] == "Critical").sum())
    datasets_count  = audit_df["Dataset"].str.split(" →").str[0].nunique()

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
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
        <strong style="color:#CBD5E1;">{total_issues} data integrity issues</strong> detected and resolved across a
        multi-source pipeline spanning {datasets_count} heterogeneous datasets.
      </p>
      <div style="margin-top:20px;display:flex;gap:16px;flex-wrap:wrap;">
        <div style="background:rgba(74,222,128,0.1);border:1px solid rgba(74,222,128,0.25);
                    border-radius:8px;padding:8px 16px;font-size:0.8rem;color:#4ADE80;font-weight:600;">
          ✅ Audit Complete
        </div>
        <div style="background:rgba(77,163,255,0.1);border:1px solid rgba(77,163,255,0.25);
                    border-radius:8px;padding:8px 16px;font-size:0.8rem;color:#4DA3FF;font-weight:600;">
          🗂️ {total_issues} Issues Logged
        </div>
        <div style="background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.25);
                    border-radius:8px;padding:8px 16px;font-size:0.8rem;color:#A78BFA;font-weight:600;">
          🏢 Kayfa EdTech Platform
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary KPIs ─────────────────────────────────────────────────────────
    section_title("AUDIT SUMMARY")
    gc1, gc2 = st.columns([1, 1.5])

    with gc1:
        # Quality score gauge (computed: resolved pct mapped to 0-100)
        st.markdown('<div class="chart-card"><h3>🎯 Data Quality Score</h3>', unsafe_allow_html=True)
        resolved_pct = resolved_count / total_issues if total_issues > 0 else 0
        score = round(resolved_pct * 100)  # simple proxy: % resolved → quality

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100", "font": {"size": 28, "color": "#E2E8F0", "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748B", "tickfont": {"size": 10}},
                "bar": {"color": "#4ADE80", "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(77,163,255,0.2)",
                "steps": [
                    {"range": [0, 50],  "color": "rgba(248,113,113,0.1)"},
                    {"range": [50, 75], "color": "rgba(251,191,36,0.1)"},
                    {"range": [75, 100],"color": "rgba(74,222,128,0.08)"},
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
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"), height=260,
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with gc2:
        st.markdown('<div class="chart-card"><h3>📊 Issue Breakdown by Severity</h3>', unsafe_allow_html=True)
        severity_order  = ["Critical", "High", "Medium", "Low"]
        severity_colors = {"Critical": RED, "High": AMBER, "Medium": BLUE, "Low": CYAN}
        severity_counts = audit_df["Severity"].value_counts()
        sc = {s: int(severity_counts.get(s, 0)) for s in severity_order}

        fig = go.Figure()
        for sev, color in severity_colors.items():
            fig.add_trace(go.Bar(
                name=sev, x=[sev], y=[sc[sev]],
                marker_color=color,
                text=[sc[sev]], textposition="outside",
                textfont=dict(size=14, color="#E2E8F0", family="Inter", weight=700),
                width=0.5,
            ))
        fig = plotly_layout(fig, height=240)
        fig.update_layout(showlegend=False, barmode="group")
        fig.update_yaxes(range=[0, max(sc.values(), default=1) + 3], title_text="Issue Count")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:4px;">
          <div class="badge badge-red">🔴 Critical: {sc['Critical']}</div>
          <div class="badge badge-amber">🟡 High: {sc['High']}</div>
          <div class="badge badge-green">🔵 Medium: {sc['Medium']}</div>
          <div class="badge badge-purple">⚪ Low: {sc['Low']}</div>
          <div class="badge badge-green">✅ Total: {total_issues}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Issue categories ──────────────────────────────────────────────────────
    section_title("ISSUE CATEGORIES — DEEP DIVE")
    cat_counts = audit_df["Category"].value_counts()

    cat_meta = {
        "Duplicate":       ("🔁", BLUE,    "Exact or near-duplicate records identified and removed."),
        "Invalid":         ("❌", RED,     "Values outside valid domain: negative scores, impossible ages, sentinel values."),
        "Missing":         ("◻️", AMBER,   "NULL or absent required fields — imputed or flagged."),
        "Referential":     ("🔗", PURPLE,  "FK violations: orphan student IDs, missing group references."),
        "ETL Artifact":    ("⚙️", CYAN,    "Test/sentinel records leaked into production from upstream pipelines."),
        "Encoding":        ("🔤", "#A78BFA","Inconsistent formats: date formats, gender labels, session times."),
        "Temporal":        ("🕐", "#FB923C","Timestamps violating logical order (events before enrollment)."),
        "Logical":         ("🧠", "#34D399","Business rule violations: wrong group assignments, miscalculated flags."),
        "Duplicate/Logical":("🔁🧠", BLUE, "Combined duplicate and logical inconsistency."),
        "Missing/Logical": ("◻️🧠", AMBER, "Missing data combined with business rule violation."),
        "Temporal/Logical":("🕐🧠", "#FB923C","Temporal inconsistency combined with logical error."),
        "Invalid/ETL Artifact":("❌⚙️", RED, "Invalid sentinel record from upstream ETL pipeline."),
    }

    card_cols = st.columns(4)
    for i, (cat, cnt) in enumerate(cat_counts.items()):
        icon, color, desc = cat_meta.get(cat, ("📋", BLUE, "Data quality issue identified and logged."))
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

    # ── Before vs After ───────────────────────────────────────────────────────
    section_title("BEFORE vs AFTER — DATA IMPROVEMENT")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="chart-card"><h3>📈 Issues by Dataset</h3>', unsafe_allow_html=True)
        ds_counts = audit_df["Dataset"].str.split(" →").str[0].value_counts().reset_index()
        ds_counts.columns = ["Dataset", "Issues"]
        ds_counts = ds_counts.sort_values("Issues", ascending=True)

        fig = go.Figure(go.Bar(
            x=ds_counts["Issues"], y=ds_counts["Dataset"],
            orientation="h",
            marker_color=[RED if v >= 7 else AMBER if v >= 4 else BLUE for v in ds_counts["Issues"]],
            text=ds_counts["Issues"], textposition="outside",
            textfont=dict(size=12, color="#94A3B8"),
        ))
        fig = plotly_layout(fig, height=max(300, len(ds_counts)*40))
        fig.update_xaxes(range=[0, ds_counts["Issues"].max() + 3], title_text="Issue Count")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><h3>🔄 Resolution Status</h3>', unsafe_allow_html=True)
        status_counts = audit_df["Status"].value_counts()
        status_colors = {"Resolved": GREEN, "Flagged": AMBER, "Documented": CYAN}
        colors_list = [status_colors.get(s, BLUE) for s in status_counts.index]

        fig = go.Figure(go.Pie(
            labels=status_counts.index, values=status_counts.values,
            hole=0.55,
            marker=dict(colors=colors_list, line=dict(color="#0B1020", width=3)),
            textfont=dict(size=12, color="#94A3B8"),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#94A3B8"),
            legend=dict(font=dict(size=11, color="#94A3B8")),
            margin=dict(l=10, r=10, t=10, b=10), height=320,
            annotations=[dict(
                text=f"<b>{resolved_count}</b><br>Resolved",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=15, color="#4ADE80", family="Inter"),
            )],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Achievement Banner ────────────────────────────────────────────────────
    unresolved = total_issues - resolved_count
    st.markdown(f"""
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
        {"Mission Accomplished" if unresolved == 0 else "Audit In Progress"}
      </div>
      <div style="color:#94A3B8;font-size:0.9rem;max-width:600px;margin:0 auto;line-height:1.6;">
        <strong style="color:#22D3EE;">{resolved_count} of {total_issues}</strong> data integrity issues
        successfully identified and resolved across <strong style="color:#22D3EE;">{datasets_count}</strong> datasets.
        {f'<br><span style="color:{AMBER};">{unresolved} issues still flagged or under review.</span>' if unresolved > 0 else ""}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Full Audit Log Table ──────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section_title(f"COMPLETE AUDIT LOG — ALL {total_issues} ISSUES")
    st.markdown('<div class="chart-card"><h3>📋 Issue Registry</h3>', unsafe_allow_html=True)

    # Filters
    af1, af2, af3 = st.columns(3)
    with af1:
        sev_filter = st.multiselect("Severity", sorted(audit_df["Severity"].unique().tolist()), default=[])
    with af2:
        cat_filter = st.multiselect("Category", sorted(audit_df["Category"].unique().tolist()), default=[])
    with af3:
        ds_filter  = st.multiselect("Dataset",  sorted(audit_df["Dataset"].str.split(" →").str[0].unique().tolist()), default=[])

    filtered = audit_df.copy()
    if sev_filter:
        filtered = filtered[filtered["Severity"].isin(sev_filter)]
    if cat_filter:
        filtered = filtered[filtered["Category"].isin(cat_filter)]
    if ds_filter:
        filtered = filtered[filtered["Dataset"].str.split(" →").str[0].isin(ds_filter)]

    def sev_emoji(s):
        return {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "⚪"}.get(s, "") + " " + s

    def status_emoji(s):
        return {"Resolved": "✅", "Flagged": "⚠️", "Documented": "📝"}.get(s, "") + " " + s

    display_log = filtered[expected_cols].copy()
    display_log["Severity"] = display_log["Severity"].apply(sev_emoji)
    display_log["Status"]   = display_log["Status"].apply(status_emoji)

    st.dataframe(display_log, use_container_width=True, hide_index=True, height=400)
    st.markdown(
        f'<div style="font-size:0.78rem;color:#475569;margin-top:8px;">Showing {len(filtered)} of {total_issues} issues</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
