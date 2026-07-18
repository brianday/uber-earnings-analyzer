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

def compare_latest_two_weeks(
    dataframe: pd.DataFrame,
) -> dict[str, object]:
    """Compare the latest calendar week with the preceding week.

    The latest timestamp in the dataset determines the current week.
    Weeks run from Monday through Sunday.

    Args:
        dataframe: Cleaned earnings data from the CSV loader.

    Returns:
        Earnings totals, trip counts, and changes for the two weeks.
    """
    latest_timestamp = dataframe["trip_datetime"].max()

    current_week_start = (
        latest_timestamp.normalize()
        - pd.Timedelta(days=latest_timestamp.weekday())
    )
    next_week_start = current_week_start + pd.Timedelta(days=7)
    previous_week_start = current_week_start - pd.Timedelta(days=7)

    current_week_data = dataframe[
        (dataframe["trip_datetime"] >= current_week_start)
        & (dataframe["trip_datetime"] < next_week_start)
    ]

    previous_week_data = dataframe[
        (dataframe["trip_datetime"] >= previous_week_start)
        & (dataframe["trip_datetime"] < current_week_start)
    ]

    current_total = round(
        float(current_week_data["earnings"].sum()),
        2,
    )
    previous_total = round(
        float(previous_week_data["earnings"].sum()),
        2,
    )
    earnings_change = round(current_total - previous_total, 2)

    percentage_change = None

    if previous_total != 0:
        percentage_change = round(
            (earnings_change / previous_total) * 100,
            2,
        )

    return {
        "current_week": {
            "start_date": current_week_start.date().isoformat(),
            "end_date": (
                next_week_start - pd.Timedelta(days=1)
            ).date().isoformat(),
            "total_earnings": current_total,
            "trip_count": len(current_week_data),
        },
        "previous_week": {
            "start_date": previous_week_start.date().isoformat(),
            "end_date": (
                current_week_start - pd.Timedelta(days=1)
            ).date().isoformat(),
            "total_earnings": previous_total,
            "trip_count": len(previous_week_data),
        },
        "earnings_change": earnings_change,
        "percentage_change": percentage_change,
    }