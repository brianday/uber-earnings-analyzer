"""MCP server exposing Uber earnings analysis tools."""

import os
from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP

from uber_earnings_analyzer.analyzer import (
    compare_latest_two_weeks,
    earnings_by_day,
    earnings_by_hour,
    weekly_earnings_trend,
)
from uber_earnings_analyzer.data_loader import (
    load_earnings_csv,
    load_uber_payments_csv,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_CSV_PATH = (
    PROJECT_ROOT / "data" / "sample" / "sample_earnings.csv"
)

mcp = FastMCP(
    "Uber Earnings Analyzer",
    instructions=(
        "Use these tools to analyze Uber trip earnings by date and "
        "hour and to compare recent weeks. Monetary values are in "
        "US dollars."
    ),
)


def get_configured_earnings_data() -> pd.DataFrame:
    """Load either a private Uber export or the public sample data.

    When UBER_EARNINGS_CSV is set, the referenced Uber payments export
    is loaded and aggregated by trip. Otherwise, the bundled normalized
    sample CSV is used.
    """
    configured_path = os.getenv("UBER_EARNINGS_CSV")

    if configured_path:
        return load_uber_payments_csv(configured_path)

    return load_earnings_csv(SAMPLE_CSV_PATH)


@mcp.tool()
def get_earnings_by_day() -> list[dict[str, object]]:
    """Return daily earnings totals and trip counts.

    Results are ordered from the most profitable day to the least
    profitable day.
    """
    dataframe = get_configured_earnings_data()
    return earnings_by_day(dataframe)


@mcp.tool()
def get_earnings_by_hour() -> list[dict[str, object]]:
    """Return earnings statistics grouped by hour of day.

    Hours use a 24-hour clock. Results are ordered from the highest
    total earnings to the lowest.
    """
    dataframe = get_configured_earnings_data()
    return earnings_by_hour(dataframe)


@mcp.tool()
def compare_weeks() -> dict[str, object]:
    """Compare the latest calendar week with the previous week.

    Weeks run from Monday through Sunday. The latest trip date in the
    dataset determines which week is treated as the current week.
    """
    dataframe = get_configured_earnings_data()
    return compare_latest_two_weeks(dataframe)

@mcp.tool()
def get_weekly_earnings_trend(
    weeks: int = 8,
) -> list[dict[str, object]]:
    """Return earnings trends for the most recent calendar weeks.

    Weeks run from Monday through Sunday. Results are chronological and
    include earnings totals, trip counts, dollar changes, and percentage
    changes from the preceding returned week.

    Args:
        weeks: Number of recent weeks to return. Must be at least 1.
    """
    dataframe = get_configured_earnings_data()
    return weekly_earnings_trend(dataframe, weeks=weeks)


def main() -> None:
    """Run the MCP server using the standard input/output transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()