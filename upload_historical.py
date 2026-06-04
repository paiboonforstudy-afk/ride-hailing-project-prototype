"""
Upload historical data files to Azure Data Lake Storage Gen2.

Scans the local 'data/historical_data/' directory and uploads all
CSV and JSON files to the 'historical_data/' folder in ADLS.

Credentials are loaded from environment variables or a '.env' file.

Required environment variables:
    AZURE_STORAGE_CONNECTION_STRING : Azure Storage Account connection string

Usage:
    python upload_historical.py
"""

from azure.storage.blob import BlobServiceClient

from config.storage import (
    AZURE_STORAGE_CONNECTION_STRING,
    ADLS_CONTAINER_NAME,
    ADLS_HISTORICAL_PREFIX,
    HISTORICAL_DATA_DIR,
)


def _build_client() -> BlobServiceClient:
    """
    Creates a Blob Service client using credentials from the environment.

    Raises:
        EnvironmentError: If AZURE_STORAGE_CONNECTION_STRING is not set.
    """
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise EnvironmentError(
            "Missing required environment variable.\n"
            "Ensure AZURE_STORAGE_CONNECTION_STRING is set in your .env file."
        )
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


def run() -> None:
    """
    Upload all CSV and JSON files from historical_data/ to ADLS.
    """
    client = _build_client()
    container = client.get_container_client(ADLS_CONTAINER_NAME)

    files = [
        f
        for f in HISTORICAL_DATA_DIR.iterdir()
        if f.suffix in (".csv", ".json")
    ]

    if not files:
        print("No historical data files found.")
        return

    print(f"Uploading {len(files)} file(s) to {ADLS_CONTAINER_NAME}/{ADLS_HISTORICAL_PREFIX}/")

    for file in files:
        blob_name = f"{ADLS_HISTORICAL_PREFIX}/{file.name}"
        with open(file, "rb") as data:
            container.upload_blob(name=blob_name, data=data, overwrite=True)
        print(f"    Uploaded: {file.name}")

    print("Done.")


if __name__ == "__main__":
    run()
