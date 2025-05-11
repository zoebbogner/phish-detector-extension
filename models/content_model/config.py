CONTENT_MODEL_DIR       = "models/content_model"
CONTENT_RAW_DATA_PATH   = "data/processed/content_features.csv"

CONTENT_TFIDF_VECT_FILE = "tfidf_vectorizer.pkl"
CONTENT_MODEL_FILE      = "content_model.pkl"

# full paths
CONTENT_TFIDF_VECT_PATH = f"{CONTENT_MODEL_DIR}/{CONTENT_TFIDF_VECT_FILE}"
CONTENT_MODEL_PATH      = f"{CONTENT_MODEL_DIR}/{CONTENT_MODEL_FILE}"

# TF-IDF params (mirror train script defaults)
CONTENT_TFIDF_PARAMS    = {
    "ngram_range": (1, 2),
    "max_df": 0.8,
    "min_df": 5,
    "max_features": 10_000
}

CONTENT_FEATURES_PATH = "data/processed/content_features.csv"
CONTENT_MODEL_PATH    = "models/content/content_pipeline.joblib"
TEST_SIZE            = 0.2
RANDOM_STATE         = 42
TFIDF_MAX_FEATURES   = 5000
TFIDF_NGRAM_RANGE    = (1, 2)
MODEL_TYPE           = "xgb"  # or "svm"

# XGBoost hyperparameters (mirror URL teacher style) :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
CONTENT_XGB_PARAMS = {
    "eval_metric": "logloss",
    "random_state": RANDOM_STATE,
    "n_estimators": 200,
    "max_depth": 5
}

FEATURES = ["num_links",
      "num_external_links",
      "num_forms",
      "num_inputs",
      "num_hidden_inputs",
      "num_password_inputs",
      "ratio_password_inputs",
      "num_scripts",
      "num_external_scripts",
      "num_iframes",
      "num_non_sandbox_iframes",
      "num_images",
      "num_event_handlers",
      "num_onclick_attrs",
      "num_onmouseover_attrs",
      "num_meta_refresh",
      "suspicious_word_count"
]
