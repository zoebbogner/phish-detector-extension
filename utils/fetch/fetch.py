"""Fetch URLs from all sources (raw, no enrichment).
"""
from utils.fetch.benign import fetch_benign_urls
from utils.fetch.phishing import fetch_phishing_urls

def fetch_all_urls(synthetic_urls: bool = False, n_paths_per_domain: int = 1) -> None:
    """Fetch all URLs from all sources (raw, no enrichment).
    If synthetic_urls is True, the URLs will be enriched with realistic paths and queries.
    """
    fetch_benign_urls(synthetic_urls, n_paths_per_domain)
    fetch_phishing_urls()

if __name__ == "__main__":
    fetch_all_urls(synthetic_urls=False, n_paths_per_domain=1)