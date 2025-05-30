# settings.py

from models.content.config import FEATURES


#############################
# Logs
#############################
LOG_FILE = "crawl.log"
LOG_LEVEL = "WARNING"
#############################
# User agent
#############################

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
)

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    # (the User-Agent above will be applied automatically)
}
#############################
# Project & Feed Settings
#############################

BOT_NAME = "phishing_crawler"

SPIDER_MODULES = ["phishing_crawler.spiders"]
NEWSPIDER_MODULE = "phishing_crawler.spiders"

# Which CSV columns to export, in order:
SEEDS_CSV = 'phishing_crawler/seeds.csv'
FEED_EXPORT_FIELDS = FEATURES + ['label', 'url']
FEED_EXPORT_ENCODING = "utf-8"

#############################
# Crawl Politeness Settings
#############################


# We’ll fetch robots.txt ourselves if needed, but we won’t let Scrapy auto‐obey it:
ROBOTSTXT_OBEY = False

# Limit total concurrent requests
CONCURRENT_REQUESTS = 8

# Limit concurrent requests per domain to avoid overloading any single host
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Introduce a fixed delay (in seconds) between requests to the same domain
DOWNLOAD_DELAY = 1.5

# Enable AutoThrottle to dynamically adjust rate based on server response times
AUTOTHROTTLE_ENABLED = True
# Initial delay before throttling kicks in
AUTOTHROTTLE_START_DELAY = 1.0
# Maximum delay between two requests when hitting high latencies
AUTOTHROTTLE_MAX_DELAY = 10.0
# Aim to send an average of 1 concurrent request per remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Turn off debug logging for AutoThrottle (set to True to see throttling stats)
AUTOTHROTTLE_DEBUG = False

#############################
# Other Defaults (uncomment/customize as needed)
#############################

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override request headers:
# DEFAULT_REQUEST_HEADERS = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "Accept-Language": "en",
# }

# ITEM_PIPELINES = {
#     "phishing_crawler.pipelines.PhishingCrawlerPipeline": 300,
# }

# HTTP cache (disable or tune):
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"