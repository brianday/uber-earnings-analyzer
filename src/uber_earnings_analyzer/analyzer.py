"""Calculations for analyzing Uber earnings data."""

import pandas as pd


def earnings_by_day(dataframe: pd.DataFrame) -> list[dict[str, object]]:
    """Calculate total earnings and trip counts for each calendar day.

    Args:
        dataframe: Cleaned earnings data from the CSV loader.

    Returns:
        Daily results ordered from highest to lowest earnings.
    """
    working_data = dataframe.copy()
    working_data["date"] = working_data["trip_datetime"].dt.date

    daily_summary = (
        working_data.groupby("date", as_index=False)
        .agg(
            total_earnings=("earnings", "sum"),
            trip_count=("earnings", "size"),
        )
        .sort_values("total_earnings", ascending=False)
    )

    daily_summary["total_earnings"] = daily_summary[
        "total_earnings"
    ].round(2)

    return daily_summary.to_dict(orient="records")


def earnings_by_hour(dataframe: pd.DataFrame) -> list[dict[str, object]]:
    """Calculate total and average earnings by hour of day.

    Args:
        dataframe: Cleaned earnings data from the CSV loader.

    Returns:
        Hourly results ordered from highest to lowest total earnings.
    """
    working_data = dataframe.copy()
    working_data["hour"] = working_data["trip_datetime"].dt.hour

    hourly_summary = (
        working_data.groupby("hour", as_index=False)
        .agg(
            total_earnings=("earnings", "sum"),
            average_trip_earnings=("earnings", "mean"),
            trip_count=("earnings", "size"),
        )
        .sort_values("total_earnings", ascending=False)
    )

    hourly_summary["total_earnings"] = hourly_summary[
        "total_earnings"
    ].round(2)

    hourly_summary["average_trip_earnings"] = hourly_summary[
        "average_trip_earnings"
    ].round(2)

    return hourly_summary.to_dict(orient="records")