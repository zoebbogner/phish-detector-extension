# content_feature_extractor.py

import re
import requests
from lxml import html, etree
import numpy as np
from concurrent.futures import ThreadPoolExecutor

class ContentFeatureExtractor:
    """
    Concurrent, XPath-optimized content feature extractor.

    Extracted features per URL:
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
    """
    def __init__(self, suspicious_tokens=None, timeout=5.0, headers=None, max_workers=10):
        tokens = suspicious_tokens or [
            'login','signin','secure','account','update','verify',
            'bank','confirm','payment'
        ]
        self._suspicious_re = re.compile('|'.join(tokens), re.IGNORECASE)
        self.session = requests.Session()
        self.session.headers.update(headers or {
            'User-Agent': 'PhishExt/1.0 (+https://yourdomain.com)'
        })
        self.timeout = timeout
        self.max_workers = max_workers

        # Precompile XPath expressions for performance
        self._xpaths = {
            'links': etree.XPath('//a'),
            'external_links': etree.XPath('//a[starts-with(translate(@href, "HTTP", "http"), "http")]'),
            'forms': etree.XPath('//form'),
            'inputs': etree.XPath('//input'),
            'scripts': etree.XPath('//script'),
            'external_scripts': etree.XPath('//script[starts-with(translate(@src, "HTTP", "http"), "http")]'),
            'iframes': etree.XPath('//iframe'),
            'images': etree.XPath('//img'),
            'onclicks': etree.XPath('count(//@onclick)'),
            'onmouseovers': etree.XPath('count(//@onmouseover)'),
            'meta_refresh': etree.XPath('count(//meta[translate(@http-equiv, "REFRESH", "refresh")="refresh"])'),
            'event_handlers': etree.XPath('count(//@*[starts-with(local-name(), "on")])')
        }

    def fit(self, X, y=None):
        return self

    def _extract_features(self, url):
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            tree = html.fromstring(resp.text)
        except Exception:
            # On error, return zeroed feature vector
            return [0] * 17

        # Extract counts using compiled XPaths
        num_links              = len(self._xpaths['links'](tree))
        num_external_links     = len(self._xpaths['external_links'](tree))
        num_forms              = len(self._xpaths['forms'](tree))
        num_inputs             = len(self._xpaths['inputs'](tree))
        num_hidden_inputs      = len([i for i in self._xpaths['inputs'](tree) if i.get('type','').lower()=='hidden'])
        num_password_inputs    = len([i for i in self._xpaths['inputs'](tree) if i.get('type','').lower()=='password'])
        ratio_password_inputs  = num_password_inputs / num_inputs if num_inputs > 0 else 0
        num_scripts            = len(self._xpaths['scripts'](tree))
        num_external_scripts   = len(self._xpaths['external_scripts'](tree))
        num_iframes            = len(self._xpaths['iframes'](tree))
        num_non_sandbox_iframes= len([i for i in self._xpaths['iframes'](tree) if 'sandbox' not in i.attrib])
        num_images             = len(self._xpaths['images'](tree))
        num_event_handlers     = int(self._xpaths['event_handlers'](tree))
        num_onclick_attrs      = int(self._xpaths['onclicks'](tree))
        num_onmouseover_attrs  = int(self._xpaths['onmouseovers'](tree))
        num_meta_refresh       = int(self._xpaths['meta_refresh'](tree))
        text = tree.text_content() or ""
        suspicious_word_count  = len(self._suspicious_re.findall(text))

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

    def transform(self, urls):
        # Process URLs concurrently to improve throughput
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            features = list(executor.map(self._extract_features, urls))
        return np.array(features)
