"""Tests for loading and validating earnings CSV files."""

from pathlib import Path

import pandas as pd
import pytest

from uber_earnings_analyzer.data_loader import (
    EarningsDataError,
    load_earnings_csv,
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