"""
Evaluate teacher and student models for phishing URL detection, print metrics, and save reports.
"""
import time
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    f1_score, precision_score, recall_score,
    accuracy_score, roc_auc_score, classification_report
)
import joblib
from config import FEATURES, RAW_DATA_PATH, TEACHER_MODEL_PATH, STUDENT_MODEL_PATH
from utils.ml_helpers import save_classification_report

def main():
    """Evaluate both teacher (XGBoost) and student (LogReg) models on the same test set."""
    print("[INFO] Loading data from:", RAW_DATA_PATH)
    df = pd.read_csv(RAW_DATA_PATH)
    df = df.dropna(subset=FEATURES + ["label"])
    X = df[FEATURES]
    y = df["label"]

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"[INFO] Test shape: {X_test.shape}")

    print("[INFO] Loading teacher model from:", TEACHER_MODEL_PATH)
    teacher = joblib.load(TEACHER_MODEL_PATH)
    start_teacher = time.time()
    y_pred_teacher = teacher.predict(X_test)
    y_proba_teacher = teacher.predict_proba(X_test)[:, 1]
    elapsed_teacher = time.time() - start_teacher
    print(f"[INFO] Teacher prediction time: {elapsed_teacher:.4f} seconds for {len(X_test)} samples")
    print("[INFO] Teacher Model Evaluation:")
    print("[INFO] Accuracy:", accuracy_score(y_test, y_pred_teacher))
    print("[INFO] F1-score:", f1_score(y_test, y_pred_teacher))
    print("[INFO] Precision:", precision_score(y_test, y_pred_teacher))
    print("[INFO] Recall:", recall_score(y_test, y_pred_teacher))
    print("[INFO] ROC AUC:", roc_auc_score(y_test, y_proba_teacher))
    teacher_report = classification_report(y_test, y_pred_teacher, output_dict=False)
    print("[INFO] Classification Report:")
    print(teacher_report)
    save_classification_report(teacher_report, "models/url_model/teacher_eval.txt")

    print("[INFO] Loading student model from:", STUDENT_MODEL_PATH)
    student = joblib.load(STUDENT_MODEL_PATH)
    start_student = time.time()
    y_pred_student = student.predict(X_test)
    y_proba_student = student.predict_proba(X_test)[:, 1]
    elapsed_student = time.time() - start_student
    print(f"[INFO] Student prediction time: {elapsed_student:.4f} seconds for {len(X_test)} samples")
    print("[INFO] Student Model Evaluation:")
    print("[INFO] Accuracy:", accuracy_score(y_test, y_pred_student))
    print("[INFO] F1-score:", f1_score(y_test, y_pred_student))
    print("[INFO] Precision:", precision_score(y_test, y_pred_student))
    print("[INFO] Recall:", recall_score(y_test, y_pred_student))
    print("[INFO] ROC AUC:", roc_auc_score(y_test, y_proba_student))
    student_report = classification_report(y_test, y_pred_student, output_dict=False)
    print("[INFO] Classification Report:")
    print(student_report)
    save_classification_report(student_report, "models/url_model/student_eval.txt")
    print("[INFO] Done.")

if __name__ == "__main__":
    main() 