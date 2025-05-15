from pathlib import Path

# === File and Directory Paths ===
RAW_DATA_PATH = "data/processed/full_feature_set.csv"
MODEL_PATH = "models/url_model/results/model.pkl"
EXPORT_JSON_PATH = "models/url_model/results/logreg_weights.json"
FEATURE_IMPORTANCE_PATH = "models/url_model/results/feature_importance.png"
CLASSIFICATION_REPORT_PATH = "models/url_model/results/classification_report.txt"
RAW_DATA_DIR: Path = Path('data/raw')
BENIGN_CSV: str = "benign_urls.csv"
PROCESSED_PATH = "data/processed/full_feature_set.csv"
RAW_DIR = "data/raw"
PRODUCTION_PATH = "models/url_model/production/url_model.pkl"

def get_benign_csv_path(synthetic_urls: bool = False) -> str:
    """Get the path to the benign CSV file based on synthetic URLs flag."""
    if synthetic_urls:
        return Path(RAW_DATA_DIR, 'synthetic', BENIGN_CSV)
    else:
        return Path(RAW_DATA_DIR, BENIGN_CSV)

