from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from typing import Any
from zoneinfo import ZoneInfo

import streamlit as st

from reporting import (
    format_comparison_value,
    format_metric_delta,
    format_metric_value,
)


AREA_LABELS = {
    "sales": "Sales",
    "project_delivery": "Project Delivery",
    "people_ops": "People Operations",
    "data_quality": "Data Quality",
    "cross_functional": "Cross-functional",
    "cross_source": "Cross-source",
}

LAGOS_TIME_ZONE = ZoneInfo("Africa/Lagos")


def display_area_name(value: str | None) -> str:
    if not value:
        return "Operations"
    return AREA_LABELS.get(value, value.replace("_", " ").title())


def format_date(value: Any) -> str:
    if not value:
        return "Unavailable"
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.strftime("%d %b %Y")
    except ValueError:
        return str(value)


def format_timestamp(value: Any) -> str:
    if not value:
        return "Time unavailable"
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        local_time = parsed.astimezone(LAGOS_TIME_ZONE)
        return local_time.strftime("%d %b %Y · %H:%M %Z")
    except ValueError:
        return str(value)


def status_badge(status: str | None) -> str:
    normalized = str(status or "unknown").lower().replace(" ", "-")
    label = str(status or "Unknown").replace("_", " ").title()
    return (
        f'<span class="status-badge status-{escape(normalized)}">'
        f"{escape(label)}</span>"
    )


def render_report_header(run: dict[str, Any]) -> None:
    start = format_date(run.get("period_start"))
    end = format_date(run.get("period_end"))
    comparison_start = run.get("comparison_start")
    comparison_end = run.get("comparison_end")
    if comparison_start and comparison_end:
        comparison = (
            f"Compared with {format_date(comparison_start)} – "
            f"{format_date(comparison_end)}"
        )
    else:
        comparison = "No comparison period available"

    st.html(
        f"""
        <div class="report-header">
          <div>
            <div class="eyebrow">Currently viewing</div>
            <h1 class="report-title">{escape(str(run.get('period_label') or 'Operations Report'))}</h1>
            <div class="report-subtitle">{escape(start)} – {escape(end)} &nbsp;·&nbsp; {escape(comparison)}</div>
          </div>
          <div class="report-meta">
            {status_badge(run.get('status'))}
            <div class="updated">Generated {escape(format_timestamp(run.get('completed_at')))}</div>
          </div>
        </div>
        """,
    )


def render_health_strip(run: dict[str, Any]) -> None:
    sources = [
        ("Sales", run.get("sales_source_status"), run.get("sales_record_count")),
        ("Project Delivery", run.get("project_source_status"), run.get("project_record_count")),
        ("People Operations", run.get("people_source_status"), run.get("people_record_count")),
    ]
    cards = []
    for label, status, count in sources:
        count_text = f"{count:,} source records" if isinstance(count, int) else "Record count unavailable"
        source_state = str(status or "unknown").replace("_", " ").title()
        cards.append(
            f"""
            <div class="health-card">
              <div class="health-top"><span class="health-label">{escape(label)}</span>{status_badge(status)}</div>
              <div class="health-value">{escape(source_state)}</div>
              <div class="health-detail">{escape(count_text)}</div>
            </div>
            """
        )

    issue_count = run.get("data_quality_issue_count")
    issue_text = f"{issue_count:,}" if isinstance(issue_count, int) else "—"
    issue_status = "warning" if issue_count else "ok"
    cards.append(
        f"""
        <div class="health-card">
          <div class="health-top"><span class="health-label">Data Quality</span>{status_badge(issue_status)}</div>
          <div class="health-value">{escape(issue_text)} detected issues</div>
          <div class="health-detail">Full evidence available in Data Quality</div>
        </div>
        """
    )
    health_html = f'<div class="health-grid">{"".join(cards)}</div>'.replace("\n", "")
    st.html(health_html)


def render_section_heading(title: str, description: str, eyebrow: str | None = None) -> None:
    eyebrow_html = f'<div class="eyebrow">{escape(eyebrow)}</div>' if eyebrow else ""
    st.html(
        f'<div class="section-heading">{eyebrow_html}<h2>{escape(title)}</h2><p>{escape(description)}</p></div>',
    )


def render_metric_grid(
    metric_index: dict[str, dict[str, Any]],
    metric_keys: list[str],
) -> None:
    cards = []
    for metric_key in metric_keys:
        metric = metric_index.get(metric_key)
        if not metric:
            label = metric_key.replace("_", " ").title()
            cards.append(
                f'<div class="metric-card"><div class="metric-label">{escape(label)}</div>'
                '<div class="metric-value">N/A</div><div class="metric-foot">Metric unavailable for this run</div></div>'
            )
            continue

        delta = format_metric_delta(metric)
        prior = format_comparison_value(metric)
        note = metric.get("calculation_note")
        warning = str(metric.get("calculation_status") or "").lower() in {"warning", "not_available"}
        foot_parts = []
        if delta:
            foot_parts.append(f'<span class="metric-delta">{escape(delta)}</span>')
        if prior:
            foot_parts.append(f'<span class="metric-prior">Prior {escape(prior)}</span>')
        if not foot_parts:
            foot_parts.append('<span class="metric-prior">No comparison available</span>')
        if warning and note:
            foot_parts.append(f'<span class="metric-note" title="{escape(str(note), quote=True)}">Calculation note</span>')

        cards.append(
            f"""
            <div class="metric-card{' warning' if warning else ''}" title="{escape(str(note or ''), quote=True)}">
              <div class="metric-label">{escape(str(metric.get('metric_label') or metric_key))}</div>
              <div class="metric-value">{escape(format_metric_value(metric))}</div>
              <div class="metric-foot">{' · '.join(foot_parts)}</div>
            </div>
            """
        )

    metric_html = f'<div class="metric-grid">{"".join(cards)}</div>'.replace("\n", "")
    st.html(metric_html)


def render_callout(kind: str, title: str, message: str) -> None:
    kind = kind if kind in {"info", "warning", "error", "success"} else "info"
    st.html(
        f'<div class="callout callout-{kind}"><strong>{escape(title)}</strong>{escape(message)}</div>',
    )
