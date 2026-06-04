"""
Storage configuration — single source of truth for all local paths
and Azure Data Lake Storage (ADLS) layout constants.

Any module that reads from or writes to local data directories,
or uploads to ADLS, should import its paths and prefixes from here.

Required environment variables:
    AZURE_STORAGE_CONNECTION_STRING : Azure Storage Account connection string
    STORAGE_ACCOUNT_CONTAINER_NAME  : Target ADLS container name
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Local Paths ---

# Root of the local data directory (repo_root/data/)
DATA_DIR = Path(__file__).parent.parent / "data"

HISTORICAL_DATA_DIR = DATA_DIR / "historical_data"
MAPPING_DATA_DIR    = DATA_DIR / "mapping_data"


# --- ADLS Layout ---

ADLS_CONTAINER_NAME     = os.environ.get("STORAGE_ACCOUNT_CONTAINER_NAME")
ADLS_HISTORICAL_PREFIX  = "bronze/manual_uploads/historical_data"
ADLS_MAPPING_PREFIX     = "bronze/mapping_data"


# --- Azure Credentials ---

AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
