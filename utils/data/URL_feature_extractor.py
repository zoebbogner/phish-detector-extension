# URL_feature_extractor.py

import re
import math
from urllib.parse import urlparse
import pandas as pd

class URLFeatureExtractor:
    """
    Vectorized URL feature extractor using pandas.
    Features:
      - url_length
      - path_depth
      - domain_length
      - num_subdomains
      - num_special_chars
      - num_digits
      - num_hyphens
      - has_at_symbol
      - query_length
      - num_query_params
      - contains_ip
      - digit_ratio
      - url_entropy
      - suspicious_word_count
      - has_https
      - dot_count
      - punycode_present
      - port_present
      - num_uppercase
      - longest_special_sequence
    """
    def __init__(self):
        self._special_re = re.compile(r'[^A-Za-z0-9]')
        self._digit_re = re.compile(r'\d')
        self._hyphen_re = re.compile(r'-')
        self._ip_re = re.compile(r'^(?:\d{1,3}\.){3}\d{1,3}$')
        self._suspicious_pattern = re.compile(
            r'login|signin|secure|account|update|verify|ebayisapi|webscr',
            re.IGNORECASE
        )
        self._uppercase_re = re.compile(r'[A-Z]')


    def fit(self, X, y=None):
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

    def _longest_special_seq(self, s: str) -> int:
        max_seq = curr = 0
        for ch in s:
            if self._special_re.match(ch):
                curr += 1
                max_seq = max(max_seq, curr)
            else:
                curr = 0
        return max_seq

    def transform(self, X):
        s = pd.Series(X, dtype=str)

        # basic lexical features
        url_length   = s.str.len()
        paths        = s.apply(lambda u: urlparse(u).path)
        # ignore empty segments and trailing slash
        path_depth   = paths.str.strip('/').str.count('/')
        domains      = s.apply(lambda u: urlparse(u).netloc.lower())
        domain_length= domains.str.len()
        num_subdomains = domains.str.count(r'\.') - 1
        num_special_chars = s.apply(lambda u: len(self._special_re.findall(u)))
        num_digits   = s.apply(lambda u: len(self._digit_re.findall(u)))
        num_hyphens  = s.apply(lambda u: len(self._hyphen_re.findall(u)))
        has_at_symbol= s.str.contains(r'@').astype(int)

        # query features
        queries      = s.apply(lambda u: urlparse(u).query)
        query_length = queries.str.len()
        num_query_params = queries.str.split('&').apply(
            lambda parts: len([p for p in parts if p])
        )

        # ratios and entropies
        contains_ip  = domains.apply(lambda d: 1 if self._ip_re.match(d) else 0)
        digit_ratio  = num_digits / url_length.replace(0, 1)
        url_entropy  = s.apply(self._shannon_entropy)
        suspicious_word_count = s.apply(
            lambda u: len(self._suspicious_pattern.findall(u))
        )

        # newly added host/protocol features
        has_https       = s.str.lower().str.startswith('https://').astype(int)
        dot_count       = domains.str.count(r'\.')
        punycode_present= domains.str.contains('xn--').astype(int)
        port_present    = domains.apply(
            lambda d: 1 if (':' in d and not d.endswith(':')) else 0
        )
        num_uppercase   = s.apply(lambda u: len(self._uppercase_re.findall(u)))
        longest_special_sequence = s.apply(self._longest_special_seq)

        # assemble DataFrame
        features = pd.concat([
            url_length.rename('url_length'),
            path_depth.rename('path_depth'),
            domain_length.rename('domain_length'),
            num_subdomains.rename('num_subdomains'),
            num_special_chars.rename('num_special_chars'),
            num_digits.rename('num_digits'),
            num_hyphens.rename('num_hyphens'),
            has_at_symbol.rename('has_at_symbol'),
            query_length.rename('query_length'),
            num_query_params.rename('num_query_params'),
            contains_ip.rename('contains_ip'),
            digit_ratio.rename('digit_ratio'),
            url_entropy.rename('url_entropy'),
            suspicious_word_count.rename('suspicious_word_count'),
            has_https.rename('has_https'),
            dot_count.rename('dot_count'),
            punycode_present.rename('punycode_present'),
            port_present.rename('port_present'),
            num_uppercase.rename('num_uppercase'),
            longest_special_sequence.rename('longest_special_sequence'),
        ], axis=1)

        return features.values
    