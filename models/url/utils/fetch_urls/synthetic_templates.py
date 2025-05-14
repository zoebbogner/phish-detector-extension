# Reusable templates for synthetic benign URL generation

import random
import re
from faker import Faker

PATH_EXTENSIONS = [
    "/cart",
    "/checkout",
    "/support/ticket",
    "/products/view",
    "/account/settings",
    "/user/profile",
    "/download",
    "/reset/password",
    "/help/faq",
    "/blog/article",
    "/news/latest",
    "/forum/thread",
    "/order/history",
    "/contact",
    "/about/company",
    "/search/results",
    "/gallery/image",
    "/events/upcoming",
    "/newsletter/subscribe",
    "/api/v1/resource"
]

QUERY_PARAM_TEMPLATES = [
    "?id=123",
    "?q=reset&page=2",
    "?ref=homepage",
    "?user=admin",
    "?token=abcdef",
    "?session=xyz",
    "?download=true",
    "?profile=public",
    "?lang=en",
    "?sort=asc",
    "?filter=active",
    "?type=basic",
    "?category=tech",
    "?search=login",
    "?page=1",
    "?tab=overview",
    "?redirect=dashboard",
    "?action=update",
    "?view=compact",
    "?mode=edit"
]

def enrich_tranco_domains(domains: list[str], n_paths_per_domain: int = 1) -> list[str]:
    """
    Enrich Tranco domains with realistic paths and queries for each domain, but keep 5-10% as plain https://domain URLs.
    """
    random.seed(42)
    Faker.seed(42)
    faker = Faker()
    suspicious_benign_keywords = [
        "reset", "download", "profile", "account", "settings", "view", "cart", "checkout", "support", "help", "faq", "blog", "news", "forum", "order", "contact", "about", "search", "gallery", "events", "newsletter", "api"
    ]
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
                path_depth = random.randint(1, 5)
                path_parts = [random.choice(suspicious_benign_keywords) for _ in range(path_depth)]
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