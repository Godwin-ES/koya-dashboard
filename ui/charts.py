from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd
import streamlit as st


def render_dimension_chart(
    rows: list[dict[str, Any]],
    category_label: str,
    value_label: str,
    unit: str,
    accent: str,
) -> None:
    data = [
        {
            category_label: row.get("dimension_value"),
            value_label: float(row["metric_value"]),
        }
        for row in rows
        if row.get("dimension_value") and row.get("metric_value") is not None
    ]
    if not data:
        st.info("No dimensional breakdown is available for this reporting period.")
        return

    frame = pd.DataFrame(data).sort_values(value_label, ascending=True)
    height = max(250, min(390, 58 * len(frame)))
    tooltip_format = ",.0f" if unit == "count" else ",.2f"

    chart = (
        alt.Chart(frame)
        .mark_bar(cornerRadiusEnd=5, color=accent, size=22)
        .encode(
            y=alt.Y(
                f"{category_label}:N",
                sort=alt.EncodingSortField(field=value_label, order="descending"),
                title=None,
                axis=alt.Axis(labelColor="#405866", labelFontSize=12, labelLimit=170, ticks=False, domain=False),
            ),
            x=alt.X(
                f"{value_label}:Q",
                title=value_label,
                scale=alt.Scale(zero=True),
                axis=alt.Axis(format="~s", gridColor="#e8eef1", titleColor="#6b7d87", labelColor="#6b7d87"),
            ),
            tooltip=[
                alt.Tooltip(f"{category_label}:N", title=category_label),
                alt.Tooltip(f"{value_label}:Q", title=value_label, format=tooltip_format),
            ],
        )
        .properties(height=height)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, width="stretch")
