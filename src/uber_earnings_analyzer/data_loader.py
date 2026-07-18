"""Functions for loading and validating Uber earnings data."""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"trip_datetime", "earnings"}


class EarningsDataError(ValueError):
    """Raised when an earnings CSV file is missing or invalid."""


def load_earnings_csv(csv_path: str | Path) -> pd.DataFrame:
    """Load and validate an Uber earnings CSV file.

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