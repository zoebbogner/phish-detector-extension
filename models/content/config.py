PROCESSED_PATH = "data/processed/content.csv"  

# === Model & Training Hyperparameters ===
TEST_SIZE = 0.2
RANDOM_STATE = 42

# === Model Parameters for Teacher (XGBoost) ===
XGB_PARAMS = {
    "eval_metric":    "logloss",
    "random_state":   RANDOM_STATE,
    "n_estimators":   120,         # cut in half → faster & smaller
    "max_depth":      8,           # shallower trees
    "subsample":      0.8,         # row subsampling for variance reduction
    "colsample_bytree":0.8,        # feature subsampling 
    "reg_alpha":      1,         # L1 regularization
    "reg_lambda":     2,        # L2 regularization
    "scale_pos_weight": 16.5,
    "min_child_weight": 3,
}

# === File Paths ===
TRAINING_MODEL_PATH = "models/content/results/model.pkl"
EXPORT_JSON_PATH = "models/content/results/logreg_weights.json"
FEATURE_IMPORTANCE_PATH = "models/content/results/feature_importance.png"
CLASSIFICATION_REPORT_PATH = "models/content/results/classification_report.txt"
PRODUCTION_PATH = "models/content/production/content_model.pkl"

# === Google Safe Browsing ===
GOOGLE_SAFEBROWSING_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
REQUEST_TIMEOUT = 10

# === Common Crawl ===
COMMON_CRAWL_S3_PATHS = [
    "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/segments/1736703362541.8/warc/CC-MAIN-20250120010617-20250120040617-00289.warc.gz",
    "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/segments/1736703363113.38/warc/CC-MAIN-20250121070313-20250121100313-00165.warc.gz",
    "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/segments/1736703361941.29/warc/CC-MAIN-20250126135402-20250126165402-00004.warc.gz",
    "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/segments/1736703365567.50/warc/CC-MAIN-20250128103419-20250128133419-00210.warc.gz",
]
BENIGN_QUOTA = 1000000
BENIGN_OUTPUT_CSV = "data/raw/benign_html.csv"
HTML_CSV_FIELDNAMES = ["url", "html", "label"]

FEATURES = [
    "domain_mismatch_link_ratio",
    "external_domain_count",
    "password_field_count",
    "anchor_count",
    "favicon_domain_mismatch",
    "ad_network_asset_count",
    "script_count",
    "suspicious_keyword_count",
    "external_stylesheet_ratio",
    "text_to_html_ratio",
    "input_count",
    "non_https_resource_ratio",
    "redirect_pattern_count",
    "document_text_entropy",
    "title_length"
]
OLD_FEATURES = [
    "html_tag_count",
    "form_count",
    "input_count",
    "anchor_count",
    "script_count",
    "iframe_count",
    "img_count",
    "meta_refresh_count",
    "title_length",
    "text_to_html_ratio",
    "document_text_entropy",
    "suspicious_keyword_count",
    "base64_asset_count",
    "data_uri_asset_count",
    "inline_style_count",
    "password_field_count",
    "hidden_redirect_element_count",
    "external_stylesheet_ratio",
    "non_https_resource_ratio",
    "domain_mismatch_link_ratio",
    "password_reset_link_count",
    "external_resource_count",
    "favicon_domain_mismatch",
    "redirect_pattern_count",
    "external_domain_count",
    "ad_network_asset_count"
]

FEATURE_CSV_FIELDNAMES = FEATURES + ["label"]

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "update", "secure", "account", "signin", "password", "ebayisapi", "webscr"
]
    
AD_NETWORK_DOMAINS = {
    "taboola.com",
    "outbrain.com",
    "revcontent.com",
    "googlesyndication.com",
    "adroll.com",
    "adsrvr.org",           # TheTradeDesk
    "rubiconproject.com",   # Rubicon
    "pubmatic.com",
    "appnexus.com",
    "openx.net",
    "criteo.com",
    "adblade.com",
    "yimg.com",             # Yahoo ads
    "doubleclick.net",
    "yieldmanager.com",
    "yieldmanager.net",
    "yieldmanager.org",
    "yieldmanager.info",
    "yieldmanager.biz",
}

MAX_CACHE_SIZE = 100