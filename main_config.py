"""Main configuration for file paths and data locations."""
from pathlib import Path

# === File and Directory Paths ===
RAW_DIR = "data/raw"
BENIGN_CSV: str = "benign_urls.csv"
OPENPHISH_CSV = "openphish.csv"
PHISHTANK_CSV = "phishtank.csv"
ALL_URLS_CSV = "all_urls.csv"
SYNTHETIC_ALL_URLS_CSV = "synthetic_all_urls.csv"
RAW_FILES = [BENIGN_CSV, OPENPHISH_CSV, PHISHTANK_CSV]

def get_benign_csv_dir(synthetic_urls: bool = False) -> str:
    """Get the path to the benign CSV file based on synthetic URLs flag."""
    if synthetic_urls:
        return Path(RAW_DIR, 'synthetic')
    else:
        return Path(RAW_DIR)

