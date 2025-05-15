# URL_feature_extractor.py

import re
import math
from urllib.parse import urlparse
import pandas as pd
import rapidfuzz.distance.Levenshtein as rlev
from models.url.config import COMMON_TLDS, COUNTRY_TLDS, BRAND_LIST, REDIRECT_KEYS
class URLFeatureExtractor:
    """
    Vectorized URL feature extractor using pandas.
    Returns a pandas DataFrame with column names for better model pipeline integration.
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
        self._redirect_keys = REDIRECT_KEYS
        self._redirect_pattern = re.compile(r'(redirect|next|url|dest|destination|continue)=', re.IGNORECASE)
        self._token_split_re = re.compile(r'[\/-_?=&]')
        self._common_tlds = COMMON_TLDS
        self._country_tlds = COUNTRY_TLDS
        self._brand_list = BRAND_LIST
        
        self.feature_names = []
        
    def _shannon_entropy(self, s: str) -> float:
        """Calculate the Shannon entropy of a string."""
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

    def _extract_tld(self, domain: str) -> str:
        """Extract the top-level domain (TLD) from a domain string."""
        parts = domain.rsplit('.', 1)
        return parts[1] if len(parts) == 2 else ''

    def _tld_type(self, tld: str) -> str:
        """Classify the TLD as common, country, suspicious, or unknown."""
        if tld in self._common_tlds:
            return 'common'
        elif tld in self._country_tlds:
            return 'country'
        elif tld:
            return 'suspicious'
        else:
            return 'unknown'

    def _levenshtein_to_brand(self, domain: str) -> int:
        """Compute the minimum Levenshtein distance from the domain to any known brand."""
        # Remove TLD
        domain_main = domain.split('.')[-2] if '.' in domain else domain
        # Use rapidfuzz for Levenshtein distance
        min_dist = min(
            [rlev.distance(domain_main, brand) for brand in self._brand_list]
        )
        return min_dist

    def transform(self, X):
        """Extract features from a list or Series of URLs and return a DataFrame."""
        s = pd.Series(X, dtype=str)

        # basic lexical features
        url_length = s.str.len()
        paths = s.apply(lambda u: urlparse(u).path)
        path_depth = paths.str.strip('/').str.count('/')  # ignore empty segments and trailing slash
        domains = s.apply(lambda u: urlparse(u).netloc.lower())
        num_subdomains = domains.str.count(r'\.') - 1
        num_special_chars = s.apply(lambda u: len(self._special_re.findall(u)))
        num_digits = s.apply(lambda u: len(self._digit_re.findall(u)))
        num_hyphens = s.apply(lambda u: len(self._hyphen_re.findall(u)))
        has_at_symbol = s.str.contains(r'@').astype(int)

        # query features
        queries = s.apply(lambda u: urlparse(u).query)
        num_query_params = queries.str.split('&').apply(lambda parts: len([p for p in parts if p]))

        # ratios and entropies
        digit_ratio = num_digits / url_length.replace(0, 1)
        url_entropy = s.apply(self._shannon_entropy)

        # host/protocol features
        has_https = s.str.lower().str.startswith('https://').astype(int)
        

        # domain analysis features
        tlds = domains.str.rsplit('.', n=1).str.get(-1)
        uncommon_tld = (~tlds.isin(self._common_tlds)).astype(int)
        levenshtein_to_brand = domains.apply(self._levenshtein_to_brand)

        # token analysis features
        tokens = s.apply(lambda u: [tok for tok in self._token_split_re.split(u) if tok])
        url_token_count = tokens.apply(len)

        # assemble DataFrame
        features = pd.concat([
            url_length.rename('url_length'),
            path_depth.rename('path_depth'),
            num_subdomains.rename('num_subdomains'),
            num_special_chars.rename('num_special_chars'),
            num_digits.rename('num_digits'),
            num_hyphens.rename('num_hyphens'),
            has_at_symbol.rename('has_at_symbol'),
            num_query_params.rename('num_query_params'),
            digit_ratio.rename('digit_ratio'),
            url_entropy.rename('url_entropy'),
            has_https.rename('has_https'),
            levenshtein_to_brand.rename('levenshtein_to_brand'),
            uncommon_tld.rename('uncommon_tld'),
            url_token_count.rename('url_token_count'),
        ], axis=1)

        self.feature_names = features.columns.tolist()
        return features
    
