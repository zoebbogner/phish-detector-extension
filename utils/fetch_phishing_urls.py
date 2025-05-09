#!/usr/bin/env python3
"""
Fetch phishing URLs from OpenPhish and PhishTank, save as CSVs with labels and metadata.
"""
from datetime import datetime, timezone
from typing import Optional
import io
import requests
import pandas as pd
from utils.constants import RAW_DATA_DIR, OPENPHISH_URL, PHISHTANK_URL, OPENPHISH_CSV, PHISHTANK_CSV


def ensure_data_dir() -> None:
    """Ensure the raw data directory exists."""
    if not RAW_DATA_DIR.exists():
        print(f"[INFO] Creating directory: {RAW_DATA_DIR}")
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    else:
        print(f"[INFO] Directory already exists: {RAW_DATA_DIR}")


def build_phishing_df(urls, source_name: str) -> pd.DataFrame:
    """Build a phishing DataFrame with required columns and UTC ISO timestamp. Deduplicate URLs."""
    unique_urls = pd.Series(urls).drop_duplicates()
    timestamp = datetime.now(timezone.utc).isoformat()
    df = pd.DataFrame({
        'url': unique_urls,
        'label': 1,
        'source': source_name,
        'timestamp': timestamp
    })
    return df


def validate_df(df: pd.DataFrame, required_columns: list[str]) -> bool:
    """Validate that DataFrame contains all required columns. Log error if missing."""
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"[ERROR] DataFrame missing columns: {missing}")
        return False
    return True


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


def save_to_csv(df: Optional[pd.DataFrame], filename: str) -> Optional[str]:
    """Save DataFrame to CSV in the raw data directory. Return saved path if successful, else None."""
    required_columns = ['url', 'label', 'source', 'timestamp']
    if df is not None and not df.empty and validate_df(df, required_columns):
        path = RAW_DATA_DIR / filename
        df.to_csv(path, index=False)
        print(f"[INFO] Saved {len(df)} records to {path}")
        return path
    else:
        print(f"[WARN] No data to save for {filename}")
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