"""Configuration constants for URL fetching and processing utilities."""

# === URLs ===
TRANCOLIST_URL = "https://tranco-list.eu/top-1m.csv.zip"
WIKIMEDIA_URL = "https://commons.wikimedia.org/w/api.php"
OPENPHISH_URL = 'https://openphish.com/feed.txt'
PHISHTANK_URL = 'http://data.phishtank.com/data/online-valid.json'
COMMON_CRAWL_S3_PATHS = [
    "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/segments/1736703362541.8/warc/CC-MAIN-20250120010617-20250120040617-00289.warc.gz",
    "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/segments/1736703363113.38/warc/CC-MAIN-20250121070313-20250121100313-00165.warc.gz",
    "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/segments/1736703361941.29/warc/CC-MAIN-20250126135402-20250126165402-00004.warc.gz",
    "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/segments/1736703365567.50/warc/CC-MAIN-20250128103419-20250128133419-00210.warc.gz",
]

# === Output ===
OUTPUT_CSV_GZ = "data/raw/labeled_crawl.csv.gz"

# === Data Processing ===
TRANCO_TOP_N = 1000000
WIKIMEDIA_CATEGORY_NAMES = ["PNG_files", "JPG_files", "SVG_files", "GIF_files"]
WIKIMEDIA_VALID_EXTENSIONS = [".png", ".jpg", ".svg", ".gif"]
WIKIMEDIA_LIMIT = 35
WIKIPEDIA_SEED_PAGES = [
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
WIKIPEDIA_BASE_URL = "https://en.wikipedia.org/wiki/"
GITHUB_PAGES = [
    "https://github.com/",
    "https://pages.github.com/",
    "https://github.blog/",
    "https://education.github.com/",
    "https://github.com/features/pages"
]

# === Synthetic URLs ===
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

SUSPICIOUS_BENIGN_KEYWORDS = [
    "reset",
    "download",
    "profile",
    "account",
    "settings",
    "view",
    "cart",
    "checkout",
    "support",
    "help",
    "faq",
    "blog",
    "news",
    "forum",
    "order", "contact",
    "about", "search",
    "gallery", "events",
    "newsletter",
    "api"]