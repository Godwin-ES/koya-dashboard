from __future__ import annotations

from datetime import date
from html import escape
from typing import Any, Callable

import streamlit as st
from supabase import create_client

from reporting import (
    MIN_SOURCE_DATE,
    REFERENCE_DATE,
    build_report_payload,
    fetch_ai_insight,
    fetch_data_quality_issues,
    fetch_kpi_metrics,
    fetch_latest_completed_run,
    fetch_report_run,
    index_scalar_metrics,
    trigger_report,
)
from ui.components import (
    format_date,
    render_callout,
    render_health_strip,
    render_report_header,
    status_badge,
)
from ui.sections import (
    render_data_quality,
    render_overview,
    render_people_operations,
    render_project_delivery,
    render_sales,
)
from ui.theme import inject_theme


st.set_page_config(
    page_title="Koya Operations Command Center",
    page_icon="◫",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()


@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_ANON_KEY"],
    )


def load_optional(
    label: str,
    loader: Callable[[], Any],
    fallback: Any,
    failures: list[str],
) -> Any:
    """Load a report section without allowing one read failure to blank the page."""
    try:
        return loader()
    except Exception:
        failures.append(label)
        return fallback


def render_sidebar_brand() -> None:
    st.html(
        """
        <div class="koya-brand">
          <div class="koya-mark">K</div>
          <div><strong>Koya Operations</strong><span>Reporting command center</span></div>
        </div>
        """,
    )


if "current_run_id" not in st.session_state:
    st.session_state.current_run_id = None
if "generation_notice" not in st.session_state:
    st.session_state.generation_notice = None


try:
    supabase = get_supabase()
    webhook_url = st.secrets["N8N_WEBHOOK_URL"]
except Exception:
    st.error(
        "Dashboard configuration is incomplete. Add SUPABASE_URL, "
        "SUPABASE_ANON_KEY, and N8N_WEBHOOK_URL to .streamlit/secrets.toml."
    )
    st.stop()


period_options = {
    "Last 30 Days": "last_30_days",
    "Last 90 Days": "last_90_days",
    "Year to Date": "year_to_date",
    "Custom Date Range": "custom",
}

with st.sidebar:
    render_sidebar_brand()
    st.html('<div class="sidebar-kicker">Generate a new report</div>')
    st.caption("Choose a period for the next workflow run. This does not change the report currently being viewed until generation succeeds.")

    selected_label = st.selectbox(
        "Reporting period",
        options=list(period_options),
        index=0,
    )
    period_type = period_options[selected_label]
    custom_start: date | None = None
    custom_end: date | None = None

    if period_type == "custom":
        custom_start = st.date_input(
            "Start date",
            value=date(2026, 5, 1),
            min_value=MIN_SOURCE_DATE,
            max_value=REFERENCE_DATE,
        )
        custom_end = st.date_input(
            "End date",
            value=date(2026, 6, 15),
            min_value=MIN_SOURCE_DATE,
            max_value=REFERENCE_DATE,
        )

    st.html(
        f'<div class="sidebar-note">Available data: {format_date(MIN_SOURCE_DATE)} – {format_date(REFERENCE_DATE)}<br>Reporting anchor: {format_date(REFERENCE_DATE)}</div>',
    )
    generate_clicked = st.button("Generate report", type="primary", width="stretch")


if generate_clicked:
    try:
        payload = build_report_payload(period_type, custom_start, custom_end)
        with st.spinner("Running the reporting workflow and persisting results…"):
            webhook_result = trigger_report(webhook_url, payload)
        returned_run_id = webhook_result.get("run_id")
        if not returned_run_id:
            raise RuntimeError("The workflow completed without returning a run ID.")
        st.session_state.current_run_id = returned_run_id
        st.session_state.generation_notice = {
            "status": webhook_result.get("status", "completed"),
            "message": webhook_result.get("warning") or webhook_result.get("message") or "Report generated.",
        }
    except Exception as exc:
        st.session_state.generation_notice = {
            "status": "error",
            "message": str(exc),
        }


current_run: dict[str, Any] | None = None
run_load_error: str | None = None
try:
    if st.session_state.current_run_id:
        current_run = fetch_report_run(supabase, st.session_state.current_run_id)
    else:
        current_run = fetch_latest_completed_run(supabase)
        if current_run:
            st.session_state.current_run_id = current_run["id"]
except Exception:
    run_load_error = "Supabase could not return the requested report. Check the connection and reporting-table access policy."


with st.sidebar:
    st.divider()
    st.html('<div class="sidebar-kicker">Currently viewing</div>')
    if current_run:
        st.html(
            f"""
            <div class="sidebar-current">
              <strong>{escape(str(current_run.get('period_label') or 'Operations Report'))}</strong><br>
              <span>{escape(format_date(current_run.get('period_start')))} – {escape(format_date(current_run.get('period_end')))}</span><br><br>
              {status_badge(current_run.get('status'))}
            </div>
            """,
        )
        with st.expander("Technical report details"):
            st.caption("Run ID")
            st.code(str(current_run.get("id")), language=None)
            st.caption(f"Period type · {current_run.get('period_type', '—')}")
            st.caption(f"Reference date · {current_run.get('reference_date', '—')}")
            st.caption(f"Started · {current_run.get('started_at', '—')}")
            st.caption(f"Completed · {current_run.get('completed_at', '—')}")
    else:
        st.html('<div class="sidebar-note">No completed or partial report is available yet.</div>')
    st.divider()
    st.html('<div class="sidebar-note">Supabase is the source of truth. KPI values are rendered from the selected persisted run and are never recalculated here.</div>')


notice = st.session_state.generation_notice
if notice:
    notice_status = str(notice.get("status") or "info").lower()
    notice_kind = "error" if notice_status == "error" else "warning" if notice_status == "partial" else "success"
    notice_title = "Report generation failed" if notice_status == "error" else "Report ready with limitations" if notice_status == "partial" else "Report ready"
    render_callout(notice_kind, notice_title, str(notice.get("message") or ""))
    st.session_state.generation_notice = None


if run_load_error:
    render_callout("error", "Unable to load reporting data", run_load_error)

if not current_run:
    st.html(
        """
        <div class="report-header">
          <div><div class="eyebrow">Operations command center</div><h1 class="report-title">No report available</h1>
          <div class="report-subtitle">Generate a reporting run from the sidebar to populate this workspace.</div></div>
        </div>
        """,
    )
    render_callout(
        "info",
        "Start with a reporting period",
        "The workflow will collect all three sources, calculate deterministic KPIs, persist the run in Supabase, and return the exact report for display.",
    )
    st.stop()


run_id = str(current_run["id"])
load_failures: list[str] = []
sales_metrics = load_optional(
    "Sales KPIs",
    lambda: fetch_kpi_metrics(supabase, run_id, "sales"),
    [],
    load_failures,
)
project_metrics = load_optional(
    "Project Delivery KPIs",
    lambda: fetch_kpi_metrics(supabase, run_id, "project_delivery"),
    [],
    load_failures,
)
people_metrics = load_optional(
    "People Operations KPIs",
    lambda: fetch_kpi_metrics(supabase, run_id, "people_ops"),
    [],
    load_failures,
)
ai_insight = load_optional(
    "AI analysis",
    lambda: fetch_ai_insight(supabase, run_id),
    None,
    load_failures,
)
dq_issues = load_optional(
    "Data Quality register",
    lambda: fetch_data_quality_issues(supabase, run_id),
    [],
    load_failures,
)

sales_index = index_scalar_metrics(sales_metrics)
project_index = index_scalar_metrics(project_metrics)
people_index = index_scalar_metrics(people_metrics)

render_report_header(current_run)
render_health_strip(current_run)

if load_failures:
    render_callout(
        "warning",
        "Some report sections are temporarily unavailable",
        f"Could not load: {', '.join(load_failures)}. Other persisted sections remain available.",
    )

overview_tab, sales_tab, project_tab, people_tab, quality_tab = st.tabs(
    ["Overview", "Sales", "Project Delivery", "People Ops", "Data Quality"]
)

with overview_tab:
    render_overview(current_run, sales_index, project_index, people_index, ai_insight)

with sales_tab:
    render_sales(sales_index, sales_metrics)

with project_tab:
    render_project_delivery(project_index, project_metrics)

with people_tab:
    render_people_operations(people_index, people_metrics)

with quality_tab:
    render_data_quality(current_run, dq_issues, ai_insight)
