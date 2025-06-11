// Content Feature Extractor for JavaScript
// Optimized for live DOM usage, with caching and batching
// Mirrors the features from models/content/utils/feature_helper.py and config.py

const SUSPICIOUS_KEYWORDS = [
  "login", "verify", "update", "secure", "account", "signin", "password", "ebayisapi", "webscr"
];

const AD_NETWORK_DOMAINS = new Set([
  "taboola.com", "outbrain.com", "revcontent.com", "googlesyndication.com", "adroll.com",
  "adsrvr.org", "rubiconproject.com", "pubmatic.com", "appnexus.com", "openx.net", "criteo.com",
  "adblade.com", "yimg.com", "doubleclick.net", "yieldmanager.com", "yieldmanager.net",
  "yieldmanager.org", "yieldmanager.info", "yieldmanager.biz"
]);

// --- Domain extraction cache ---
const domainCache = new Map();
const DOMAIN_CACHE_MAX = 100;
function extractDomainCached(hostname) {
  if (domainCache.has(hostname)) return domainCache.get(hostname);
  const parts = hostname.split('.');
  const domain = parts.length >= 2 ? parts.slice(-2).join('.') : hostname;
  if (domainCache.size > DOMAIN_CACHE_MAX) domainCache.delete(domainCache.keys().next().value);
  domainCache.set(hostname, domain);
  return domain;
}

// --- LRU cache for shannonEntropy ---
const entropyCache = new Map();
const ENTROPY_CACHE_MAX = 20;
function shannonEntropyLRU(s) {
  if (!s) return 0.0;
  if (entropyCache.has(s)) {
    // Move to end (most recently used)
    const v = entropyCache.get(s);
    entropyCache.delete(s);
    entropyCache.set(s, v);
    return v;
  }
  const freq = {};
  for (const ch of s) freq[ch] = (freq[ch] || 0) + 1;
  let entropy = 0.0;
  const length = s.length;
  for (const count of Object.values(freq)) {
    const p = count / length;
    entropy -= p * Math.log2(p);
  }
  if (entropyCache.size > ENTROPY_CACHE_MAX) entropyCache.delete(entropyCache.keys().next().value);
  entropyCache.set(s, entropy);
  return entropy;
}

function isExternalResource(link, pageDomain) {
  if (!link || !pageDomain) return false;
  try {
    const url = new URL(link, 'http://'+pageDomain); // relative-safe
    const domain = extractDomainCached(url.hostname);
    return domain !== pageDomain;
  } catch {
    return false;
  }
}

function isHttps(link) {
  try {
    return link.trim().toLowerCase().startsWith('https://');
  } catch {
    return false;
  }
}

const FEATURE_SYMBOL = Symbol('content_features');

/**
 * Extracts content-based features from a live Document or Element and a URL string.
 * Caches expensive computations and attaches the result to the document for reuse.
 * @param {Document|Element} root - The root DOM node (usually document.documentElement)
 * @param {string} url - The page URL
 * @returns {Object} Feature map
 */
function extractContentFeatures(root, url) {
  // Check for cached result
  if (root[FEATURE_SYMBOL]) return root[FEATURE_SYMBOL];

  // Parse URL once
  let pageHostname = '';
  try {
    pageHostname = new URL(url).hostname;
  } catch {}
  const pageDomain = extractDomainCached(pageHostname);

  // Batch DOM queries
  const allTags = root.getElementsByTagName('*');
  const anchors = root.querySelectorAll('a[href]');
  const forms = root.getElementsByTagName('form');
  const inputs = root.getElementsByTagName('input');
  const scripts = root.getElementsByTagName('script');
  const iframes = root.getElementsByTagName('iframe');
  const imgs = root.getElementsByTagName('img');
  const metas = root.getElementsByTagName('meta');
  const stylesheets = root.querySelectorAll('link[rel*="stylesheet" i]');
  const faviconLink = root.querySelector('link[rel*="icon" i]');
  const titleTag = root.querySelector('title');

  // --- Feature extraction ---
  const features = {};
  features["html_tag_count"] = allTags.length;
  features["form_count"] = forms.length;
  features["input_count"] = inputs.length;
  features["anchor_count"] = anchors.length;
  features["script_count"] = scripts.length;
  features["iframe_count"] = iframes.length;
  features["img_count"] = imgs.length;
  features["meta_refresh_count"] = Array.from(metas).filter(m => (m.getAttribute('http-equiv')||'').toLowerCase() === 'refresh').length;

  // Ad network asset count, unique script domains, script srcs
  let adCount = 0;
  const scriptSrcs = [];
  const uniqueScriptDomains = new Set();
  for (const tag of scripts) {
    const src = tag.getAttribute('src');
    if (src) {
      scriptSrcs.push(src);
      const domain = extractDomainCached((new URL(src, url)).hostname);
      if (domain && domain !== pageDomain) uniqueScriptDomains.add(domain);
      if (AD_NETWORK_DOMAINS.has(domain)) adCount++;
    }
  }
  const iframeSrcs = [];
  for (const tag of iframes) {
    const src = tag.getAttribute('src');
    if (src) {
      iframeSrcs.push(src);
      const domain = extractDomainCached((new URL(src, url)).hostname);
      if (AD_NETWORK_DOMAINS.has(domain)) adCount++;
    }
  }
  features["ad_network_asset_count"] = adCount;

  // Favicon domain mismatch
  let faviconDomainMismatch = 0;
  if (faviconLink && faviconLink.getAttribute('href')) {
    try {
      const faviconDomain = extractDomainCached((new URL(faviconLink.getAttribute('href'), url)).hostname);
      if (faviconDomain && faviconDomain !== pageDomain) faviconDomainMismatch = 1;
    } catch {}
  }
  features["favicon_domain_mismatch"] = faviconDomainMismatch;

  // Domain mismatch link ratio
  let mismatchCount = 0;
  for (const a of anchors) {
    const href = a.getAttribute('href') || '';
    try {
      const domain = extractDomainCached((new URL(href, url)).hostname);
      if (domain && domain !== pageDomain) mismatchCount++;
    } catch {}
  }
  features["domain_mismatch_link_ratio"] = anchors.length ? mismatchCount / anchors.length : 0;

  // External stylesheet ratio
  let externalStylesheetCount = 0;
  for (const s of stylesheets) {
    const href = s.getAttribute('href');
    if (href) {
      try {
        const domain = extractDomainCached((new URL(href, url)).hostname);
        if (domain && domain !== pageDomain) externalStylesheetCount++;
      } catch {}
    }
  }
  features["external_stylesheet_ratio"] = stylesheets.length ? externalStylesheetCount / stylesheets.length : 0;

  // Additional structural features
  const htmlLength = root.outerHTML ? root.outerHTML.length : 0;
  features["html_length"] = htmlLength;

  // Script text entropy
  let scriptText = '';
  for (const tag of scripts) {
    if (tag.textContent) scriptText += tag.textContent + ' ';
  }

  // Content Ratios & Text Stats
  features["title_length"] = titleTag && titleTag.textContent ? titleTag.textContent.trim().length : 0;
  const rawText = root.textContent || '';
  features["text_to_html_ratio"] = htmlLength ? rawText.length / htmlLength : 0;
  features["document_text_entropy"] = shannonEntropyLRU(rawText);

  // Suspicious Patterns
  const lowerText = rawText.toLowerCase();
  features["suspicious_keyword_count"] = SUSPICIOUS_KEYWORDS.reduce((acc, word) => acc + (lowerText.split(word).length - 1), 0);
  features["base64_asset_count"] = (root.outerHTML.match(/base64,/gi) || []).length;
  features["data_uri_asset_count"] = (root.outerHTML.match(/src=['"]data:/gi) || []).length;
  features["inline_style_count"] = Array.from(allTags).filter(tag => tag.getAttribute('style')).length;
  features["password_field_count"] = Array.from(inputs).filter(inp => (inp.getAttribute('type')||'').toLowerCase() === 'password').length;
  features["hidden_redirect_element_count"] = Array.from(allTags).filter(tag => {
    const style = (tag.getAttribute('style') || '').toLowerCase();
    return style.includes('display:none') || style.includes('opacity:0');
  }).length;

  // External/Redirect Risks
  // Non-HTTPS resources
  const resources = [
    ...Array.from(imgs).map(t => t.getAttribute('src')),
    ...scriptSrcs,
    ...iframeSrcs
  ];
  const nonHttpsResources = resources.filter(r => r && !isHttps(r));
  features["non_https_resource_ratio"] = resources.length ? nonHttpsResources.length / resources.length : 0;

  let externalResourceCount = 0;
  for (const r of resources) {
    if (isExternalResource(r, pageDomain)) externalResourceCount++;
  }
  features["external_resource_count"] = externalResourceCount;
  features["password_reset_link_count"] = Array.from(anchors).filter(a => {
    const text = a.textContent.toLowerCase();
    return (text.includes('reset') || text.includes('forgot')) && text.includes('password');
  }).length;

  // Redirect pattern count and external domain count
  const redirectPatterns = [
    /redirect[\w%]*=/i, /next[\w%]*=/i, /url[\w%]*=/i, /target[\w%]*=/i
  ];
  let redirectPatternCount = 0;
  const base64Regex = /^[A-Za-z0-9+/]{20,}={0,2}$/;
  for (const a of anchors) {
    const href = a.getAttribute('href') || '';
    for (const pat of redirectPatterns) {
      if (pat.test(href)) {
        redirectPatternCount++;
        break;
      }
      // Try percent-decoded
      try {
        const decodedHref = decodeURIComponent(href);
        if (pat.test(decodedHref)) {
          redirectPatternCount++;
          break;
        }
      } catch {}
      // Try base64-decoded
      try {
        if (href.length > 32 && base64Regex.test(href)) {
          const base64Decoded = atob(href);
          if (pat.test(base64Decoded)) {
            redirectPatternCount++;
            break;
          }
        }
      } catch {}
    }
  }
  const externalDomains = new Set();
  for (const tag of allTags) {
    for (const attr of ["href", "src"]) {
      const link = tag.getAttribute(attr);
      if (link) {
        try {
          const domain = extractDomainCached((new URL(link, url)).hostname);
          if (domain && domain !== pageDomain) externalDomains.add(domain);
        } catch {}
      }
    }
  }
  features["redirect_pattern_count"] = redirectPatternCount;
  features["external_domain_count"] = externalDomains.size;

  // Attach to root for reuse
  root[FEATURE_SYMBOL] = features;
  return features;
}

window.extractContentFeatures = extractContentFeatures;