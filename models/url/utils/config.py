# Configuration for URL model training and deployment

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
