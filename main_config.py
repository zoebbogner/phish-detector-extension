"""Main configuration for file paths and data locations."""
from pathlib import Path

# === File and Directory Paths ===
MODEL_PATH = "models/url_model/results/model.pkl"
EXPORT_JSON_PATH = "models/url_model/results/logreg_weights.json"
FEATURE_IMPORTANCE_PATH = "models/url_model/results/feature_importance.png"
CLASSIFICATION_REPORT_PATH = "models/url_model/results/classification_report.txt"
RAW_DATA_DIR: Path = Path('data/raw')
PROCESSED_PATH = "data/processed/full_feature_set.csv"
RAW_DIR = "data/raw"
PRODUCTION_PATH = "models/url_model/production/url_model.pkl"

BENIGN_CSV: str = "benign_urls.csv"
OPENPHISH_CSV = "openphish.csv"
PHISHTANK_CSV = "phishtank.csv"

RAW_FILES = [BENIGN_CSV, OPENPHISH_CSV, PHISHTANK_CSV]
def get_benign_csv_dir(synthetic_urls: bool = False) -> str:
    """Get the path to the benign CSV file based on synthetic URLs flag."""
    if synthetic_urls:
        return Path(RAW_DATA_DIR, 'synthetic')
    else:
        return Path(RAW_DATA_DIR)

