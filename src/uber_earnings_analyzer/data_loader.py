"""Functions for loading and validating Uber earnings data."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"trip_datetime", "earnings"}

UBER_PAYMENT_COLUMNS = {
    "Trip UUID",
    "Local Amount",
    "Currency Code",
    "Local Timestamp",
}


class EarningsDataError(ValueError):
    """Raised when an earnings CSV file is missing or invalid."""


def load_earnings_csv(csv_path: str | Path) -> pd.DataFrame:
    """Load and validate a normalized earnings CSV file.

    Args:
        csv_path: Location of the CSV file.

    Returns:
        A cleaned pandas DataFrame containing trip datetimes and earnings.

    Raises:
        EarningsDataError: If the file is missing, unreadable, or invalid.
    """
    path = Path(csv_path)

    if not path.exists():
        raise EarningsDataError(f"CSV file does not exist: {path}")

    if not path.is_file():
        raise EarningsDataError(f"CSV path is not a file: {path}")

    try:
        dataframe = pd.read_csv(path)
    except (OSError, pd.errors.ParserError) as error:
        raise EarningsDataError(
            f"Could not read CSV file: {path}"
        ) from error

    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise EarningsDataError(
            f"CSV is missing required columns: {missing}"
        )

    cleaned = dataframe.loc[:, ["trip_datetime", "earnings"]].copy()

    cleaned["trip_datetime"] = pd.to_datetime(
        cleaned["trip_datetime"],
        errors="coerce",
    )

    cleaned["earnings"] = pd.to_numeric(
        cleaned["earnings"],
        errors="coerce",
    )

    invalid_rows = cleaned[
        cleaned["trip_datetime"].isna() | cleaned["earnings"].isna()
    ]

    if not invalid_rows.empty:
        raise EarningsDataError(
            f"CSV contains {len(invalid_rows)} row(s) with invalid "
            "dates or earnings values."
        )

    if cleaned.empty:
        raise EarningsDataError("CSV file contains no earnings records.")

    return cleaned.sort_values("trip_datetime").reset_index(drop=True)


def load_uber_payments_csv(csv_path: str | Path) -> pd.DataFrame:
    """Load an Uber payments export and aggregate it by trip.

    Uber stores each fare, fee, tip, incentive, and adjustment as a
    separate payment component. All components sharing a Trip UUID are
    summed to calculate the driver's net earnings for that trip.

    Args:
        csv_path: Location of Uber's driver payments CSV export.

    Returns:
        A DataFrame with one row per trip containing ``trip_datetime``
        and ``earnings``.

    Raises:
        EarningsDataError: If the file is missing, malformed, uses an
            unsupported currency, or contains invalid values.
    """
    path = Path(csv_path)

    if not path.exists():
        raise EarningsDataError(f"CSV file does not exist: {path}")

    if not path.is_file():
        raise EarningsDataError(f"CSV path is not a file: {path}")

    try:
        dataframe = pd.read_csv(path)
    except (OSError, pd.errors.ParserError) as error:
        raise EarningsDataError(
            f"Could not read CSV file: {path}"
        ) from error

    missing_columns = UBER_PAYMENT_COLUMNS - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise EarningsDataError(
            f"Uber payments CSV is missing required columns: {missing}"
        )

    if dataframe.empty:
        raise EarningsDataError(
            "Uber payments CSV contains no payment records."
        )

    working_data = dataframe.loc[
        :,
        [
            "Trip UUID",
            "Local Amount",
            "Currency Code",
            "Local Timestamp",
        ],
    ].copy()

    working_data["Local Timestamp"] = pd.to_datetime(
        working_data["Local Timestamp"],
        errors="coerce",
    )

    working_data["Local Amount"] = pd.to_numeric(
        working_data["Local Amount"],
        errors="coerce",
    )

    invalid_rows = working_data[
        working_data["Trip UUID"].isna()
        | working_data["Local Timestamp"].isna()
        | working_data["Local Amount"].isna()
    ]

    if not invalid_rows.empty:
        raise EarningsDataError(
            f"Uber payments CSV contains {len(invalid_rows)} row(s) "
            "with missing or invalid trip IDs, timestamps, or amounts."
        )

    currencies = set(
        working_data["Currency Code"].dropna().astype(str).str.upper()
    )

    if currencies != {"USD"}:
        currencies_text = ", ".join(sorted(currencies)) or "none"
        raise EarningsDataError(
            "Uber payments CSV must contain only USD records. "
            f"Found: {currencies_text}"
        )

    timestamp_counts = working_data.groupby("Trip UUID")[
        "Local Timestamp"
    ].nunique()

    inconsistent_trip_count = int((timestamp_counts > 1).sum())

    if inconsistent_trip_count:
        raise EarningsDataError(
            f"Uber payments CSV contains {inconsistent_trip_count} "
            "trip(s) with inconsistent timestamps."
        )

    grouped = (
        working_data.groupby("Trip UUID", as_index=False)
        .agg(
            trip_datetime=("Local Timestamp", "first"),
            earnings=("Local Amount", "sum"),
        )
        .loc[:, ["trip_datetime", "earnings"]]
    )

    grouped["earnings"] = grouped["earnings"].round(2)

    return grouped.sort_values("trip_datetime").reset_index(drop=True)