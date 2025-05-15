import os
import pandas as pd
from models.content.utils.feature_extractor import ContentFeatureExtractor

PROCESSED_PATH = "models/content/results/content_features.csv"  # Placeholder path
RAW_DIR = "models/content/results"  # Placeholder path
ALL_HTML_CSV = "all_html.csv"  # Placeholder file name


def extract_features():
    """
    Extract features from a CSV with 'html' and 'label' columns and save for training.
    """
    extractor = ContentFeatureExtractor()
    path = os.path.join(RAW_DIR, ALL_HTML_CSV)
    print(f"[INFO] Loading {path}")
    try:
        df = pd.read_csv(path)
    except (pd.errors.ParserError, FileNotFoundError) as e:
        print(f"[ERROR] Could not read {path}: {e}")
        return

    if "html" not in df.columns or "label" not in df.columns:
        print(f"[ERROR] {ALL_HTML_CSV} missing required columns. Exiting.")
        return

    try:
        features = extractor.transform(df["html"])
        features_df = features
        features_df["label"] = df["label"].values
        print(f"[INFO] Extracted features from {ALL_HTML_CSV} ({len(df)} rows)")
    except (ValueError, KeyError, TypeError) as e:
        print(f"[ERROR] Feature extraction failed for {ALL_HTML_CSV}: {e}")
        return

    print(f"[INFO] Saving combined feature set to {PROCESSED_PATH} ({len(features_df)} rows)")
    try:
        features_df.to_csv(PROCESSED_PATH, index=False)
        print("[INFO] Feature set saved successfully.")
    except (OSError, PermissionError, pd.errors.EmptyDataError) as e:
        print(f"[ERROR] Could not save feature set: {e}") 