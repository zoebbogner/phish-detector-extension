"""
Fetch benign URLs from all sources (raw, no enrichment).
"""
import random
import re
from typing import Optional
from faker import Faker
import pandas as pd
from utils.fetch.config import (
    TRANCO_TOP_N, PATH_EXTENSIONS, QUERY_PARAM_TEMPLATES,
    SUSPICIOUS_BENIGN_KEYWORDS
)
from utils.fetch.data_helpers import build_benign_df, save_to_csv, ensure_data_dir
from utils.fetch.raw_url_fetchers import (
    fetch_tranco_domains, fetch_wikipedia_urls, fetch_github_pages
)
from main_config import BENIGN_CSV, get_benign_csv_dir

def enrich_tranco_domains(domains: list[str], n_paths_per_domain: int = 1) -> list[str]:
    """
    Enrich Tranco domains with realistic paths and queries for each domain, but keep 5-10% as plain https://domain URLs.
    """
    random.seed(42)
    Faker.seed(42)
    faker = Faker()
    urls = []
    plain_ratio = random.uniform(0.05, 0.10)
    for domain in domains:
        for _ in range(n_paths_per_domain):
            # With 5-10% probability, keep as plain domain
            if random.random() < plain_ratio:
                urls.append(f"https://{domain}")
                continue
            # Random path: either from template or random segments
            if random.random() < 0.5:
                path = random.choice(PATH_EXTENSIONS)
            else:
                path_depth = random.randint(1, 10)
                path_parts = [random.choice(SUSPICIOUS_BENIGN_KEYWORDS) for _ in range(path_depth)]
                path = "/" + "/".join(path_parts)
            # Optionally add a query string
            if random.random() < 0.7:
                query_template = random.choice(QUERY_PARAM_TEMPLATES)
                # Replace numbers in query with random values
                query = re.sub(r"\\d+", lambda m: str(random.randint(1, 9999)), query_template)
                # Replace tokens like 'token', 'session', etc. with fake values
                query = re.sub(r"token=[^&]+", f"token={faker.sha1()[:8]}", query)
                query = re.sub(r"session=[^&]+", f"session={faker.uuid4()[:8]}", query)
            else:
                query = ""
            url = f"https://{domain}{path}{query}"
            urls.append(url)
    return urls 

def fetch_benign_urls(synthetic_urls: bool = False, n_paths_per_domain: int = 1) -> tuple[Optional[str], Optional[pd.DataFrame]]:
    """Main function to fetch and save benign URLs from all sources (raw, no enrichment).
    If synthetic_urls is True, the URLs will be enriched with realistic paths and queries.
    """
    print("[INFO] Fetching benign URLs...")
    ensure_data_dir()
    tranco_urls = fetch_tranco_domains(top_n=TRANCO_TOP_N)
    wikipedia_urls = fetch_wikipedia_urls(max_links_per_page=50)
    github_urls = fetch_github_pages()

    dfs = []
    if tranco_urls:
        if synthetic_urls:
            print("[INFO] Enriching Tranco domains with realistic paths and queries...")
            tranco_urls = enrich_tranco_domains(tranco_urls, n_paths_per_domain)
            
        print(f"[INFO] Tranco URLs: {len(tranco_urls)}")
        dfs.append(build_benign_df(tranco_urls, "Tranco"))
    if wikipedia_urls:
        dfs.append(build_benign_df(wikipedia_urls, "Wikipedia"))
    if github_urls:
        dfs.append(build_benign_df(github_urls, "GitHub Pages"))

    if not dfs:
        print("[ERROR] No benign URLs collected from any source.")
        return None, None
    
    all_benign = pd.concat(dfs, ignore_index=True)
    all_benign = all_benign.drop_duplicates(subset=["url"])
    all_benign = all_benign[all_benign["url"].str.startswith("https://")].copy()
    saved_path = save_to_csv(all_benign, BENIGN_CSV, path=get_benign_csv_dir(synthetic_urls=synthetic_urls))
    
    if saved_path:
        print(f"[INFO] Benign URLs saved to {saved_path}")
        print(f"[INFO] Total benign URLs collected: {len(all_benign)}")
    return saved_path, all_benign
