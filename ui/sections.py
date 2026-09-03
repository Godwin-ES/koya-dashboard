from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from reporting import extract_ai_data_quality_warnings, filter_dimension_metrics, sort_data_quality_issues
from ui.charts import render_dimension_chart
from ui.components import display_area_name, render_callout, render_metric_grid, render_section_heading


SALES_KEYS = [
    "total_leads",
    "closed_won_deals",
    "closed_lost_deals",
    "win_rate",
    "pipeline_value",
    "revenue_won",
    "marketing_spend",
    "cost_per_lead",
]

PROJECT_KEYS = [
    "active_projects",
    "completed_projects",
    "blocked_projects",
    "on_time_completion_rate",
    "average_delay",
    "budget_variance",
    "over_budget_projects",
]

PEOPLE_KEYS = [
    "active_headcount",
    "applications",
    "offers_accepted",
    "new_hires",
    "exits",
    "attrition_rate",
    "time_to_hire",
    "offer_acceptance_time",
]


def _content_card(title: str, body: str, class_name: str = "") -> None:
    st.html(
        f'<div class="content-card {escape(class_name)}"><h3>{escape(title)}</h3><p>{escape(body)}</p></div>',
    )


def _render_risk(risk: dict[str, Any]) -> None:
    severity = str(risk.get("severity") or "low").lower()
    if severity not in {"low", "medium", "high"}:
        severity = "low"
    st.html(
        f"""
        <div class="content-card item-card">
          <div class="item-head">
            <span class="item-area">{escape(display_area_name(risk.get('area')))}</span>
            <span class="severity severity-{escape(severity)}">{escape(severity)}</span>
          </div>
          <p>{escape(str(risk.get('finding') or 'No finding supplied.'))}</p>
          <div class="card-meta"><strong>Evidence</strong> · {escape(str(risk.get('evidence') or 'No evidence supplied.'))}</div>
        </div>
        """,
    )


def _render_action(action: dict[str, Any], number: int) -> None:
    priority = str(action.get("priority") or "low").lower()
    if priority not in {"low", "medium", "high"}:
        priority = "low"
    st.html(
        f"""
        <div class="content-card item-card">
          <div class="item-head">
            <span class="item-area">{escape(display_area_name(action.get('area')))}</span>
            <span class="severity severity-{escape(priority)}">{escape(priority)} priority</span>
          </div>
          <p><span class="action-number">{number:02d}</span>&nbsp;&nbsp;{escape(str(action.get('action') or 'No action supplied.'))}</p>
          <div class="card-meta"><strong>Why now</strong> · {escape(str(action.get('rationale') or 'No rationale supplied.'))}</div>
        </div>
        """,
    )


def render_overview(
    run: dict[str, Any],
    sales_index: dict[str, dict[str, Any]],
    project_index: dict[str, dict[str, Any]],
    people_index: dict[str, dict[str, Any]],
    ai_insight: dict[str, Any] | None,
) -> None:
    render_section_heading(
        "Leadership overview",
        "A selective view of the persisted operational results and the decisions they may require.",
        "Executive brief",
    )

    if run.get("status") == "partial":
        render_callout(
            "warning",
            "Deterministic report available",
            "This run completed with partial results. Operational KPIs remain authoritative; the AI layer may be unavailable.",
        )

    if ai_insight:
        summary = str(ai_insight.get("executive_summary") or "No executive summary was returned.")
        st.html(
            f'<div class="content-card summary-card"><div class="eyebrow">Executive summary</div><p>{escape(summary)}</p></div>',
        )
    else:
        render_callout(
            "warning",
            "AI analysis unavailable",
            "The deterministic KPI report is complete and remains fully usable. No interpretive summary was available for this run.",
        )
        if run.get("error_summary"):
            st.caption(str(run["error_summary"]))

    render_section_heading(
        "Operational snapshot",
        "Selected indicators from each function. Values and comparisons come directly from the persisted KPI rows.",
    )
    snapshot = {
        **{key: sales_index[key] for key in ("revenue_won", "win_rate") if key in sales_index},
        **{key: project_index[key] for key in ("active_projects", "completed_projects") if key in project_index},
        **{key: people_index[key] for key in ("active_headcount", "attrition_rate") if key in people_index},
    }
    render_metric_grid(
        snapshot,
        ["revenue_won", "win_rate", "active_projects", "completed_projects", "active_headcount", "attrition_rate"],
    )

    if not ai_insight:
        return

    st.html('<div class="trust-note">AI-generated decision support based on deterministic KPIs. Operational calculations remain authoritative.</div>')
    left, right = st.columns(2, gap="large")
    risks = ai_insight.get("operational_risks") or []
    actions = ai_insight.get("recommended_actions") or []

    with left:
        render_section_heading("Operational risks", "Evidence-backed concerns selected for leadership attention.")
        if risks:
            for risk in risks:
                _render_risk(risk)
        else:
            render_callout("success", "No material risks identified", "The AI analysis did not identify a material operational risk for this period.")

    with right:
        render_section_heading("Recommended actions", "Practical next steps grounded in the supplied reporting context.")
        if actions:
            for number, action in enumerate(actions, start=1):
                _render_action(action, number)
        else:
            render_callout("info", "No actions returned", "No recommended management actions were returned for this run.")


def render_sales(metric_index: dict[str, dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    render_section_heading(
        "Sales performance",
        "Pipeline activity, closed outcomes, revenue, and acquisition efficiency for the selected period.",
        "Commercial operations",
    )
    render_metric_grid(metric_index, SALES_KEYS)
    render_section_heading(
        "Revenue by lead source",
        "Closed Won revenue grouped by recorded lead source—not lead volume, conversion, or ROI.",
    )
    render_dimension_chart(
        filter_dimension_metrics(rows, "revenue_by_lead_source"),
        "Lead Source",
        "Revenue Won",
        "currency",
        "#087f78",
    )


def render_project_delivery(metric_index: dict[str, dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    render_section_heading(
        "Project delivery",
        "Current delivery load and period-completed outcomes across schedule and budget performance.",
        "Delivery operations",
    )
    render_metric_grid(metric_index, PROJECT_KEYS)

    snapshot_note = next(
        (
            metric.get("calculation_note")
            for key in ("active_projects", "blocked_projects")
            if (metric := metric_index.get(key)) and metric.get("calculation_note")
        ),
        None,
    )
    if snapshot_note:
        render_callout("warning", "Snapshot limitation", str(snapshot_note))

    render_section_heading(
        "Delivery load by team",
        "Unique union of current active projects and projects completed during the reporting period.",
    )
    render_dimension_chart(
        filter_dimension_metrics(rows, "delivery_load_by_team"),
        "Team",
        "Project Load",
        "count",
        "#356c8c",
    )


def render_people_operations(metric_index: dict[str, dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    render_section_heading(
        "People operations",
        "Hiring flow, workforce movement, recruiting pace, and point-in-time headcount.",
        "Workforce operations",
    )
    render_metric_grid(metric_index, PEOPLE_KEYS)
    render_section_heading(
        "Headcount by department",
        "Employees active at the end of the selected reporting period, grouped by department.",
    )
    render_dimension_chart(
        filter_dimension_metrics(rows, "headcount_by_department"),
        "Department",
        "Active Headcount",
        "count",
        "#7667a7",
    )


def render_data_quality(
    run: dict[str, Any],
    issues: list[dict[str, Any]],
    ai_insight: dict[str, Any] | None,
) -> None:
    render_section_heading(
        "Data quality",
        "Deterministic source-quality evidence for this run, separated from AI-selected executive limitations.",
        "Reporting confidence",
    )
    sorted_issues = sort_data_quality_issues(issues)
    error_count = sum(str(issue.get("severity", "")).lower() == "error" for issue in sorted_issues)
    warning_count = sum(str(issue.get("severity", "")).lower() == "warning" for issue in sorted_issues)
    metric_rows = {
        "issues": {"metric_label": "Detected Issues", "metric_value": len(sorted_issues), "metric_unit": "count"},
        "errors": {"metric_label": "Errors", "metric_value": error_count, "metric_unit": "count"},
        "warnings": {"metric_label": "Warnings", "metric_value": warning_count, "metric_unit": "count"},
        "sources": {
            "metric_label": "Affected Sources",
            "metric_value": len({str(i.get("source")) for i in sorted_issues if i.get("source")}),
            "metric_unit": "count",
        },
    }
    render_metric_grid(metric_rows, ["issues", "errors", "warnings", "sources"])

    ai_warnings = extract_ai_data_quality_warnings(ai_insight)
    if ai_warnings:
        render_section_heading(
            "Executive limitations",
            "Material reporting limitations selected by the AI analysis for management attention.",
        )
        columns = st.columns(2, gap="large")
        for index, warning in enumerate(ai_warnings):
            with columns[index % 2]:
                _content_card(
                    display_area_name(warning.get("source")),
                    str(warning.get("warning") or "Data quality warning."),
                )
                if warning.get("impact"):
                    st.caption(f"Impact · {warning['impact']}")
    elif ai_insight and ai_insight.get("data_quality_summary"):
        render_callout("info", "Executive data-quality summary", str(ai_insight["data_quality_summary"]))

    render_section_heading(
        "Issue register",
        "The complete deterministic register. Filters change presentation only and do not alter report values.",
    )
    if not sorted_issues:
        render_callout("success", "No issues detected", "No source-data quality issues were recorded for this reporting run.")
        return

    filter_col_1, filter_col_2 = st.columns(2)
    severities = sorted({str(issue.get("severity") or "Unknown").title() for issue in sorted_issues})
    sources = sorted({display_area_name(issue.get("source")) for issue in sorted_issues})
    with filter_col_1:
        selected_severities = st.multiselect("Severity", severities, default=severities, key="dq_severity_filter")
    with filter_col_2:
        selected_sources = st.multiselect("Source", sources, default=sources, key="dq_source_filter")

    table_rows = []
    for issue in sorted_issues:
        severity = str(issue.get("severity") or "Unknown").title()
        source = display_area_name(issue.get("source"))
        if severity not in selected_severities or source not in selected_sources:
            continue
        affected = issue.get("affected_metrics") or []
        table_rows.append(
            {
                "Severity": severity,
                "Source": source,
                "Record ID": issue.get("source_record_id") or "—",
                "Field": issue.get("field_name") or "—",
                "Issue": issue.get("message") or "—",
                "Affected KPIs": ", ".join(str(value).replace("_", " ").title() for value in affected) if affected else "None mapped",
            }
        )

    if not table_rows:
        st.info("No issues match the selected filters.")
        return

    frame = pd.DataFrame(table_rows)
    st.dataframe(
        frame,
        width="stretch",
        hide_index=True,
        height=min(560, 42 + 36 * len(frame)),
        column_config={
            "Severity": st.column_config.TextColumn(width="small"),
            "Source": st.column_config.TextColumn(width="medium"),
            "Record ID": st.column_config.TextColumn(width="small"),
            "Field": st.column_config.TextColumn(width="small"),
            "Issue": st.column_config.TextColumn(width="large"),
            "Affected KPIs": st.column_config.TextColumn(width="large"),
        },
    )
    st.caption(f"Showing {len(frame)} of {len(sorted_issues)} detected issues · Run total: {run.get('data_quality_issue_count', len(sorted_issues))}")
