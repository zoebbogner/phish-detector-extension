# save_feature_index.py

import json
import os
from models.url.config import FEATURES as URL_FEATURES

def dump_feature_index(path="extension/production/url_feature_index.json"):
    """
    URL_FEATURES is your Python list in training order, e.g.:
      ["url_length","path_depth",...,"url_token_count"]
    We'll map each name to its integer index.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mapping = { name: idx for idx, name in enumerate(URL_FEATURES) }
    with open(path, "w") as f:
        json.dump(mapping, f, indent=2)
    print(f"[INFO] Wrote feature index mapping ({len(mapping)} entries) to {path}")

if __name__ == "__main__":
    dump_feature_index()