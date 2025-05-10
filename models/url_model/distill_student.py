"""
Distill XGBoost teacher into a Logistic Regression student model for phishing URL detection.
"""
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from config import (
    RAW_DATA_PATH, TEACHER_MODEL_PATH, STUDENT_MODEL_PATH,
    FEATURES, TEMPERATURE
)
from utils.ml_helpers import (
    load_and_preprocess_data, save_classification_report,
    save_model, apply_temperature
)

STUDENT_REPORT_PATH = "models/url_model/student_classification_report.txt"


def main():
    """Train and evaluate a distilled Logistic Regression student model."""
    # ---- Load Data ----
    x, y = load_and_preprocess_data(RAW_DATA_PATH, FEATURES, label_col="label")

    # ---- Train/Test Split ----
    x_train, x_test, _, y_test = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"[INFO] Train shape: {x_train.shape}, Test shape: {x_test.shape}")

    # ---- Load Teacher Model ----
    print(f"[INFO] Loading teacher model from: {TEACHER_MODEL_PATH}")
    teacher = joblib.load(TEACHER_MODEL_PATH)
    y_train_teacher = teacher.predict_proba(x_train)[:, 1]
    y_test_teacher = teacher.predict_proba(x_test)[:, 1]

    # ---- Apply Temperature Scaling to Teacher Outputs ----
    y_train_teacher_soft = apply_temperature(y_train_teacher, temperature=TEMPERATURE)
    y_test_teacher_soft = apply_temperature(y_test_teacher, temperature=TEMPERATURE)

    # ---- Train Student Model ----
    print("[INFO] Training Logistic Regression student model...")
    student = LogisticRegression(max_iter=1000, random_state=42)
    student.fit(x_train, y_train_teacher_soft)

    # ---- Evaluation: Student vs. True Labels ----
    y_pred = student.predict(x_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[INFO] Student test accuracy (vs true labels): {acc:.4f}")
    report = classification_report(y_test, y_pred, output_dict=False)
    print("[INFO] Student Classification Report (vs true labels):")
    print(report)
    save_classification_report(report, STUDENT_REPORT_PATH)

    # ---- Optional: Student vs. Teacher (for analysis) ----
    y_pred_teacher = (y_test_teacher_soft > 0.5).astype(int)
    acc_teacher = accuracy_score(y_pred_teacher, y_pred)
    print(f"[INFO] Student test accuracy (vs softened teacher): {acc_teacher:.4f}")

    # ---- Save Student Model ----
    save_model(student, STUDENT_MODEL_PATH)
    print(f"[INFO] Student model saved to {STUDENT_MODEL_PATH}")
    print("[INFO] Done.")

if __name__ == "__main__":
    main() 