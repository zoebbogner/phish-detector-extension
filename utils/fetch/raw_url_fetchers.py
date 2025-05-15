"""
Fetch URLs from various sources and return as lists of URLs (raw).
"""
from typing import List
import io 
import zipfile
import requests 
import pandas as pd
from bs4 import BeautifulSoup
from utils.fetch.config import (
    TRANCOLIST_URL, TRANCO_TOP_N, WIKIPEDIA_SEED_PAGES, WIKIPEDIA_BASE_URL, GITHUB_PAGES,
    OPENPHISH_URL, PHISHTANK_URL
)
from utils.fetch.session import get

def fetch_tranco_domains(top_n: int = TRANCO_TOP_N) -> List[str]:
    """Fetch top N domains from Tranco and return as a list of domains (no enrichment)."""
    try:
        resp = get(TRANCOLIST_URL)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            with z.open(z.namelist()[0]) as f:
                df = pd.read_csv(f, header=None, names=["rank", "domain"])
                domains = [str(d).strip() for d in df["domain"].head(top_n) if isinstance(d, str) and str(d).strip()]
        
        domains = [f"https://{d}" for d in domains]
        
        return domains
    except (requests.RequestException, zipfile.BadZipFile, pd.errors.ParserError, FileNotFoundError) as e:
        print(f"[ERROR] Failed to fetch Tranco list: {e}")
        return []

def fetch_wikipedia_urls(max_links_per_page: int = 50) -> List[str]:
    """Fetch Wikipedia URLs from seed pages, extract up to max_links_per_page per page (raw URLs only)."""
    base_url = WIKIPEDIA_BASE_URL.rstrip("/")
    all_urls = []
    for seed in WIKIPEDIA_SEED_PAGES:
        url = f"{base_url}/{seed}"
        try:
            resp = get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            links = [a.get("href") for a in soup.find_all("a", href=True)]
            wiki_links = [l for l in links if l.startswith("/wiki/") and ":" not in l]
            wiki_links = wiki_links[:max_links_per_page]
            full_urls = [f"{WIKIPEDIA_BASE_URL.rstrip('/')}{l}" for l in wiki_links]
            all_urls.extend(full_urls)
        except (requests.RequestException, FileNotFoundError) as e:
            print(f"[ERROR] Failed to fetch Wikipedia page {seed}: {e}")
            
    return all_urls

def fetch_github_pages() -> List[str]:
    """Return a list of predefined GitHub Pages URLs (raw)."""
    return list(GITHUB_PAGES) if GITHUB_PAGES else []

def fetch_openphish_urls() -> List[str]:
    """Fetch phishing URLs from OpenPhish and return as a list of URLs (raw)."""
    print("[INFO] Fetching OpenPhish URLs (raw)...")
    try:
        resp = get(OPENPHISH_URL)
        resp.raise_for_status()
        urls = [line.strip() for line in resp.text.splitlines() if line.strip()]
        return urls
    except (requests.RequestException, FileNotFoundError) as e:
        print(f"[ERROR] Failed to fetch from OpenPhish: {e}")
        return []

def fetch_phishtank_urls() -> List[str]:
    """Fetch phishing URLs from PhishTank API and return as a list of URLs (raw)."""
    try:
        resp = get(PHISHTANK_URL)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            with z.open(z.namelist()[0]) as f:
                df = pd.read_json(f)
                if 'url' not in df.columns:
                    print("[ERROR] 'url' column not found in PhishTank data.")
                    return []
                urls = df['url'].dropna().unique().tolist()
                
        return urls
    except (requests.RequestException, zipfile.BadZipFile, pd.errors.ParserError, FileNotFoundError) as e:
        print(f"[ERROR] Failed to fetch from PhishTank: {e}")
        return []