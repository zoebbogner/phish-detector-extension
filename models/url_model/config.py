# Configuration for URL model training and deployment

FEATURES = [
    "url_length",
    "path_depth", 
    "domain_length",
    "num_subdomains",
    "num_special_chars",
    "num_digits",
    "num_hyphens",
    "has_at_symbol",
    "query_length",
    "num_query_params",
    "contains_ip",
    "digit_ratio",
    "url_entropy",
    "suspicious_word_count",
    "has_https",
    "dot_count",
    "punycode_present",
    "port_present",
    "longest_special_sequence"
]

RAW_DATA_PATH = "data/processed/full_feature_set.csv"
TEACHER_MODEL_PATH = "models/url_model/xgb_teacher.pkl"
STUDENT_MODEL_PATH = "models/url_model/logreg_student.pkl"
EXPORT_JSON_PATH = "models/url_model/logreg_weights.json"
FEATURE_IMPORTANCE_PATH = "models/url_model/feature_importance.png"
CLASSIFICATION_REPORT_PATH = "models/url_model/classification_report.txt"
STUDENT_REPORT_PATH = "models/url_model/student_classification_report.txt"
LOGREG_MODEL_PATH = "models/url_model/logreg_student.pkl"

TEST_SIZE = 0.2
RANDOM_STATE = 42
TEMPERATURE = 2.0

XGB_PARAMS = {
    "eval_metric": "logloss",
    "random_state": RANDOM_STATE,
    "n_estimators": 200,
    "max_depth": 5
}
