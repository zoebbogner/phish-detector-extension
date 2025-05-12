#!/usr/bin/env python3
"""
Fetch benign URLs from Tranco, Wikipedia, and GitHub Pages, label and save as CSV using helpers.
"""
from typing import Optional
import random
import argparse
import io
import zipfile
import requests
import pandas as pd
from bs4 import BeautifulSoup
from faker import Faker

from utils.data.constants import (
    WIKIPEDIA_SEED_PAGES, GITHUB_PAGES, BENIGN_CSV, TRANCOLIST_URL,
    WIKIPEDIA_BASE_URL
)
from utils.data.url_synthetic_templates import PATH_EXTENSIONS, QUERY_PARAM_TEMPLATES, enrich_tranco_domains
from utils.data.data_helpers import ensure_data_dir, build_benign_df, save_to_csv



def fetch_tranco_urls(top_n: int = 100000) -> Optional[pd.DataFrame]:
    """Fetch top N domains from Tranco, enrich with realistic paths/queries, and return as DataFrame."""
    print(f"[INFO] Fetching Tranco top {top_n} domains...")
    try:
        resp = requests.get(TRANCOLIST_URL, timeout=30)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            with z.open(z.namelist()[0]) as f:
                df = pd.read_csv(f, header=None, names=["rank", "domain"])
                domains = [str(d).strip() for d in df["domain"].head(top_n) if isinstance(d, str) and str(d).strip()]
                urls = enrich_tranco_domains(domains)
        print(f"[INFO] Retrieved {len(urls)} enriched Tranco URLs.")
        return build_benign_df(urls, "Tranco")
    except (requests.RequestException, zipfile.BadZipFile, pd.errors.ParserError) as e:
        print(f"[ERROR] Failed to fetch Tranco list: {e}")
        return None


def fetch_wikipedia_urls(max_links_per_page: int = 50) -> Optional[pd.DataFrame]:
    """Fetch Wikipedia URLs from seed pages, extract up to max_links_per_page per page."""
    print("[INFO] Fetching Wikipedia URLs from seed pages...")
    base_url = WIKIPEDIA_BASE_URL.rstrip("/")
    all_urls = []
    for seed in WIKIPEDIA_SEED_PAGES:
        url = f"{base_url}/{seed}"
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            links = [a.get("href") for a in soup.find_all("a", href=True)]
            wiki_links = [l for l in links if l.startswith("/wiki/") and ":" not in l]
            wiki_links = wiki_links[:max_links_per_page]
            full_urls = [f"{WIKIPEDIA_BASE_URL.rstrip('/')}{l}" for l in wiki_links]
            all_urls.extend(full_urls)
            print(f"[INFO] {seed}: {len(full_urls)} links fetched.")
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch Wikipedia page {seed}: {e}")
    if all_urls:
        print(f"[INFO] Total Wikipedia URLs collected: {len(all_urls)}")
        return build_benign_df(all_urls, "Wikipedia")
    else:
        return None


def fetch_github_pages() -> Optional[pd.DataFrame]:
    """Return a DataFrame of predefined GitHub Pages URLs."""
    print("[INFO] Using predefined GitHub Pages URLs...")
    if GITHUB_PAGES:
        return build_benign_df(GITHUB_PAGES, "GitHub Pages")
    else:
        print("[WARN] No GitHub Pages URLs defined.")
        return None


def generate_synthetic_benign_urls(n: int = 20000, seed: int = 42) -> list[str]:
    """Generate a list of synthetic benign URLs using Faker and templates."""
    faker = Faker()
    random.seed(seed)
    Faker.seed(seed)
    suspicious_benign_keywords = ["reset", "download", "profile", "account", "settings", "view", "cart", "checkout", "support", "help", "faq", "blog", "news", "forum", "order", "contact", "about", "search", "gallery", "events", "newsletter", "api"]
    urls = []
    for _ in range(n):
        domain = faker.domain_name()
        # Random path depth 1-10
        path_depth = random.randint(1, 10)
        path_parts = [random.choice(suspicious_benign_keywords) for _ in range(path_depth)]
        # Sometimes use a template extension
        if random.random() < 0.5:
            path = random.choice(PATH_EXTENSIONS)
        else:
            path = "/" + "/".join(path_parts)
        # Sometimes add a query string
        if random.random() < 0.7:
            query = random.choice(QUERY_PARAM_TEMPLATES)
        else:
            query = ""
        url = f"https://{domain}{path}{query}"
        urls.append(url)
    return urls


def main() -> tuple[Optional[str], Optional[pd.DataFrame]]:
    """Main function to fetch and save benign URLs from all sources."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-synthetic", action="store_true", help="Include synthetic benign URLs")
    args = parser.parse_args()

    ensure_data_dir()
    tranco_df = fetch_tranco_urls(top_n=1000000)
    wikipedia_df = fetch_wikipedia_urls(max_links_per_page=50)
    github_df = fetch_github_pages()

    dfs: list[pd.DataFrame] = [df for df in [tranco_df, wikipedia_df, github_df] if df is not None]

    # Synthetic URLs
    if args.include_synthetic:
        synthetic_urls = generate_synthetic_benign_urls(n=100000)
        synthetic_df = pd.DataFrame({
            "url": [u for u in synthetic_urls if u.startswith("https://")],
            "label": 0,
        })
        dfs.append(synthetic_df)
        print(f"[INFO] Synthetic URLs generated and included: {len(synthetic_df)}")

    if not dfs:
        print("[ERROR] No benign URLs collected from any source.")
        return None, None
    all_benign = pd.concat(dfs, ignore_index=True)
    all_benign = all_benign.drop_duplicates(subset=["url"])
    # Filter only valid https URLs
    all_benign = all_benign[all_benign["url"].str.startswith("https://")].copy()
    saved_path = save_to_csv(all_benign, BENIGN_CSV)
    if saved_path:
        print(f"[INFO] Benign URLs saved to {saved_path}")
        print(f"[INFO] Total benign URLs collected: {len(all_benign)}")
        
    return saved_path, all_benign


if __name__ == "__main__":
    main() 