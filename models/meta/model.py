import time
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from joblib import load
from models.content.config import FEATURES as CONTENT_FEATURES
from models.url.config import FEATURES as URL_FEATURES
from models.meta.config import (
    CONTENT_PROCESSED_PATH, URL_PROCESSED_PATH, TRAINING_MODEL_PATH,
    CLASSIFICATION_REPORT_PATH, META_XGB_PARAMS, PRODUCTION_PATH
)
from utils.ml_helpers import (
    cross_val_score_with_logging, save_classification_report,
    print_confusion_matrix, load_and_preprocess_data,
    save_model_with_joblib, save_model_to_production_json
)

def train_meta_model_for_training():
    """Train and evaluate an XGBoost meta-model for phishing detection ensemble."""
    # ---- Load Data ----
    content_model = load("models/content/results/model.pkl")
    url_model = load("models/url/results/model.pkl")
    x_content, y = load_and_preprocess_data(CONTENT_PROCESSED_PATH, CONTENT_FEATURES, label_col="label")
    x_url, _ = load_and_preprocess_data(URL_PROCESSED_PATH, URL_FEATURES, label_col="label")
    assert x_content.shape[0] == x_url.shape[0] == len(y), "Shape mismatch between base model outputs"
    meta_features = np.column_stack([
        content_model.predict_proba(x_content)[:, 1],
        url_model.predict_proba(x_url)[:, 1]
    ])
    print(f"[INFO] Loaded meta features with shape: {meta_features.shape}")

    # ---- Cross-Validation ----
    cross_val_score_with_logging(XGBClassifier(**META_XGB_PARAMS), meta_features, y, cv=5, scoring="f1")

    # ---- Train/Test Split ----
    x_train, x_test, y_train, y_test = train_test_split(
        meta_features, y, stratify=y, test_size=0.2, random_state=42
    )
    print(f"[INFO] Train shape: {x_train.shape}, Test shape: {x_test.shape}")

    # ---- Model Training ----
    print("[INFO] Training XGBoost meta-model...")
    start_time = time.time()
    meta_model = XGBClassifier(**META_XGB_PARAMS)
    meta_model.fit(x_train, y_train, eval_set=[(x_test, y_test)], verbose=False)
    elapsed = time.time() - start_time
    print(f"[INFO] Training completed in {elapsed:.2f} seconds.")

    # ---- Evaluation ----
    y_pred = meta_model.predict(x_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[INFO] Test accuracy: {acc:.4f}")
    print_confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=False)
    print("[INFO] Classification report:")
    print(report)
    save_classification_report(report, CLASSIFICATION_REPORT_PATH)

    # ---- Save Model ----
    save_model_with_joblib(meta_model, TRAINING_MODEL_PATH)
    print(f"[INFO] Meta-model saved to {TRAINING_MODEL_PATH}")
    print("[INFO] Done.")

def train_meta_model_for_production():
    """Train an XGBoost meta-model on all available data and save for production deployment."""
    content_model = load("models/content/results/model.pkl")
    url_model = load("models/url/results/model.pkl")
    x_content, y = load_and_preprocess_data(CONTENT_PROCESSED_PATH, CONTENT_FEATURES, label_col="label")
    x_url, _ = load_and_preprocess_data(URL_PROCESSED_PATH, URL_FEATURES, label_col="label")
    assert x_content.shape[0] == x_url.shape[0] == len(y), "Shape mismatch between base model outputs"
    meta_features = np.column_stack([
        content_model.predict_proba(x_content)[:, 1],
        url_model.predict_proba(x_url)[:, 1]
    ])
    print(f"[INFO] Loaded full meta features with shape: {meta_features.shape}")
    print("[INFO] Training XGBoost meta-model on all data for production...")
    meta_model = XGBClassifier(**META_XGB_PARAMS)
    meta_model.fit(meta_features, y)
    save_model_to_production_json(meta_model, PRODUCTION_PATH)
    print(f"[INFO] Production meta-model saved to {PRODUCTION_PATH}") 