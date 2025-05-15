"""Fetch URLs from all sources (raw, no enrichment).
"""
import os
import pandas as pd
from utils.fetch.benign import fetch_benign_urls
from utils.fetch.phishing import fetch_phishing_urls
from main_config import (
    RAW_FILES,BENIGN_CSV,ALL_URLS_CSV, SYNTHETIC_ALL_URLS_CSV, RAW_DIR, get_benign_csv_dir
)
def copy_to_single_csv(synthetic_urls: bool = False) -> None:
    """Combine all raw URL CSVs into a single CSV file (with deduplication)."""
    dfs = []
    benign_path = get_benign_csv_dir(synthetic_urls)
    file_name = SYNTHETIC_ALL_URLS_CSV if synthetic_urls else ALL_URLS_CSV
    output_path = os.path.join(RAW_DIR, file_name)

    for file in RAW_FILES:
        if file == BENIGN_CSV:
            path = os.path.join(benign_path, file)
        else:
            path = os.path.join(RAW_DIR, file)

        try:
            df = pd.read_csv(path)
            if "url" in df.columns:
                dfs.append(df)
                print(f"[INFO] Loaded {len(df)} rows from {file}")
            else:
                print(f"[WARN] Skipping {file} — no 'url' column found")
        except (FileNotFoundError, pd.errors.ParserError, OSError) as e:
            print(f"[ERROR] Failed to read {file}: {e}")

    if not dfs:
        print("[ERROR] No valid CSVs to combine.")
        return

    combined = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["url"])
    combined.to_csv(output_path, index=False)
    print(f"[INFO] Combined CSV saved to {output_path} with {len(combined)} unique URLs")
            
def fetch_all_urls(synthetic_urls: bool = False, n_paths_per_domain: int = 1) -> None:
    """Fetch all URLs from all sources (raw, no enrichment).
    If synthetic_urls is True, the URLs will be enriched with realistic paths and queries.
    """
    fetch_benign_urls(synthetic_urls, n_paths_per_domain)
    fetch_phishing_urls()
    copy_to_single_csv(synthetic_urls)
    
if __name__ == "__main__":
    fetch_all_urls(synthetic_urls=False, n_paths_per_domain=1)