# Configuration for URL model training and deployment

# === Model & Training Hyperparameters ===
TEST_SIZE = 0.2
RANDOM_STATE = 42


# === Model Parameters for Teacher (XGBoost) ===
XGB_PARAMS = {
    "eval_metric":    "logloss",
    "random_state":   RANDOM_STATE,
    "n_estimators":   120,         # cut in half → faster & smaller
    "max_depth":      6,           # shallower trees
    "subsample":      0.8,         # row subsampling for variance reduction
    "colsample_bytree":0.8,        # feature subsampling 
    "reg_alpha":      1,         # L1 regularization
    "reg_lambda":     2        # L2 regularization
}


# === Feature List ===
FEATURES = [
    'url_length', 'path_depth', 'num_subdomains', 'num_special_chars',
    'num_digits', 'num_hyphens', 'has_at_symbol', 'num_query_params',
    'digit_ratio', 'url_entropy',
    'has_https', 'levenshtein_to_brand',
    'uncommon_tld', 'url_token_count',
]


BRAND_LIST = [
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

COUNTRY_TLDS = {
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

COMMON_TLDS = {"com", "org", "net", "edu", "gov", "info", "io", "co"}

REDIRECT_KEYS = ["redirect", "next", "url", "dest", "destination", "continue"]


