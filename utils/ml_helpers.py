"""
General-purpose machine learning utility functions for model training, evaluation, and analysis.
"""
import os
import json
from typing import Sequence, Optional
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import joblib
import pandas as pd
from xgboost import plot_importance as xgb_plot_importance, XGBClassifier


def apply_temperature(probabilities, temperature=2.0):
    """
    Apply temperature scaling to a vector of probabilities.
    Used during knowledge distillation to soften teacher outputs.

    Args:
        probabilities (array-like): Probabilities from teacher model (values between 0 and 1).
        temperature (float): Temperature value (T > 1 softens more).

    Returns:
        np.ndarray: Softened probabilities.
    """
    # Convert to numpy array and clip to avoid log(0) and division by zero
    probabilities = np.asarray(probabilities)
    probabilities = np.clip(probabilities, 1e-6, 1 - 1e-6)
    logits = np.log(probabilities / (1 - probabilities))
    softened = 1 / (1 + np.exp(-logits / temperature))
    return softened


def cross_val_score_with_logging(model, X, y, cv: int = 5, scoring: str = "f1") -> np.ndarray:
    """
    Run cross-validation and print mean/std of the score.
    Returns the array of scores.
    """
    print(f"[INFO] Running {cv}-fold cross-validation (scoring={scoring})...")
    scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
    print(f"[INFO] Cross-validated {scoring} scores: {scores}")
    print(f"[INFO] Mean {scoring}: {scores.mean():.4f} ± {scores.std():.4f}")
    return scores


def print_top_n_feature_importance(importances: Sequence[float], feature_names: Sequence[str], n: int = 3) -> None:
    """
    Print the top-n most important features and their values.
    """
    importances = np.array(importances)
    top_indices = np.argsort(importances)[::-1][:n]
    print(f"[INFO] Top {n} important features:")
    for i in top_indices:
        print(f" - {feature_names[i]}: {importances[i]:.4f}")


def save_classification_report(report: str, path: str, encoding: Optional[str] = "utf-8") -> None:
    """
    Save a classification report string to a file with specified encoding.
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, "w", encoding=encoding) as f:
        f.write(report)
    print(f"[INFO] Classification report saved to {path}")


def print_confusion_matrix(y_true, y_pred) -> None:
    """
    Print the confusion matrix for predictions.
    """
    print("[INFO] Confusion matrix:")
    print(confusion_matrix(y_true, y_pred))


def plot_feature_importance(model, path: str, importance_type: str = 'gain', figsize=(8, 6)) -> None:
    """
    Plot and save feature importance for a fitted model.
    """
    plt.figure(figsize=figsize)
    xgb_plot_importance(model, importance_type=importance_type, show_values=False)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print(f"[INFO] Feature importance plot saved to {path}")


def save_model_with_joblib(model, path: str) -> None:
    """
    Save a model to disk using joblib.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    print(f"[INFO] Model saved to {path}")
    
def save_model_to_production_json(model : XGBClassifier, path: str) -> None:
    """
    Save a model to disk using booster.savemodel().
    This is the recommended way to save a model for production deployment in chrome extension.
    """
    if not path.lower().endswith('.json'):
        raise ValueError("Production model path should end in '.json'")
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    booster = model.get_booster()
    booster.save_model(path)
    print(f"[INFO] Saved model to {path}")

def load_and_preprocess_data(path: str, features: Sequence[str], label_col: str = "label") -> tuple[pd.DataFrame, pd.Series]:
    """
    Load a CSV, drop rows with missing values in features+label, and return (X, y).
    """
    df = pd.read_csv(path)
    initial_rows = len(df)
    df = df.dropna(subset=list(features) + [label_col])
    dropped = initial_rows - len(df)
    missing_cols = set(features + [label_col]) - set(df.columns)
    if missing_cols:
        print(f"[ERROR] Missing columns in CSV: {missing_cols}")
    
    X = df[list(features)]
    y = df[label_col]
    return X, y 
