# URL_feature_extractor.py

import re
import math
from urllib.parse import urlparse
import pandas as pd
import rapidfuzz.distance.Levenshtein as rlev
from utils.ml_helpers import should_check_levenshtein
class URLFeatureExtractor:
    """
    Vectorized URL feature extractor using pandas.
    Returns a pandas DataFrame with column names for better model pipeline integration.
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
      - tld_type (one-hot encoded)
      - levenshtein_to_brand
      - uncommon_tld
      - url_token_count
      - avg_token_length
      - has_redirect_chain_pattern
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
        self._redirect_keys = ["redirect", "next", "url", "dest", "destination", "continue"]
        self._redirect_pattern = re.compile(r'(redirect|next|url|dest|destination|continue)=', re.IGNORECASE)
        self._token_split_re = re.compile(r'[\/-_?=&]')
        self._common_tlds = {"com", "org", "net", "edu", "gov", "info", "io", "co"}
        self._country_tlds = {
            "uk", "de", "fr", "cn", "ru", "jp", "br", "in", "au", "ca", "us", "es", "it",
            "nl", "se", "no", "fi", "pl", "tr", "ch", "be", "at", "dk", "kr", "mx", "ar",
            "za", "gr", "pt", "cz", "hu", "ro", "il", "nz", "ie", "sg", "hk", "id", "my",
            "th", "ph", "vn", "sa", "ae", "ir", "eg", "pk", "bd", "ua", "by", "kz", "sk",
            "bg", "lt", "lv", "ee", "si", "hr", "rs", "cl", "co", "pe", "ve", "ec", "uy",
            "bo", "py", "do", "cr", "gt", "hn", "ni", "sv", "pa", "cu", "pr", "jm", "tt",
            "bs", "bb", "ag", "lc", "gd", "kn", "vc", "dm", "ai", "bm", "ky", "ms", "tc",
            "vg", "vi", "mq", "gp", "re", "yt", "pm", "wf", "pf", "nc", "tf", "bl", "mf",
            "sx", "cw", "bq", "aw", "sr", "gy", "fk", "gs", "aq", "bv", "hm", "io", "sh",
            "ac", "pn", "tk", "to", "tv", "ws", "as", "ck", "nu", "sb", "tl", "fm", "mh",
            "nr", "pw", "ki", "cc", "cx", "nf", "um", "mp", "gu", "vu"
        }
        self._brand_list = [
            "google", "facebook", "apple", "amazon", "microsoft", "paypal", "bank", "yahoo",
            "instagram", "linkedin", "twitter", "github", "dropbox", "adobe", "netflix",
            "whatsapp", "tiktok", "snapchat", "reddit", "ebay", "wellsfargo", "chase", "boa",
            "hsbc", "citi", "capitalone", "americanexpress", "discover", "samsung", "icloud",
            "outlook", "office", "mail", "gmail", "hotmail", "aol", "yandex", "baidu", "alibaba",
            "jd", "weibo", "wechat", "taobao", "tmall", "bing", "duckduckgo", "yahoo", "live",
            "skype", "slack", "zoom", "airbnb", "booking", "expedia", "uber", "lyft", "doordash",
            "grubhub", "stripe", "square", "venmo", "coinbase", "binance", "kraken", "robinhood",
            "etrade", "fidelity", "vanguard", "tdameritrade", "schwab", "sofi", "mint", "intuit",
            "turbotax", "hulu", "spotify", "pandora", "soundcloud", "imdb", "pinterest", "quora",
            "tumblr", "wordpress", "blogger", "medium", "wikipedia", "wikimedia"]
        self.feature_names = [
            'url_length',
            'path_depth',
            'num_subdomains',
            'num_special_chars',
            'num_digits',
            'num_hyphens',
            'has_at_symbol',
            'query_length',
            'num_query_params',
            'contains_ip',
            'digit_ratio',
            'url_entropy',
            'suspicious_word_count',
            'has_https',
            'punycode_present',
            'longest_special_sequence',
            'tld_type',
            'levenshtein_to_brand',
            'uncommon_tld',
            'url_token_count',
            'avg_token_length',
            'has_redirect_chain_pattern'
        ]
        
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

    def _extract_tld(self, domain: str) -> str:
        parts = domain.rsplit('.', 1)
        return parts[1] if len(parts) == 2 else ''

    def _tld_type(self, tld: str) -> str:
        if tld in self._common_tlds:
            return 'common'
        elif tld in self._country_tlds:
            return 'country'
        elif tld:
            return 'suspicious'
        else:
            return 'unknown'

    def _levenshtein_to_brand(self, domain: str) -> int:
        if not should_check_levenshtein(domain):
            return 100
        # Remove TLD
        domain_main = domain.split('.')[-2] if '.' in domain else domain
        # Use rapidfuzz for Levenshtein distance
        min_dist = min(
            [rlev.distance(domain_main, brand) for brand in self._brand_list]
        )
        return min_dist

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

        tlds = domains.apply(self._extract_tld)
        tld_type = tlds.apply(self._tld_type)
        tld_type_encoded = pd.get_dummies(tld_type, prefix="tld_type")
        uncommon_tld = (~tlds.isin(self._common_tlds)).astype(int)
        levenshtein_to_brand = domains.apply(self._levenshtein_to_brand)
        tokens = s.apply(lambda u: [tok for tok in self._token_split_re.split(u) if tok])
        url_token_count = tokens.apply(len)
        avg_token_length = tokens.apply(lambda toks: sum(len(t) for t in toks) / len(toks) if toks else 0)
        has_redirect_chain_pattern = queries.apply(lambda q: 1 if self._redirect_pattern.search(q) else 0)

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
            tld_type_encoded,
            levenshtein_to_brand.rename('levenshtein_to_brand'),
            uncommon_tld.rename('uncommon_tld'),
            url_token_count.rename('url_token_count'),
            avg_token_length.rename('avg_token_length'),
            has_redirect_chain_pattern.rename('has_redirect_chain_pattern'),
        ], axis=1)

        return features
    
