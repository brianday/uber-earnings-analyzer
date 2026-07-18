"""Tests for loading and validating earnings CSV files."""

from pathlib import Path

import pandas as pd
import pytest

from uber_earnings_analyzer.data_loader import (
    EarningsDataError,
    load_earnings_csv,
    load_uber_payments_csv,
)


SAMPLE_CSV = Path("data/sample/sample_earnings.csv")


def test_load_valid_sample_csv() -> None:
    """The sample CSV should load with normalized data types."""
    dataframe = load_earnings_csv(SAMPLE_CSV)

    assert len(dataframe) == 21
    assert list(dataframe.columns) == ["trip_datetime", "earnings"]
    assert pd.api.types.is_datetime64_any_dtype(
        dataframe["trip_datetime"]
    )
    assert pd.api.types.is_float_dtype(dataframe["earnings"])


def test_missing_file_raises_clear_error() -> None:
    """A missing CSV should raise our custom validation error."""
    with pytest.raises(
        EarningsDataError,
        match="CSV file does not exist",
    ):
        load_earnings_csv("data/raw/does-not-exist.csv")


def test_missing_required_column_is_rejected(
    tmp_path: Path,
) -> None:
    """A CSV without the earnings column should be rejected."""
    invalid_csv = tmp_path / "missing-column.csv"
    invalid_csv.write_text(
        "trip_datetime\n2026-07-17 08:00\n",
        encoding="utf-8",
    )

    with pytest.raises(
        EarningsDataError,
        match="missing required columns: earnings",
    ):
        load_earnings_csv(invalid_csv)

def test_load_uber_payments_groups_components_by_trip(
    tmp_path: Path,
) -> None:
    """Payment components should be summed into one net row per trip."""
    payments_csv = tmp_path / "driver-payments.csv"

    payments_csv.write_text(
        (
            "Trip UUID,Local Amount,Currency Code,Local Timestamp\n"
            "trip-1,10.00,USD,2026-07-17 08:00:00\n"
            "trip-1,-2.50,USD,2026-07-17 08:00:00\n"
            "trip-1,3.00,USD,2026-07-17 08:00:00\n"
            "trip-2,8.25,USD,2026-07-17 09:00:00\n"
            "trip-2,2.00,USD,2026-07-17 09:00:00\n"
        ),
        encoding="utf-8",
    )

    dataframe = load_uber_payments_csv(payments_csv)

    assert len(dataframe) == 2

    assert dataframe.iloc[0]["trip_datetime"] == pd.Timestamp(
        "2026-07-17 08:00:00"
    )
    assert dataframe.iloc[0]["earnings"] == 10.50

    assert dataframe.iloc[1]["trip_datetime"] == pd.Timestamp(
        "2026-07-17 09:00:00"
    )
    assert dataframe.iloc[1]["earnings"] == 10.25


def test_uber_payments_rejects_non_usd_currency(
    tmp_path: Path,
) -> None:
    """The initial version should reject unsupported currencies."""
    payments_csv = tmp_path / "non-usd-payments.csv"

    payments_csv.write_text(
        (
            "Trip UUID,Local Amount,Currency Code,Local Timestamp\n"
            "trip-1,10.00,CAD,2026-07-17 08:00:00\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        EarningsDataError,
        match="must contain only USD records",
    ):
        load_uber_payments_csv(payments_csv)


def test_uber_payments_rejects_inconsistent_trip_timestamps(
    tmp_path: Path,
) -> None:
    """Components for one trip must share the same timestamp."""
    payments_csv = tmp_path / "inconsistent-times.csv"

    payments_csv.write_text(
        (
            "Trip UUID,Local Amount,Currency Code,Local Timestamp\n"
            "trip-1,10.00,USD,2026-07-17 08:00:00\n"
            "trip-1,-2.00,USD,2026-07-17 08:05:00\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        EarningsDataError,
        match="inconsistent timestamps",
    ):
        load_uber_payments_csv(payments_csv)