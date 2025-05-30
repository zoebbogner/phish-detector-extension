// URL Feature Extractor for JavaScript
// Mirrors the features from models/url/utils/feature_extractor.py

const COMMON_TLDS = new Set(["com", "org", "net", "edu", "gov", "info", "io", "co"]);

const BRAND_LIST = [
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
  "tumblr", "wordpress", "blogger", "medium", "wikipedia", "wikimedia"
];

function shannonEntropy(s) {
  if (!s) return 0.0;
  const freq = {};
  for (const ch of s) freq[ch] = (freq[ch] || 0) + 1;
  let entropy = 0.0;
  const length = s.length;
  for (const count of Object.values(freq)) {
    const p = count / length;
    entropy -= p * Math.log2(p);
  }
  return entropy;
}

function levenshtein(a, b) {
  // Simple iterative implementation
  const m = a.length, n = b.length;
  const dp = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (a[i - 1] === b[j - 1]) dp[i][j] = dp[i - 1][j - 1];
      else dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
    }
  }
  return dp[m][n];
}

function extractTLD(domain) {
  const parts = domain.split('.');
  return parts.length > 1 ? parts[parts.length - 1] : '';
}

function getDomainMain(domain) {
  // Remove TLD
  const parts = domain.split('.');
  return parts.length > 1 ? parts[parts.length - 2] : domain;
}

function levenshteinToBrand(domain) {
  const main = getDomainMain(domain);
  let minDist = Infinity;
  for (const brand of BRAND_LIST) {
    const dist = levenshtein(main, brand);
    if (dist < minDist) minDist = dist;
  }
  return minDist;
}

function extractUrlFeatures(url) {
  try {
    const urlObj = new URL(url);
    const s = url;
    const url_length = s.length;
    const path = urlObj.pathname;
    const path_depth = path.replace(/(^\/|\/$)/g, '').split('/').filter(Boolean).length;
    const domain = urlObj.hostname.toLowerCase();
    const num_subdomains = domain.includes('www') ? domain.split('.').length - 3 : domain.split('.').length - 2;
    const num_special_chars = (s.match(/[^A-Za-z0-9]/g) || []).length;
    const num_digits = (s.match(/\d/g) || []).length;
    const num_hyphens = (s.match(/-/g) || []).length;
    const has_at_symbol = s.includes('@') ? 1 : 0;
    const query = urlObj.search.replace(/^\?/, '');
    const num_query_params = query ? query.split('&').filter(Boolean).length : 0;
    const digit_ratio = url_length ? num_digits / url_length : 0;
    const url_entropy = shannonEntropy(s);
    const has_https = urlObj.protocol.toLowerCase() === 'https:' ? 1 : 0;
    const tld = extractTLD(domain);
    const uncommon_tld = COMMON_TLDS.has(tld) ? 0 : 1;
    const lev_to_brand = levenshteinToBrand(domain);
    const tokens = s.split(/[\/_\-?=&]/).filter(Boolean);
    const url_token_count = tokens.length;
    return {
      url_length,
      path_depth,
      num_subdomains,
      num_special_chars,
      num_digits,
      num_hyphens,
      has_at_symbol,
      num_query_params,
      digit_ratio,
      url_entropy,
      has_https,
      levenshtein_to_brand: lev_to_brand,
      uncommon_tld,
      url_token_count
    };
  } catch (e) {
    // If URL parsing fails, return null or zeros
    return null;
  }
}

export { extractUrlFeatures };
