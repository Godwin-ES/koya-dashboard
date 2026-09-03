from reporting import (
    build_report_payload,
    extract_ai_data_quality_warnings,
    filter_dimension_metrics,
    format_comparison_value,
    format_metric_delta,
    format_metric_value,
    index_scalar_metrics,
    sort_data_quality_issues,
)

from datetime import date

import pytest


def test_formats_count_without_decimal_places():

    metric = {
        "metric_value": 13,
        "metric_unit": "count",
    }

    assert (
        format_metric_value(metric)
        == "13"
    )


def test_formats_currency_without_symbol():

    metric = {
        "metric_value": 54000,
        "metric_unit": "currency",
    }

    assert (
        format_metric_value(metric)
        == "54,000"
    )


def test_formats_fractional_currency():

    metric = {
        "metric_value": 376.9231,
        "metric_unit": "currency",
    }

    assert (
        format_metric_value(metric)
        == "376.92"
    )


def test_formats_percentage():

    metric = {
        "metric_value": 62.5,
        "metric_unit": "percent",
    }

    assert (
        format_metric_value(metric)
        == "62.5%"
    )


def test_formats_days():

    metric = {
        "metric_value": 28.5,
        "metric_unit": "days",
    }

    assert (
        format_metric_value(metric)
        == "28.5 days"
    )


def test_percentage_metric_uses_pp_delta():

    metric = {
        "metric_unit": "percent",
        "comparison_value": 57.1429,
        "absolute_change": 5.3571,
        "percent_change": 9.3749,
    }

    assert (
        format_metric_delta(metric)
        == "+5.36 pp vs prior"
    )


def test_non_percentage_uses_relative_change():

    metric = {
        "metric_unit": "currency",
        "comparison_value": 44400,
        "absolute_change": 9600,
        "percent_change": 21.6216,
    }

    assert (
        format_metric_delta(metric)
        == "+21.62% vs prior"
    )


def test_zero_prior_falls_back_to_absolute():

    metric = {
        "metric_unit": "count",
        "comparison_value": 0,
        "absolute_change": 2,
        "percent_change": None,
    }

    assert (
        format_metric_delta(metric)
        == "+2 vs prior"
    )


def test_days_absolute_change_fallback():

    metric = {
        "metric_unit": "days",
        "comparison_value": 0,
        "absolute_change": 4.5,
        "percent_change": None,
    }

    assert (
        format_metric_delta(metric)
        == "+4.5 days vs prior"
    )


def test_missing_comparison_returns_none():

    metric = {
        "metric_unit": "count",
        "comparison_value": None,
        "absolute_change": None,
        "percent_change": None,
    }

    assert (
        format_metric_delta(metric)
        is None
    )


def test_formats_persisted_comparison_value():
    metric = {
        "metric_unit": "percent",
        "comparison_value": 57.1429,
    }

    assert format_comparison_value(metric) == "57.14%"


def test_missing_comparison_value_is_not_zero():
    assert format_comparison_value({"comparison_value": None}) is None


def test_custom_payload_respects_source_date_bounds():
    with pytest.raises(ValueError, match="2025-01-01"):
        build_report_payload(
            "custom",
            date(2024, 12, 31),
            date(2025, 1, 2),
        )

    with pytest.raises(ValueError, match="2026-06-30"):
        build_report_payload(
            "custom",
            date(2026, 6, 1),
            date(2026, 7, 1),
        )


def test_scalar_index_excludes_dimensions():

    rows = [
        {
            "metric_key":
                "total_leads",
            "dimension_name": "",
            "dimension_value": "",
            "metric_value": 13,
        },
        {
            "metric_key":
                "revenue_by_lead_source",
            "dimension_name":
                "lead_source",
            "dimension_value":
                "Inbound",
            "metric_value": 11400,
        },
    ]

    result = (
        index_scalar_metrics(rows)
    )

    assert (
        "total_leads"
        in result
    )

    assert (
        "revenue_by_lead_source"
        not in result
    )


def test_filter_dimension_metrics():

    rows = [
        {
            "metric_key":
                "delivery_load_by_team",
            "dimension_name": "team",
            "dimension_value":
                "AI Apps",
            "metric_value": 5,
        },
        {
            "metric_key":
                "completed_projects",
            "dimension_name": "",
            "dimension_value": "",
            "metric_value": 5,
        },
        {
            "metric_key":
                "delivery_load_by_team",
            "dimension_name": "team",
            "dimension_value":
                "Data",
            "metric_value": 4,
        },
    ]

    result = (
        filter_dimension_metrics(
            rows,
            "delivery_load_by_team",
        )
    )

    assert len(result) == 2

    assert {
        row["dimension_value"]
        for row in result
    } == {
        "AI Apps",
        "Data",
    }


def test_extracts_ai_data_quality_warnings():

    insight = {
        "raw_response": {
            "data_quality_warnings": [
                {
                    "source": "sales",
                    "warning":
                        "Invalid date.",
                    "impact":
                        "Period assignment unavailable.",
                }
            ]
        }
    }

    result = (
        extract_ai_data_quality_warnings(
            insight
        )
    )

    assert len(result) == 1

    assert (
        result[0]["source"]
        == "sales"
    )


def test_missing_ai_insight_has_no_warnings():

    assert (
        extract_ai_data_quality_warnings(
            None
        )
        == []
    )


def test_data_quality_errors_sort_before_warnings():

    issues = [
        {
            "severity": "warning",
            "source": "sales",
            "source_record_id": "B",
        },
        {
            "severity": "error",
            "source": "sales",
            "source_record_id": "A",
        },
    ]

    result = (
        sort_data_quality_issues(
            issues
        )
    )

    assert (
        result[0]["severity"]
        == "error"
    )
