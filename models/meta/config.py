# Configuration for Meta model training and deployment

# === File Paths ===
TRAINING_MODEL_PATH = "models/meta/results/meta_model_xgb.pkl"
CLASSIFICATION_REPORT_PATH = "models/meta/results/classification_report.txt"
PRODUCTION_PATH = "extension/production/meta_model.json"
CONTENT_PROCESSED_PATH = "data/processed/content.csv"
URL_PROCESSED_PATH = "data/processed/url.csv"

# === Model & Training Hyperparameters ===
META_XGB_PARAMS = {
    "n_estimators": 200,
    "max_depth": 3,
    "subsample": 0.8,
    "reg_alpha": 1,
    "reg_lambda": 2,
    "min_child_weight": 2,
    "eval_metric": "logloss",
}

# === Meta Features ===
META_FEATURES = [
    "content_model_proba",
    "url_model_proba"
] 