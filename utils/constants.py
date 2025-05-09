"""
Constants for phishing URL fetching utilities.
"""
from pathlib import Path

RAW_DATA_DIR: Path = Path('data/raw')
OPENPHISH_URL: str = 'https://openphish.com/feed.txt'
PHISHTANK_URL: str = 'http://data.phishtank.com/data/online-valid.csv'
OPENPHISH_CSV: str = 'openphish.csv'
PHISHTANK_CSV: str = 'phishtank.csv' 