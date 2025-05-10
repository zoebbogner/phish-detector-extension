"""
Constants for phishing URL fetching utilities.
"""
from pathlib import Path

REQUIRED_COLUMNS: list[str] = ["url", "label"]

RAW_DATA_DIR: Path = Path('data/raw')
OPENPHISH_URL: str = 'https://openphish.com/feed.txt'
PHISHTANK_URL: str = 'http://data.phishtank.com/data/online-valid.csv'
OPENPHISH_CSV: str = 'openphish.csv'
PHISHTANK_CSV: str = 'phishtank.csv'

WIKIPEDIA_BASE_URL: str = "https://en.wikipedia.org/wiki/"

WIKIPEDIA_SEED_PAGES: list[str] = [
    "Python_(programming_language)",
    "Artificial_intelligence",
    "Machine_learning",
    "Data_science",
    "Internet",
    "World_Wide_Web",
    "Computer_science",
    "Open_source",
    "GitHub",
    "Wikipedia"
]

GITHUB_PAGES: list[str] = [
    "https://github.com/",
    "https://pages.github.com/",
    "https://github.blog/",
    "https://education.github.com/",
    "https://github.com/features/pages"
]

BENIGN_CSV: str = "benign_urls.csv" 

TRANCOLIST_URL: str = "https://tranco-list.eu/top-1m.csv.zip"

# Constants for data processing and feature extraction

RAW_DIR = "data/raw"
PROCESSED_PATH = "data/processed/full_feature_set.csv"
RAW_FILES = ["openphish.csv", "phishtank.csv", "benign_urls.csv"]