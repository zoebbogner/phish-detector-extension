# utils/fetch/extract_from_json.py

import os
import json
from models.content.utils.feature_extractor import ContentFeatureExtractor
from models.content.config import FEATURES, PROCESSED_PATH

JSON_PATH = "data/raw/hf/webs.json"  # standard .json file: list of {text, label}

def load_json_array(path: str):
    """
    Load a full JSON array from file.
    """
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            print(f"[INFO] Loaded {len(data)} entries.")
            return data
        except json.JSONDecodeError as e:
            print(f"[ERROR] Could not parse JSON file: {e}")
            return []

def yield_batches(data, batch_size: int = 1000):
    """
    Yield data in batches of given size.
    """
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def extract_html_features(batch_size: int = 1000):
    """
    Extract HTML content features from a JSON array file and write them to a CSV in batches.
    """
    print(f"[INFO] Reading: {JSON_PATH}")
    data = load_json_array(JSON_PATH)
    if not data:
        print("[ERROR] No valid data loaded.")
        return

    print(f"[INFO] Loaded {len(data)} entries. Processing in batches of {batch_size}.")
    extractor = ContentFeatureExtractor()
    first_write = True

    for batch_idx, batch in enumerate(yield_batches(data, batch_size)):
        print(f"[INFO] Processing batch {batch_idx + 1} ({len(batch)} items)")

        html_list = [entry["text"] for entry in batch if "text" in entry and "label" in entry]
        labels = [entry["label"] for entry in batch if "text" in entry and "label" in entry]

        if not html_list:
            print(f"[WARN] Skipping batch {batch_idx + 1}: no valid entries")
            continue

        try:
            features_df = extractor.transform_batch(html_list)
            features_df = features_df[FEATURES]
            features_df["label"] = labels

            os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
            features_df.to_csv(
                PROCESSED_PATH, 
                mode="w" if first_write else "a", 
                index=False, 
                header=first_write
            )
            print(f"[INFO] Saved batch {batch_idx + 1} ({len(batch)} entries)")
            first_write = False
        except (AttributeError, KeyError, ValueError, TypeError, OSError, PermissionError, ImportError) as e:
            print(f"[ERROR] Failed to extract features from batch {batch_idx + 1}: {e}")

if __name__ == "__main__":
    extract_html_features()