"""
Helper functions for phishing data processing: directory management, 
DataFrame construction, validation, and saving.
"""
<<<<<<< HEAD
from datetime import datetime, timezone
=======
>>>>>>> 18b28a670c3407fdc429fa17901bd32f511f8bea
from typing import Optional
import pandas as pd
from utils.data.constants import RAW_DATA_DIR


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
<<<<<<< HEAD
    timestamp = datetime.now(timezone.utc).isoformat()
    df = pd.DataFrame({
        'url': unique_urls,
        'label': label,
        'source': source_name,
        'timestamp': timestamp
=======
    df = pd.DataFrame({
        'url': unique_urls,
        'label': label,
>>>>>>> 18b28a670c3407fdc429fa17901bd32f511f8bea
    })
    return df

def build_phishing_df(urls, source_name: str) -> pd.DataFrame:
    """Build a phishing DataFrame with required columns and UTC ISO timestamp. Deduplicate URLs."""
    return build_df(urls, source_name, 1)


def build_benign_df(urls, source_name: str) -> pd.DataFrame:
    """Build a benign DataFrame with required columns and UTC ISO timestamp. Deduplicate URLs."""
    return build_df(urls, source_name, 0)

<<<<<<< HEAD

def validate_df(df: pd.DataFrame, required_columns: list[str]) -> bool:
    """Validate that DataFrame contains all required columns. Log error if missing."""
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"[ERROR] DataFrame missing columns: {missing}")
        return False
    return True


def save_to_csv(df: Optional[pd.DataFrame], filename: str) -> Optional[str]:
    """Save DataFrame to CSV in the raw data directory. Return saved path if successful, else None."""
    required_columns = ['url', 'label', 'source', 'timestamp']
    if df is not None and not df.empty and validate_df(df, required_columns):
=======
def save_to_csv(df: Optional[pd.DataFrame], filename: str) -> Optional[str]:
    """Save DataFrame to CSV in the raw data directory. Return saved path if successful, else None."""
    if df is not None and not df.empty:
>>>>>>> 18b28a670c3407fdc429fa17901bd32f511f8bea
        path = RAW_DATA_DIR / filename
        df.to_csv(path, index=False)
        print(f"[INFO] Saved {len(df)} records to {path}")
        return path
    else:
        print(f"[WARN] No data to save for {filename}")
        return None 