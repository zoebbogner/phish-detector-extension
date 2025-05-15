"""
Helper functions for phishing data processing: directory management, 
DataFrame construction, validation, and saving.
"""
from typing import Optional
from pathlib import Path
import pandas as pd
from models.url.utils.config import RAW_DATA_DIR


def ensure_data_dir() -> None:
    """Ensure the raw data directory exists."""
    if not RAW_DATA_DIR.exists():
        print(f"[INFO] Creating directory: {RAW_DATA_DIR}")
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    else:
        print(f"[INFO] Directory already exists: {RAW_DATA_DIR}")

def build_df(urls, source_name: str, label: int) -> pd.DataFrame:
    """Build a DataFrame with required columns and UTC ISO timestamp. Deduplicate URLs."""
    print(f"[INFO] Building DataFrame for {source_name} with {len(urls)} URLs")
    unique_urls = pd.Series(urls).drop_duplicates()
    df = pd.DataFrame({
        'url': unique_urls,
        'label': label,
    })
    return df

def build_phishing_df(urls, source_name: str) -> pd.DataFrame:
    """Build a phishing DataFrame with required columns and UTC ISO timestamp. Deduplicate URLs."""
    return build_df(urls, source_name, 1)


def build_benign_df(urls, source_name: str) -> pd.DataFrame:
    """Build a benign DataFrame with required columns and UTC ISO timestamp. Deduplicate URLs."""
    return build_df(urls, source_name, 0)

def save_to_csv(df: Optional[pd.DataFrame], filename: str, path: Optional[Path] = None) -> Optional[str]:
    """Save DataFrame to CSV in the raw data directory. Return saved path if successful, else None.
    If path is provided, save to that path, otherwise save to the raw data directory.
    """
    if df is not None and not df.empty:
        if path is None:
            path = RAW_DATA_DIR / filename
        else:
            path = Path(path) / filename
        df.to_csv(path, index=False)
        print(f"[INFO] Saved {len(df)} records to {path}")
        return path
    else:
        print(f"[WARN] No data to save for {filename}")
        return None 