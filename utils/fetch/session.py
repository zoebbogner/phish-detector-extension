import requests
from requests.adapters import HTTPAdapter, Retry

# Centralized session with retry/back-off and custom headers
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; PhishDetector/1.0; +https://github.com/zoebbogner/phish-detector-extension)"
})
DEFAULT_TIMEOUT = 20

def get(url, **kwargs):
    """Centralized GET with default timeout and retry/back-off."""
    timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)
    return session.get(url, timeout=timeout, **kwargs) 