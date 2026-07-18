"""Tests for earnings analysis calculations."""

from pathlib import Path

import pytest

from uber_earnings_analyzer.analyzer import (
    compare_latest_two_weeks,
    earnings_by_day,
    earnings_by_hour,
)
from uber_earnings_analyzer.data_loader import load_earnings_csv


SAMPLE_CSV = Path("data/sample/sample_earnings.csv")


@pytest.fixture
def sample_data():
    """Load the public sample dataset for analyzer tests."""
    return load_earnings_csv(SAMPLE_CSV)


def test_earnings_by_day_ranks_highest_day_first(
    sample_data,
) -> None:
    """Daily results should be sorted by total earnings."""
    results = earnings_by_day(sample_data)

    assert len(results) == 10
    assert str(results[0]["date"]) == "2026-07-15"
    assert results[0]["total_earnings"] == 41.20
    assert results[0]["trip_count"] == 2


def test_earnings_by_hour_ranks_highest_hour_first(
    sample_data,
) -> None:
    """Hourly results should be sorted by total earnings."""
    results = earnings_by_hour(sample_data)

    assert len(results) == 6
    assert results[0]["hour"] == 9
    assert results[0]["total_earnings"] == 90.30
    assert results[0]["average_trip_earnings"] == 15.05
    assert results[0]["trip_count"] == 6

def test_compare_latest_two_weeks(sample_data) -> None:
    """The latest week should be compared with the prior week."""
    result = compare_latest_two_weeks(sample_data)

    assert result["current_week"] == {
        "start_date": "2026-07-13",
        "end_date": "2026-07-19",
        "total_earnings": 172.07,
        "trip_count": 11,
    }

    assert result["previous_week"] == {
        "start_date": "2026-07-06",
        "end_date": "2026-07-12",
        "total_earnings": 145.00,
        "trip_count": 10,
    }

    assert result["earnings_change"] == 27.07
    assert result["percentage_change"] == 18.67