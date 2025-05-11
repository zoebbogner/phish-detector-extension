"""
Train an XGBoost teacher model for phishing detection based on page content (TF-IDF).
"""
import sys, os

# ▸ Walk up from content_model/ → models/ → <repo_root>
REPO_ROOT = os.path.abspath(
    os.path.join(__file__, os.pardir, os.pardir, os.pardir)
)
sys.path.insert(0, REPO_ROOT)

#!/usr/bin/env python3
"""
Train and evaluate the content-based phishing detection model using TF-IDF + classifier pipeline.
"""
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Import content-specific configuration
from config import (
    CONTENT_FEATURES_PATH,
    CONTENT_MODEL_PATH,
    TEST_SIZE,
    RANDOM_STATE,
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
    MODEL_TYPE
)

def main():
    # Load extracted content features (expect 'text' and 'label' columns)
    df = pd.read_csv(CONTENT_FEATURES_PATH)
    if 'text' not in df.columns or 'label' not in df.columns:
        raise ValueError("Content features CSV must include 'text' and 'label' columns.")

    # Features and target
    texts = df['text'].fillna("")
    y = df['label']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )

    # Choose classifier
    if MODEL_TYPE.lower() == 'xgb':
        clf_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=RANDOM_STATE)
    else:
        clf_model = SVC(kernel='linear', probability=True, random_state=RANDOM_STATE)

    # Pipeline: TF-IDF + classifier
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=tuple(TFIDF_NGRAM_RANGE)
        )),
        ('clf', clf_model)
    ])

    # Train
    print(f"[INFO] Training content-based model ({MODEL_TYPE}) on {len(X_train)} samples...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    print("[INFO] Evaluating on test set")
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(f"Confusion Matrix:\n{cm}")

    # Save pipeline
    os.makedirs(os.path.dirname(CONTENT_MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, CONTENT_MODEL_PATH)
    print(f"[INFO] Saved pipeline to {CONTENT_MODEL_PATH}")

if __name__ == '__main__':
    main()
