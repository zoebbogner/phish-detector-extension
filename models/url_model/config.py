# Configuration for URL model training and deployment

FEATURES = [
    "url_length",
    "entropy",
    "has_ip",
    "is_https",
    "keyword_count",
    "tld_encoded"
]

RAW_DATA_PATH = "data/processed/full_feature_set.csv"
TEACHER_MODEL_PATH = "models/url_model/xgb_teacher.pkl"
STUDENT_MODEL_PATH = "models/url_model/logreg_student.pkl"
EXPORT_JSON_PATH = "models/url_model/logreg_weights.json"
FEATURE_IMPORTANCE_PATH = "models/url_model/feature_importance.png"
CLASSIFICATION_REPORT_PATH = "models/url_model/classification_report.txt"

TEST_SIZE = 0.2
RANDOM_STATE = 42
TEMPERATURE = 2.0

XGB_PARAMS = {
    "use_label_encoder": False,
    "eval_metric": "logloss",
    "random_state": RANDOM_STATE,
    "n_estimators": 200,
    "max_depth": 5
}
