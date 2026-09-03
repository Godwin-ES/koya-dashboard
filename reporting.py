from __future__ import annotations

from datetime import date
from typing import Any

import requests
from supabase import Client


VALID_PERIOD_TYPES = {
    "last_30_days",
    "last_90_days",
    "year_to_date",
    "custom",
}

REFERENCE_DATE = date(2026, 6, 30)
MIN_SOURCE_DATE = date(2025, 1, 1)


# =========================================================
# Report request / workflow
# =========================================================


def build_report_payload(
    period_type: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict[str, Any]:

    if period_type not in VALID_PERIOD_TYPES:
        raise ValueError(
            f"Unsupported period type: {period_type}"
        )

    payload: dict[str, Any] = {
        "period_type": period_type,
    }

    if period_type == "custom":

        if start_date is None or end_date is None:
            raise ValueError(
                "Custom reporting requires both "
                "start_date and end_date."
            )

        if start_date > end_date:
            raise ValueError(
                "Custom start date cannot be after end date."
            )

        if start_date < MIN_SOURCE_DATE:
            raise ValueError(
                "Custom start date cannot be earlier than "
                f"{MIN_SOURCE_DATE.isoformat()}."
            )

        if end_date > REFERENCE_DATE:
            raise ValueError(
                "Custom end date cannot be later than "
                f"{REFERENCE_DATE.isoformat()}."
            )

        payload["start_date"] = start_date.isoformat()
        payload["end_date"] = end_date.isoformat()

    return payload


def trigger_report(
    webhook_url: str,
    payload: dict[str, Any],
    timeout_seconds: int = 90,
) -> dict[str, Any]:

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=timeout_seconds,
        )
    except requests.Timeout as exc:
        raise RuntimeError(
            "The reporting workflow took too long to respond. "
            "The current report has been preserved; try again shortly."
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(
            "The reporting workflow could not be reached. "
            "Check the connection and try again."
        ) from exc

    try:
        body = response.json()

    except ValueError as exc:
        raise RuntimeError(
            "n8n returned a non-JSON response."
        ) from exc

    if not response.ok:
        error_message = (
            body.get("error_message")
            or body.get("message")
            or (
                "n8n request failed with HTTP "
                f"{response.status_code}."
            )
        )

        raise RuntimeError(error_message)

    return body


# =========================================================
# Supabase reads
# =========================================================


def fetch_report_run(
    supabase: Client,
    run_id: str,
) -> dict[str, Any]:

    response = (
        supabase
        .table("report_runs")
        .select("*")
        .eq("id", run_id)
        .limit(1)
        .execute()
    )

    rows = response.data or []

    if not rows:
        raise RuntimeError(
            f"No report run found for run_id {run_id}."
        )

    return rows[0]


def fetch_latest_completed_run(
    supabase: Client,
) -> dict[str, Any] | None:

    response = (
        supabase
        .table("report_runs")
        .select("*")
        .in_(
            "status",
            ["completed", "partial"],
        )
        .order(
            "completed_at",
            desc=True,
        )
        .limit(1)
        .execute()
    )

    rows = response.data or []

    return rows[0] if rows else None


def fetch_kpi_metrics(
    supabase: Client,
    run_id: str,
    department: str | None = None,
) -> list[dict[str, Any]]:

    query = (
        supabase
        .table("kpi_metrics")
        .select("*")
        .eq("run_id", run_id)
    )

    if department:
        query = query.eq(
            "department",
            department,
        )

    response = (
        query
        .order("metric_key")
        .execute()
    )

    return response.data or []


def fetch_ai_insight(
    supabase: Client,
    run_id: str,
) -> dict[str, Any] | None:
    """
    Return the AI insight for a report run.

    A missing row is valid for partial reports where
    deterministic KPIs succeeded but AI generation failed.
    """

    response = (
        supabase
        .table("ai_insights")
        .select("*")
        .eq("run_id", run_id)
        .limit(1)
        .execute()
    )

    rows = response.data or []

    return rows[0] if rows else None


def fetch_data_quality_issues(
    supabase: Client,
    run_id: str,
) -> list[dict[str, Any]]:

    response = (
        supabase
        .table("data_quality_issues")
        .select("*")
        .eq("run_id", run_id)
        .execute()
    )

    return response.data or []


# =========================================================
# Metric preparation
# =========================================================


def index_scalar_metrics(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:

    return {
        row["metric_key"]: row
        for row in rows
        if not row.get("dimension_name")
        and not row.get("dimension_value")
    }


def filter_dimension_metrics(
    rows: list[dict[str, Any]],
    metric_key: str,
) -> list[dict[str, Any]]:

    return [
        row
        for row in rows
        if (
            row.get("metric_key") == metric_key
            and row.get("dimension_value")
        )
    ]


# =========================================================
# AI / data-quality preparation
# =========================================================


def extract_ai_data_quality_warnings(
    ai_insight: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Extract the executive-level data quality warnings
    selected by the model from raw_response.
    """

    if not ai_insight:
        return []

    raw_response = (
        ai_insight.get("raw_response")
        or {}
    )

    warnings = raw_response.get(
        "data_quality_warnings"
    )

    return (
        warnings
        if isinstance(warnings, list)
        else []
    )


def sort_data_quality_issues(
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Sort errors before warnings while preserving
    deterministic ordering within each severity.
    """

    severity_order = {
        "error": 0,
        "warning": 1,
        "info": 2,
    }

    return sorted(
        issues,
        key=lambda row: (
            severity_order.get(
                str(
                    row.get(
                        "severity",
                        ""
                    )
                ).lower(),
                99,
            ),
            str(row.get("source", "")),
            str(
                row.get(
                    "source_record_id",
                    ""
                )
            ),
        ),
    )


# =========================================================
# Display formatting
# =========================================================


def _format_decimal(
    value: float,
    decimal_places: int = 2,
) -> str:

    text = (
        f"{value:,.{decimal_places}f}"
    )

    if "." in text:
        text = (
            text
            .rstrip("0")
            .rstrip(".")
        )

    return text


def _format_signed_number(
    value: float,
    decimal_places: int = 2,
) -> str:

    sign = "+" if value > 0 else ""

    return (
        f"{sign}"
        f"{_format_decimal(value, decimal_places)}"
    )


def format_metric_value(
    metric: dict[str, Any],
) -> str:

    value = metric.get("metric_value")
    unit = metric.get("metric_unit")

    if value is None:
        return "N/A"

    value = float(value)

    if unit == "count":

        if value.is_integer():
            return f"{int(value):,}"

        return _format_decimal(value)

    if unit == "currency":
        # Currency denomination is not supplied
        # by the project data, so no symbol is invented.
        return _format_decimal(value)

    if unit == "percent":
        return (
            f"{_format_decimal(value)}%"
        )

    if unit == "days":
        return (
            f"{_format_decimal(value)} days"
        )

    return _format_decimal(value)


def format_metric_delta(
    metric: dict[str, Any],
) -> str | None:

    comparison_value = metric.get(
        "comparison_value"
    )

    if comparison_value is None:
        return None

    unit = metric.get("metric_unit")

    absolute_change = metric.get(
        "absolute_change"
    )

    percent_change = metric.get(
        "percent_change"
    )

    # Percentage KPI:
    # show percentage-point movement.
    if (
        unit == "percent"
        and absolute_change is not None
    ):
        change = float(absolute_change)

        return (
            f"{_format_signed_number(change)} "
            "pp vs prior"
        )

    # Other KPIs:
    # prefer stored relative change.
    if percent_change is not None:
        change = float(percent_change)

        return (
            f"{_format_signed_number(change)}% "
            "vs prior"
        )

    # Percent change may intentionally be null
    # when the prior value is zero or for
    # signed zero-crossing metrics.
    if absolute_change is None:
        return None

    change = float(absolute_change)

    if unit == "count":

        if change.is_integer():

            signed = (
                f"+{int(change)}"
                if change > 0
                else str(int(change))
            )

        else:
            signed = (
                _format_signed_number(
                    change
                )
            )

        return (
            f"{signed} vs prior"
        )

    if unit == "days":
        return (
            f"{_format_signed_number(change)} "
            "days vs prior"
        )

    return (
        f"{_format_signed_number(change)} "
        "vs prior"
    )


def format_comparison_value(
    metric: dict[str, Any],
) -> str | None:
    """Format the persisted comparison value without deriving a new one."""

    comparison_value = metric.get("comparison_value")

    if comparison_value is None:
        return None

    comparison_metric = {
        "metric_value": comparison_value,
        "metric_unit": metric.get("metric_unit"),
    }

    return format_metric_value(comparison_metric)
