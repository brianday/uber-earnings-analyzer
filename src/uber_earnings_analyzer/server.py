"""MCP server exposing Uber earnings analysis tools."""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from uber_earnings_analyzer.analyzer import (
    earnings_by_day,
    earnings_by_hour,
)
from uber_earnings_analyzer.data_loader import load_earnings_csv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "sample" / "sample_earnings.csv"

mcp = FastMCP(
    "Uber Earnings Analyzer",
    instructions=(
        "Use these tools to analyze Uber trip earnings by date and "
        "hour. Monetary values are in US dollars."
    ),
)


@mcp.tool()
def get_earnings_by_day() -> list[dict[str, object]]:
    """Return daily earnings totals and trip counts.

    Results are ordered from the most profitable day to the least
    profitable day.
    """
    dataframe = load_earnings_csv(DEFAULT_CSV_PATH)
    return earnings_by_day(dataframe)


@mcp.tool()
def get_earnings_by_hour() -> list[dict[str, object]]:
    """Return earnings statistics grouped by hour of day.

    Hours use a 24-hour clock. Results are ordered from the highest
    total earnings to the lowest.
    """
    dataframe = load_earnings_csv(DEFAULT_CSV_PATH)
    return earnings_by_hour(dataframe)


def main() -> None:
    """Run the MCP server using the standard input/output transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()