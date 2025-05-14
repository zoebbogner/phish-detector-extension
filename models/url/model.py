"""
Train an XGBoost teacher model for phishing URL detection using features and config.
"""
import time
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from models.url.utils.config import (
    FEATURES, RAW_DATA_PATH, MODEL_PATH, TEST_SIZE,
    RANDOM_STATE, FEATURE_IMPORTANCE_PATH, XGB_PARAMS,
    CLASSIFICATION_REPORT_PATH, PRODUCTION_PATH
)
from utils.ml_helpers import (
    cross_val_score_with_logging, save_classification_report,
    print_confusion_matrix, plot_feature_importance, save_model, load_and_preprocess_data
)

def train_model_for_training():
    """Train and evaluate an XGBoost model for phishing URL detection."""
    # ---- Load Data ----
    x, y = load_and_preprocess_data(RAW_DATA_PATH, FEATURES, label_col="label")
    print(f"[INFO] Loaded data with shape: {x.shape}")

    # ---- Cross-Validation ----
    cross_val_score_with_logging(XGBClassifier(**XGB_PARAMS), x, y, cv=5, scoring="f1")

    # ---- Train/Test Split ----
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, stratify=y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"[INFO] Train shape: {x_train.shape}, Test shape: {x_test.shape}")

    # ---- Model Training ----
    print("[INFO] Training XGBoost model...")
    start_time = time.time()
    model = XGBClassifier(**XGB_PARAMS)
    model.fit(x_train, y_train, eval_set=[(x_test, y_test)], verbose=False)
    elapsed = time.time() - start_time
    print(f"[INFO] Training completed in {elapsed:.2f} seconds.")

    # ---- Evaluation ----
    y_pred = model.predict(x_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[INFO] Test accuracy: {acc:.4f}")

    # ---- Confusion Matrix ----
    print_confusion_matrix(y_test, y_pred)

    # ---- Classification Report ----
    report = classification_report(y_test, y_pred, output_dict=False)
    print("[INFO] Classification report:")
    print(report)
    save_classification_report(report, CLASSIFICATION_REPORT_PATH)

    # ---- Feature Importance Plot ----
    plot_feature_importance(model, FEATURE_IMPORTANCE_PATH)

    # ---- Save Model ----
    save_model(model, MODEL_PATH)
    print(f"[INFO] Model saved to {MODEL_PATH}")
    print("[INFO] Done.")

def train_model_for_production():
    """Train an XGBoost model for phishing URL detection on all available data and save for production deployment."""
    # ---- Load all data ----
    x, y = load_and_preprocess_data(RAW_DATA_PATH, FEATURES, label_col="label")
    print(f"[INFO] Loaded full data with shape: {x.shape}")

    # ---- Train on all data ----
    print("[INFO] Training XGBoost model on all data for production...")
    model = XGBClassifier(**XGB_PARAMS)
    model.fit(x, y)

    # ---- Save production model ----
    save_model(model, PRODUCTION_PATH)
    print(f"[INFO] Production model saved to {PRODUCTION_PATH}")
