from ui.components import format_timestamp


def test_formats_utc_timestamp_in_lagos_time():
    assert (
        format_timestamp("2026-09-04T11:52:00+00:00")
        == "04 Sep 2026 · 12:52 WAT"
    )


def test_treats_naive_backend_timestamp_as_utc():
    assert (
        format_timestamp("2026-09-04T11:52:00")
        == "04 Sep 2026 · 12:52 WAT"
    )


def test_invalid_timestamp_keeps_original_value():
    assert format_timestamp("not-a-timestamp") == "not-a-timestamp"
