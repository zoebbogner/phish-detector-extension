#!/usr/bin/env python3
"""
Extract URL features from combined CSVs and save a feature set for model training.
"""
import os
import pandas as pd
from models.url.utils.feature_extractor import URLFeatureExtractor
from models.url.config import PROCESSED_PATH
from main_config import RAW_DIR, ALL_URLS_CSV, SYNTHETIC_ALL_URLS_CSV


def extract_features(use_synthetic: bool = True):
    """Extract features from the combined all_urls.csv or synthetic_all_urls.csv and save for training."""
    extractor = URLFeatureExtractor()
    file_name = SYNTHETIC_ALL_URLS_CSV if use_synthetic else ALL_URLS_CSV
    path = os.path.join(RAW_DIR, file_name)
    print(f"[INFO] Loading {path}")
    try:
        df = pd.read_csv(path)
    except (pd.errors.ParserError, FileNotFoundError) as e:
        print(f"[ERROR] Could not read {path}: {e}")
        return
    
    if "url" not in df.columns or "label" not in df.columns:
        print(f"[ERROR] {file_name} missing required columns. Exiting.")
        return
    
    try:
        features = extractor.transform(df["url"])
        features_df = features
        features_df["label"] = df["label"].values
        print(f"[INFO] Extracted features from {file_name} ({len(df)} rows)")
        
    except (ValueError, KeyError, TypeError) as e:
        print(f"[ERROR] Feature extraction failed for {file_name}: {e}")
        return
    
    print(f"[INFO] Saving combined feature set to {PROCESSED_PATH} ({len(features_df)} rows)")
    
    try:
        features_df.to_csv(PROCESSED_PATH, index=False)
        print("[INFO] Feature set saved successfully.")
    except (OSError, PermissionError, pd.errors.EmptyDataError) as e:
        print(f"[ERROR] Could not save feature set: {e}")
