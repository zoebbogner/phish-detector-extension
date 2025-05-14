# Configuration for URL model training and deployment
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

# === Model & Training Hyperparameters ===
TEST_SIZE = 0.2
RANDOM_STATE = 42


# === Model Parameters for Teacher (XGBoost) ===
XGB_PARAMS = {
    "eval_metric":    "logloss",
    "random_state":   RANDOM_STATE,
    "n_estimators":   120,         # cut in half → faster & smaller
    "max_depth":      6,           # shallower trees
    "subsample":      0.8,         # row subsampling for variance reduction
    "colsample_bytree":0.8,        # feature subsampling 
    "reg_alpha":      1,         # L1 regularization
    "reg_lambda":     2        # L2 regularization
}


# === Feature List ===
FEATURES = [
    'url_length', 'path_depth', 'num_subdomains', 'num_special_chars',
    'num_digits', 'num_hyphens', 'has_at_symbol', 'num_query_params',
    'digit_ratio', 'url_entropy',
    'has_https', 'levenshtein_to_brand',
    'uncommon_tld', 'url_token_count',
]

# === Data Source Constants ===
REQUIRED_COLUMNS: list[str] = ["url", "label"]
OPENPHISH_URL: str = 'https://openphish.com/feed.txt'
PHISHTANK_URL: str = 'http://data.phishtank.com/data/online-valid.csv'
OPENPHISH_CSV: str = 'openphish.csv'
PHISHTANK_CSV: str = 'phishtank.csv'
WIKIPEDIA_BASE_URL: str = "https://en.wikipedia.org/wiki/"
WIKIPEDIA_SEED_PAGES: list[str] = [
    "Python_(programming_language)",
    "Artificial_intelligence",
    "Machine_learning",
    "Data_science",
    "Internet",
    "World_Wide_Web",
    "Computer_science",
    "Open_source",
    "GitHub",
    "Wikipedia"
]
GITHUB_PAGES: list[str] = [
    "https://github.com/",
    "https://pages.github.com/",
    "https://github.blog/",
    "https://education.github.com/",
    "https://github.com/features/pages"
]
TRANCOLIST_URL: str = "https://tranco-list.eu/top-1m.csv.zip"
TRANCO_TOP_N: int = 1000000
# === Data Processing ===
RAW_FILES = ["openphish.csv", "phishtank.csv", "benign_urls.csv"]
