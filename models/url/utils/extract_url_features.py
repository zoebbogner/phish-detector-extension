#!/usr/bin/env python3
"""
Extract URL features from raw CSVs and save a combined feature set for model training.
"""
import os
import pandas as pd
from models.url.utils.feature_extractor import URLFeatureExtractor
from models.url.utils.config import RAW_DIR, PROCESSED_PATH, RAW_FILES


def extract_url_features():
    """Extract features from raw URL CSVs and save a combined feature set for training."""
    all_dfs = []
    extractor = URLFeatureExtractor()
    for fname in RAW_FILES:
        path = os.path.join(RAW_DIR, fname)
        print(f"[INFO] Loading {path}")
        try:
            df = pd.read_csv(path)
        except (pd.errors.ParserError, FileNotFoundError) as e:
            print(f"[ERROR] Could not read {path}: {e}")
            continue
        if "url" not in df.columns or "label" not in df.columns:
            print(f"[ERROR] {fname} missing required columns. Skipping.")
            continue
        try:
            features = extractor.transform(df["url"])
            features_df = features
            features_df["label"] = df["label"].values
            all_dfs.append(features_df)
            print(f"[INFO] Extracted features from {fname} ({len(df)} rows)")
        except (ValueError, KeyError, TypeError) as e:
            print(f"[ERROR] Feature extraction failed for {fname}: {e}")
    if not all_dfs:
        print("[ERROR] No data processed. Exiting.")
        return
    full_df = pd.concat(all_dfs, ignore_index=True)
    print(f"[INFO] Saving combined feature set to {PROCESSED_PATH} ({len(full_df)} rows)")
    try:
        full_df.to_csv(PROCESSED_PATH, index=False)
        print("[INFO] Feature set saved successfully.")
    except (OSError, PermissionError, pd.errors.EmptyDataError) as e:
        print(f"[ERROR] Could not save feature set: {e}")

if __name__ == "__main__":
    extract_url_features() 