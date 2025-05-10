"""
Export a trained LogisticRegression model's weights and bias to JSON for browser inference.
"""
import json
import joblib
from sklearn.linear_model import LogisticRegression
from config import FEATURES, STUDENT_MODEL_PATH, EXPORT_JSON_PATH

def main():
    """Export LogisticRegression weights and bias to JSON for browser inference."""
    print(f"[INFO] Loading student model from: {STUDENT_MODEL_PATH}")
    model = joblib.load(STUDENT_MODEL_PATH)

    # Validation
    if not isinstance(model, LogisticRegression):
        raise TypeError("Loaded model is not a LogisticRegression instance.")
    if model.coef_.shape[1] != len(FEATURES):
        raise ValueError(f"Model weights shape {model.coef_.shape[1]} does not match feature count {len(FEATURES)}.")

    weights = [round(float(w), 6) for w in model.coef_.flatten()]
    bias = round(float(model.intercept_[0]), 6)
    export_dict = {
        "weights": weights,
        "bias": bias
    }

    print(f"[INFO] Writing weights and bias to: {EXPORT_JSON_PATH}")
    with open(EXPORT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(export_dict, f, indent=2)
    print("[INFO] Export complete.")

if __name__ == "__main__":
    main() 