import re
import math
from urllib.parse import urlparse
import pandas as pd

class URLFeatureExtractor:
    """
    Efficient, vectorized URL feature extractor using pandas.
    Features:
      - url_length
      - path_depth
      - domain_length
      - num_subdomains
      - num_special_chars
      - num_digits
      - num_hyphens
      - num_underscores
      - has_at_symbol
      - query_length
      - num_query_params
      - contains_ip
      - digit_ratio
      - url_entropy
      - suspicious_word_count
    """
    def __init__(self):
        # Precompile regex for performance
        self._special_re = re.compile(r'[^A-Za-z0-9]')
        self._digit_re = re.compile(r'\d')
        self._hyphen_re = re.compile(r'-')
        self._underscore_re = re.compile(r'_')
        self._ip_re = re.compile(r'^(?:\d{1,3}\.){3}\d{1,3}$')
        # Suspicious tokens often used in phishing URLs
        tokens = ['login', 'signin', 'secure', 'account', 'update', 'verify', 'ebayisapi', 'webscr']
        self._suspicious_pattern = re.compile('|'.join(tokens), re.IGNORECASE)

    def fit(self, X, y=None):
        # No fitting required
        return self

    def _shannon_entropy(self, s: str) -> float:
        if not s:
            return 0.0
        freq = {}
        for ch in s:
            freq[ch] = freq.get(ch, 0) + 1
        entropy = 0.0
        length = len(s)
        for count in freq.values():
            p = count / length
            entropy -= p * math.log2(p)
        return entropy

    def transform(self, X):
        s = pd.Series(X, dtype=str)

        # Core features
        url_length = s.str.len()
        paths = s.apply(lambda u: urlparse(u).path)
        path_depth = paths.str.split('/').apply(lambda segs: sum(bool(seg) for seg in segs))
        domains = s.apply(lambda u: urlparse(u).netloc.lower())
        domain_length = domains.str.len()
        sub_count = domains.str.count(r"\\.") - 1
        num_subdomains = sub_count.clip(lower=0)

        # Additional features
        num_special_chars = s.apply(lambda u: len(self._special_re.findall(u)))
        num_digits = s.apply(lambda u: len(self._digit_re.findall(u)))
        num_hyphens = s.apply(lambda u: len(self._hyphen_re.findall(u)))
        num_underscores = s.apply(lambda u: len(self._underscore_re.findall(u)))
        has_at_symbol = s.str.contains(r'@').astype(int)
        queries = s.apply(lambda u: urlparse(u).query)
        query_length = queries.str.len()
        num_query_params = queries.str.split('&').apply(lambda parts: len([p for p in parts if p]))
        contains_ip = domains.apply(lambda d: 1 if self._ip_re.match(d) else 0)
        digit_ratio = num_digits / url_length.replace(0, 1)
        url_entropy = s.apply(self._shannon_entropy)
        suspicious_word_count = s.apply(lambda u: len(self._suspicious_pattern.findall(u)))

        # Combine all features into DataFrame
        features = pd.concat([
            url_length.rename('url_length'),
            path_depth.rename('path_depth'),
            domain_length.rename('domain_length'),
            num_subdomains.rename('num_subdomains'),
            num_special_chars.rename('num_special_chars'),
            num_digits.rename('num_digits'),
            num_hyphens.rename('num_hyphens'),
            num_underscores.rename('num_underscores'),
            has_at_symbol.rename('has_at_symbol'),
            query_length.rename('query_length'),
            num_query_params.rename('num_query_params'),
            contains_ip.rename('contains_ip'),
            digit_ratio.rename('digit_ratio'),
            url_entropy.rename('url_entropy'),
            suspicious_word_count.rename('suspicious_word_count')
        ], axis=1)

        return features.values