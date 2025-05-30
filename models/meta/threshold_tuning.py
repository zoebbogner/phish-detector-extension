# threshold_tuning.py
import numpy as np
from joblib import load
from xgboost import XGBClassifier
from sklearn.metrics import precision_recall_curve
from sklearn.model_selection import train_test_split
from utils.ml_helpers import load_and_preprocess_data
from models.content.config import FEATURES as CONTENT_FEATURES
from models.url.config     import FEATURES as URL_FEATURES
from models.meta.config    import (
    CONTENT_PROCESSED_PATH, URL_PROCESSED_PATH,
    META_XGB_PARAMS
)

def get_meta_data():
    # Load base models
    content_model = load("models/content/results/model.pkl")
    url_model     = load("models/url/results/model.pkl")

    # Load and stack features
    Xc, y = load_and_preprocess_data(CONTENT_PROCESSED_PATH, CONTENT_FEATURES, label_col="label")
    Xu, _ = load_and_preprocess_data(URL_PROCESSED_PATH,     URL_FEATURES,   label_col="label")

    meta_feats = np.column_stack([
        content_model.predict_proba(Xc)[:, 1],
        url_model.predict_proba(Xu)[:, 1]
    ])
    return meta_feats, y

def train_holdout_split(meta_feats, y, test_size=0.2, random_state=42):
    return train_test_split(
        meta_feats, y, test_size=test_size,
        random_state=random_state, stratify=y
    )

def tune_thresholds(probs, y_true):
    precision, recall, thresholds = precision_recall_curve(y_true, probs)

    # 1) F1-maximizer
    f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1])
    idx_f1    = np.argmax(f1_scores)
    thresh_f1 = thresholds[idx_f1]
    p_f1, r_f1 = precision[idx_f1], recall[idx_f1]
    
    # 2) Balanced precision=recall
    min_pr    = np.minimum(precision[:-1], recall[:-1])
    idx_bal   = np.argmax(min_pr)
    thresh_bal= thresholds[idx_bal]
    p_bal, r_bal = precision[idx_bal], recall[idx_bal]
    min_pr_bal  = min_pr[idx_bal]

    return {
      "f1":   dict(threshold=thresh_f1, precision=p_f1, recall=r_f1, f1=f1_scores[idx_f1]),
      "balanced": dict(threshold=thresh_bal, precision=p_bal, recall=r_bal, min_pr=min_pr_bal)
    }

def main():
    # 1. Prepare data & split
    meta_feats, y = get_meta_data()
    X_train, X_test, y_train, y_test = train_holdout_split(meta_feats, y)

    # 2. Train the meta-model
    meta_model = XGBClassifier(**META_XGB_PARAMS)
    meta_model.fit(X_train, y_train)

    # 3. Get hold-out probabilities
    probs = meta_model.predict_proba(X_test)[:, 1]

    # 4. Tune!
    results = tune_thresholds(probs, y_test)

    # 5. Report
    print("→ F1-maximizing threshold:")
    for k,v in results["f1"].items():
        print(f"   {k:10s} = {v:.4f}")

    print("\n→ Balanced precision/recall threshold:")
    for k,v in results["balanced"].items():
        print(f"   {k:10s} = {v:.4f}")

    # return whichever you prefer, e.g.
    return results["balanced"]["threshold"]

if __name__ == "__main__":
    best = main()
    print(f"\nUse threshold = {best:.4f} in your extension.")