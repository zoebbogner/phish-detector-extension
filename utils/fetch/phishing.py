"""
Fetch phishing URLs from OpenPhish and PhishTank.
"""
import pandas as pd
from utils.fetch.config import OPENPHISH_CSV
from utils.fetch.data_helpers import build_phishing_df, save_to_csv, ensure_data_dir
from utils.fetch.raw_url_fetchers import fetch_openphish_urls, fetch_phishtank_urls

def fetch_openphish() -> pd.DataFrame:
    """Fetch phishing URLs from OpenPhish and return as a DataFrame."""
    print("[INFO] Fetching OpenPhish URLs...")
    urls = fetch_openphish_urls()
    if urls:
        print(f"[INFO] Retrieved {len(urls)} URLs from OpenPhish.")
        return build_phishing_df(urls, 'OpenPhish')
    else:
        print("[ERROR] No URLs fetched from OpenPhish.")
        return pd.DataFrame(columns=["url", "label"])

def fetch_phishtank() -> pd.DataFrame:
    """Fetch phishing URLs from PhishTank and return as a DataFrame."""
    print("[INFO] Fetching PhishTank URLs...")
    urls = fetch_phishtank_urls()
    if urls:
        print(f"[INFO] Retrieved {len(urls)} URLs from PhishTank.")
        return build_phishing_df(urls, 'PhishTank')
    else:
        print("[ERROR] No URLs fetched from PhishTank.")
        return pd.DataFrame(columns=["url", "label"])

def fetch_phishing_urls() -> None:
    """Main function to fetch and save phishing URLs from both sources."""
    ensure_data_dir()
    openphish_df = fetch_openphish()
    if not openphish_df.empty:
        openphish_path = save_to_csv(openphish_df, OPENPHISH_CSV)
        if openphish_path is not None:
            print(f"[INFO] OpenPhish saved to {openphish_path}")
    else:
        print("[ERROR] OpenPhish DataFrame is empty and was not saved.")

    # phishtank_df = fetch_phishtank()
    # if not phishtank_df.empty:
    #     phishtank_path = save_to_csv(phishtank_df, PHISHTANK_CSV)
    #     if phishtank_path is not None:
    #         print(f"[INFO] PhishTank saved to {phishtank_path}")
    # else:
    #     print("[ERROR] PhishTank DataFrame is empty and was not saved.")
        
    total = 0
    if not openphish_df.empty:
        total += len(openphish_df)
        print(f"[INFO] OpenPhish URLs collected: {len(openphish_df)}")
    # if not phishtank_df.empty:
    #     total += len(phishtank_df)
    #     print(f"[INFO] PhishTank URLs collected: {len(phishtank_df)}")
        
    print(f"[INFO] Fetching complete. Total phishing URLs collected: {total}")
