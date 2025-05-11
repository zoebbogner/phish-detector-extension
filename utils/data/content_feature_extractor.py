import re
import requests
from lxml import html, etree
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

class ContentFeatureExtractor:
    """
    Concurrent, XPath-optimized content feature extractor with TF-IDF support.

    Extracted structural features per URL:
      - num_links
      - num_external_links
      - num_forms
      - num_inputs
      - num_hidden_inputs
      - num_password_inputs
      - ratio_password_inputs
      - num_scripts
      - num_external_scripts
      - num_iframes
      - num_non_sandbox_iframes
      - num_images
      - num_event_handlers
      - num_onclick_attrs
      - num_onmouseover_attrs
      - num_meta_refresh
      - suspicious_word_count

    TF-IDF features on cleaned page text.
    """
    def __init__(
        self,
        suspicious_tokens=None,
        timeout: float = 5.0,
        headers: dict | None = None,
        max_workers: int = 10,
        tfidf_params: dict | None = None
    ):
        # Suspicious token regex
        tokens = suspicious_tokens or [
            'login','signin','secure','account','update','verify',
            'bank','confirm','payment'
        ]
        self._suspicious_re = re.compile('|'.join(tokens), re.IGNORECASE)

        # HTTP session
        self.session = requests.Session()
        self.session.headers.update(headers or {
            'User-Agent': 'PhishExt/1.0 (+https://yourdomain.com)'
        })
        self.timeout = timeout
        self.max_workers = max_workers

        # Precompile XPath expressions for performance
        self._xpaths = {
            'links': etree.XPath('//a'),
            'external_links': etree.XPath(
                '//a[starts-with(translate(@href, "HTTP", "http"), "http")]'
            ),
            'forms': etree.XPath('//form'),
            'inputs': etree.XPath('//input'),
            'scripts': etree.XPath('//script'),
            'external_scripts': etree.XPath(
                '//script[starts-with(translate(@src, "HTTP", "http"), "http")]'
            ),
            'iframes': etree.XPath('//iframe'),
            'images': etree.XPath('//img'),
            'onclicks': etree.XPath('count(//@onclick)'),
            'onmouseovers': etree.XPath('count(//@onmouseover)'),
            'meta_refresh': etree.XPath(
                'count(//meta[translate(@http-equiv, "REFRESH", "refresh")="refresh"])'
            ),
            'event_handlers': etree.XPath('count(//@*[starts-with(local-name(), "on")])')
        }

        # TF-IDF setup
        default_tfidf = {
            "ngram_range": (1, 2),
            "max_df": 0.8,
            "min_df": 5,
            "max_features": 10_000
        }
        self.tfidf_params = tfidf_params or default_tfidf
        self.vectorizer: TfidfVectorizer = TfidfVectorizer(**self.tfidf_params)

    def fit(self, X=None, y=None):
        return self

    def _extract_features(self, url: str) -> list[float]:
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            tree = html.fromstring(resp.text)
        except Exception:
            return [0] * 17

        # Structural feature extraction
        num_links = len(self._xpaths['links'](tree))
        num_external_links = len(self._xpaths['external_links'](tree))
        num_forms = len(self._xpaths['forms'](tree))
        num_inputs = len(self._xpaths['inputs'](tree))
        num_hidden_inputs = len([
            i for i in self._xpaths['inputs'](tree)
            if i.get('type','').lower() == 'hidden'
        ])
        num_password_inputs = len([
            i for i in self._xpaths['inputs'](tree)
            if i.get('type','').lower() == 'password'
        ])
        ratio_password_inputs = (
            num_password_inputs / num_inputs if num_inputs > 0 else 0
        )
        num_scripts = len(self._xpaths['scripts'](tree))
        num_external_scripts = len(self._xpaths['external_scripts'](tree))
        num_iframes = len(self._xpaths['iframes'](tree))
        num_non_sandbox_iframes = len([
            i for i in self._xpaths['iframes'](tree)
            if 'sandbox' not in i.attrib
        ])
        num_images = len(self._xpaths['images'](tree))
        num_event_handlers = int(self._xpaths['event_handlers'](tree))
        num_onclick_attrs = int(self._xpaths['onclicks'](tree))
        num_onmouseover_attrs = int(self._xpaths['onmouseovers'](tree))
        num_meta_refresh = int(self._xpaths['meta_refresh'](tree))

        # Suspicious word count in raw text
        text = tree.text_content() or ""
        suspicious_word_count = len(self._suspicious_re.findall(text))

        return [
            num_links,
            num_external_links,
            num_forms,
            num_inputs,
            num_hidden_inputs,
            num_password_inputs,
            ratio_password_inputs,
            num_scripts,
            num_external_scripts,
            num_iframes,
            num_non_sandbox_iframes,
            num_images,
            num_event_handlers,
            num_onclick_attrs,
            num_onmouseover_attrs,
            num_meta_refresh,
            suspicious_word_count
        ]

    def transform(self, urls: list[str]) -> np.ndarray:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            features = list(executor.map(self._extract_features, urls))
        return np.array(features)

    def _fetch_html(self, url: str, timeout: float = 5.0) -> str:
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception:
            return ""

    def _clean_text(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "iframe", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        return re.sub(r"\s+", " ", text).strip()

    def fetch_and_clean(self, url: str) -> str:
        html = self._fetch_html(url, timeout=self.timeout)
        return self._clean_text(html) if html else ""

    def fit_tfidf(self, texts: list[str]):
        return self.vectorizer.fit_transform(texts)

    def transform_tfidf(self, texts: list[str]):
        return self.vectorizer.transform(texts)

    def save_vectorizer(self, path: str):
        joblib.dump(self.vectorizer, path)

    def load_vectorizer(self, path: str):
        self.vectorizer = joblib.load(path)
