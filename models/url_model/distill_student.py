"""
Distill XGBoost teacher into a Logistic Regression student model for phishing URL detection.
"""
import argparse

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.utils.class_weight import compute_sample_weight
import joblib
from models.url_model.config import (
    RAW_DATA_PATH, TEACHER_MODEL_PATH, FEATURES,
    STUDENT_REPORT_PATH, LOGREG_MODEL_PATH
)
from utils.ml_helpers import (
    load_and_preprocess_data, save_classification_report,
    save_model
)



def main():
    """Train and evaluate a distilled Logistic Regression student model using hard labels and realistic class balance (no oversampling or temperature scaling) to match production settings."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--use-class-weight', action='store_true', help='Use class_weight=balanced for sample_weight')
    args = parser.parse_args()

    # ---- Load Data ----
    x, y = load_and_preprocess_data(RAW_DATA_PATH, FEATURES, label_col="label")

    # ---- Train/Test Split ----
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"[INFO] Train shape: {x_train.shape}, Test shape: {x_test.shape}")

    # ---- Load Teacher Model ----
    print(f"[INFO] Loading teacher model from: {TEACHER_MODEL_PATH}")
    teacher = joblib.load(TEACHER_MODEL_PATH)
    y_train_teacher = teacher.predict_proba(x_train)[:, 1]
    y_test_teacher = teacher.predict_proba(x_test)[:, 1]

    # ---- Use hard labels from teacher outputs ----
    y_train_hard = (y_train_teacher > 0.5).astype(int)
    # y_test_hard = (y_test_teacher > 0.5).astype(int)  # Not used, so omitted

    # ---- Optional: Class Weighting ----
    sample_weight = None
    if args.use_class_weight:
        print("[INFO] Using class_weight='balanced' for sample_weight in LogisticRegression fit.")
        sample_weight = compute_sample_weight(class_weight='balanced', y=y_train)

    # ---- K-Fold Cross-Validation ----
    print("[INFO] Running 5-fold cross-validation for Logistic Regression student model...")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    student = LogisticRegression(max_iter=1000, random_state=42)
    cv_scores = cross_val_score(
        student, x_train, y_train_hard, cv=kf, scoring="f1"
    )
    print(f"[INFO] LogReg student 5-fold CV F1: {cv_scores}")
    print(f"[INFO] Mean F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ---- Train Student Model ----
    print("[INFO] Training Logistic Regression student model...")
    student.fit(x_train, y_train_hard, sample_weight=sample_weight)

    # ---- Evaluation: Student vs. True Labels ----
    y_pred = student.predict(x_test)
    y_proba = student.predict_proba(x_test)[:, 1]
    acc = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)
    print(f"[INFO] Student test accuracy (vs true labels): {acc:.4f}")
    print(f"[INFO] Student ROC AUC (vs true labels): {roc_auc:.4f}")
    report = classification_report(y_test, y_pred, output_dict=False)
    print("[INFO] Student Classification Report (vs true labels):")
    print(report)
    save_classification_report(report, STUDENT_REPORT_PATH)

    # ---- Optional: Student vs. Teacher (for analysis) ----
    y_pred_teacher = (y_test_teacher > 0.5).astype(int)
    acc_teacher = accuracy_score(y_pred_teacher, y_pred)
    print(f"[INFO] Student test accuracy (vs teacher hard labels): {acc_teacher:.4f}")

    # ---- Save Student Model ----
    save_model(student, LOGREG_MODEL_PATH)
    print(f"[INFO] Student model saved to {LOGREG_MODEL_PATH}")
    print("[INFO] Done.")

if __name__ == "__main__":
    main() 