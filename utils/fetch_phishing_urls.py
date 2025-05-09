#!/usr/bin/env python3
"""
Fetch phishing URLs from OpenPhish and PhishTank, save as CSVs with labels and metadata.
"""
from typing import Optional
import io
import requests
import pandas as pd
from utils.constants import OPENPHISH_URL, PHISHTANK_URL, OPENPHISH_CSV, PHISHTANK_CSV
from utils.data_helpers import ensure_data_dir, build_phishing_df, save_to_csv


def fetch_openphish() -> Optional[pd.DataFrame]:
    """Fetch phishing URLs from OpenPhish and return as a DataFrame."""
    print("[INFO] Fetching OpenPhish URLs...")
    try:
        resp = requests.get(OPENPHISH_URL, timeout=20)
        resp.raise_for_status()
        urls = [line.strip() for line in resp.text.splitlines() if line.strip()]
        print(f"[INFO] Retrieved {len(urls)} URLs from OpenPhish.")
        return build_phishing_df(urls, 'OpenPhish')
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch from OpenPhish: {e}")
        return None


def fetch_phishtank() -> Optional[pd.DataFrame]:
    """Fetch phishing URLs from PhishTank and return as a DataFrame."""
    print("[INFO] Fetching PhishTank URLs...")
    try:
        resp = requests.get(PHISHTANK_URL, timeout=30)
        resp.raise_for_status()
        df_raw = pd.read_csv(io.StringIO(resp.text))
        if 'url' not in df_raw.columns:
            print("[ERROR] 'url' column not found in PhishTank data.")
            return None
        
        urls = df_raw['url'].dropna().unique()
        print(f"[INFO] Retrieved {len(urls)} URLs from PhishTank.")
        return build_phishing_df(urls, 'PhishTank')
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch from PhishTank: {e}")
        return None


def main() -> None:
    """Main function to fetch and save phishing URLs from both sources."""
    ensure_data_dir()
    openphish_df = fetch_openphish()
    openphish_path = save_to_csv(openphish_df, OPENPHISH_CSV)
    if openphish_path is not None:  
        print(f"[INFO] OpenPhish saved to {openphish_path}")
    
    phishtank_df = fetch_phishtank()
    phishtank_path = save_to_csv(phishtank_df, PHISHTANK_CSV)
    if phishtank_path is not None:
        print(f"[INFO] PhishTank saved to {phishtank_path}")
    
    total = 0
    if openphish_df is not None:
        total += len(openphish_df)
    if phishtank_df is not None:
        total += len(phishtank_df)
    print(f"[INFO] Fetching complete. Total phishing URLs collected: {total}")


if __name__ == "__main__":
    main() 