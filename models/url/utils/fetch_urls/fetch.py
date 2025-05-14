"""Utility functions to fetch benign and phishing URLs."""
from models.url.utils.fetch_urls.benign import fetch_benign_urls
from models.url.utils.fetch_urls.phishing import fetch_phishing_urls

def fetch_urls() -> None:
    """Fetch both benign and phishing URLs."""
    fetch_benign_urls()
    fetch_phishing_urls()

if __name__ == "__main__":
    fetch_urls()
