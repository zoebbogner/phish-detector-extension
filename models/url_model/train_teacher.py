"""
Train an XGBoost teacher model for phishing URL detection using features and config.
"""
import time
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from config import (
    FEATURES, RAW_DATA_PATH, TEACHER_MODEL_PATH, TEST_SIZE,
    RANDOM_STATE, FEATURE_IMPORTANCE_PATH, XGB_PARAMS,
    CLASSIFICATION_REPORT_PATH
)
from utils.ml_helpers import (
    cross_val_score_with_logging, print_top_n_feature_importance, save_classification_report,
    print_confusion_matrix, plot_feature_importance, save_model, load_and_preprocess_data
)

def main():
    """Train and evaluate an XGBoost model for phishing URL detection."""
    # ---- Load Data ----
    x, y = load_and_preprocess_data(RAW_DATA_PATH, FEATURES, label_col="label")

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
    model.fit(x_train, y_train)
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

    # ---- Top 3 Most Important Features ----
    print_top_n_feature_importance(model.feature_importances_, FEATURES, n=3)

    # ---- Feature Importance Plot ----
    plot_feature_importance(model, FEATURE_IMPORTANCE_PATH)

    # ---- Save Model ----
    save_model(model, TEACHER_MODEL_PATH)
    print(f"[INFO] Model saved to {TEACHER_MODEL_PATH}")
    print("[INFO] Done.")

if __name__ == "__main__":
    main() 