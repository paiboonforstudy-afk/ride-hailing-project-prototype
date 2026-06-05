"""
Upload historical data files to Azure Data Lake Storage Gen2.

Scans the local 'data/historical_data/' directory and uploads selected
CSV and JSON files to the ADLS historical data prefix.

Credentials are loaded from environment variables or a '.env' file.

Required environment variables:
    AZURE_STORAGE_CONNECTION_STRING : Azure Storage Account connection string
    STORAGE_ACCOUNT_CONTAINER_NAME  : Target ADLS container name

Usage:
    # Upload all files
    python upload_historical.py

    # Upload specific files by name
    python upload_historical.py --files historical_20260101_20260201.csv historical_20260201_20260301.csv

    # Upload files whose start date falls within a date range (inclusive)
    python upload_historical.py --from-date 20260101 --to-date 20260401
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from azure.storage.blob import BlobServiceClient

from config.storage import (
    AZURE_STORAGE_CONNECTION_STRING,
    ADLS_CONTAINER_NAME,
    ADLS_HISTORICAL_PREFIX,
    HISTORICAL_DATA_DIR,
)

# Matches filenames like: historical_20260101_20260201.csv / .json
_FILENAME_PATTERN = re.compile(r"^historical_(\d{8})_(\d{8})\.(csv|json)$")
_DATE_FMT         = "%Y%m%d"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

def _build_client() -> BlobServiceClient:
    """
    Create a BlobServiceClient using credentials from the environment.

    Raises:
        EnvironmentError: If AZURE_STORAGE_CONNECTION_STRING is not set.
    """
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise EnvironmentError(
            "Missing required environment variable.\n"
            "Ensure AZURE_STORAGE_CONNECTION_STRING is set in your .env file."
        )
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


# ---------------------------------------------------------------------------
# File selection
# ---------------------------------------------------------------------------

def _all_local_files() -> list[Path]:
    """Return all .csv and .json files in the historical data directory."""
    return [f for f in HISTORICAL_DATA_DIR.iterdir() if f.suffix in (".csv", ".json")]


def _select_by_names(names: list[str]) -> list[Path]:
    """
    Return local Path objects for the requested filenames.
    Prints a warning for any name not found locally.
    """
    selected = []
    for name in names:
        path = HISTORICAL_DATA_DIR / name
        if path.exists():
            selected.append(path)
        else:
            print(f"  [WARNING] File not found locally, skipping: {name}")
    return selected


def _select_by_date_range(from_date: datetime, to_date: datetime) -> list[Path]:
    """
    Return files whose embedded start date falls within [from_date, to_date] inclusive.
    Files that do not match the expected naming convention are skipped with a warning.
    """
    selected = []
    for f in _all_local_files():
        match = _FILENAME_PATTERN.match(f.name)
        if not match:
            print(f"  [WARNING] Filename does not match expected pattern, skipping: {f.name}")
            continue

        file_start = datetime.strptime(match.group(1), _DATE_FMT)
        if from_date <= file_start <= to_date:
            selected.append(f)

    return sorted(selected)


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

def _upload(files: list[Path]) -> None:
    """Upload the given list of local files to ADLS."""
    if not files:
        print("No files matched the selection criteria.")
        return

    client    = _build_client()
    container = client.get_container_client(ADLS_CONTAINER_NAME)

    print(f"Uploading {len(files)} file(s) to {ADLS_CONTAINER_NAME}/{ADLS_HISTORICAL_PREFIX}/")

    for file in files:
        blob_name = f"{ADLS_HISTORICAL_PREFIX}/{file.name}"
        with open(file, "rb") as data:
            container.upload_blob(name=blob_name, data=data, overwrite=True)
        print(f"  Uploaded: {file.name}")

    print("Done.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload historical ride data files to ADLS Gen2.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Upload all files:
    python upload_historical.py

  Upload specific files:
    python upload_historical.py --files historical_20260101_20260201.csv

  Upload files within a date range:
    python upload_historical.py --from-date 20260101 --to-date 20260401
        """,
    )

    parser.add_argument(
        "--files",
        nargs  = "+",
        metavar= "FILENAME",
        help   = "One or more specific filenames to upload (e.g. historical_20260101_20260201.csv).",
    )
    parser.add_argument(
        "--from-date",
        metavar = "YYYYMMDD",
        help    = "Start of date range filter (inclusive). Requires --to-date.",
    )
    parser.add_argument(
        "--to-date",
        metavar = "YYYYMMDD",
        help    = "End of date range filter (inclusive). Requires --from-date.",
    )

    args = parser.parse_args()

    # Mutual inclusion: --from-date and --to-date must be used together.
    if bool(args.from_date) ^ bool(args.to_date):
        parser.error("--from-date and --to-date must be used together.")

    return args


def run() -> None:
    args = _parse_args()

    all_files = _all_local_files()
    if not all_files:
        print(f"No historical data files found in {HISTORICAL_DATA_DIR}.")
        return

    # --- Determine which files to upload ---
    if args.files:
        # Mode: explicit file selection
        files = _select_by_names(args.files)

    elif args.from_date and args.to_date:
        # Mode: date range selection
        try:
            from_dt = datetime.strptime(args.from_date, _DATE_FMT)
            to_dt   = datetime.strptime(args.to_date,   _DATE_FMT)
        except ValueError:
            print("Error: Dates must be in YYYYMMDD format (e.g. 20260101).")
            sys.exit(1)

        if from_dt > to_dt:
            print("Error: --from-date must be earlier than or equal to --to-date.")
            sys.exit(1)

        files = _select_by_date_range(from_dt, to_dt)

    else:
        # Mode: default — upload everything
        files = sorted(all_files)

    _upload(files)


if __name__ == "__main__":
    run()
