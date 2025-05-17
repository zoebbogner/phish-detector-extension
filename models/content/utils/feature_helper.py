"""
This file contains helper functions for the content feature extraction.
It extracts exactly 26 features from HTML and URL for phishing detection:
    html_tag_count, form_count, input_count, anchor_count, script_count, iframe_count, img_count, meta_refresh_count,
    title_length, text_to_html_ratio, document_text_entropy, suspicious_keyword_count, base64_asset_count, data_uri_asset_count,
    inline_style_count, password_field_count, hidden_redirect_element_count, external_stylesheet_ratio, non_https_resource_ratio,
    domain_mismatch_link_ratio, password_reset_link_count, external_resource_count, favicon_domain_mismatch,
    redirect_pattern_count, external_domain_count, ad_network_asset_count
"""
import math
import base64
import binascii
import re
from bs4 import BeautifulSoup
import tldextract
from models.content.config import SUSPICIOUS_KEYWORDS, MAX_CACHE_SIZE, AD_NETWORK_DOMAINS

domain_cache = {}

def shannon_entropy(s: str) -> float:
    """
    Calculate the Shannon entropy of a string.
    Args:
        s (str): Input string.
    Returns:
        float: Shannon entropy value.
    """
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

def extract_domain(url: str) -> str:
    """
    Extract the normalized domain from a URL using tldextract, with in-module cache.
    Args:
        url (str): The URL to extract the domain from.
    Returns:
        str: The normalized domain (domain.suffix) or empty string.
    """
    if url in domain_cache:
        return domain_cache[url]
    
    ext = tldextract.extract(url)
    if ext.domain and ext.suffix:
        domain = f"{ext.domain}.{ext.suffix}"
    else:
        domain = ext.domain or ""
    domain_cache[url] = domain
    
    if len(domain_cache) > MAX_CACHE_SIZE:
        domain_cache.pop(list(domain_cache.keys())[0])
        
    return domain

def is_external_resource(link: str, page_domain: str) -> bool:
    """
    Determine if a resource link is external to the given page domain.
    Args:
        link (str): The resource URL.
        page_domain (str): The normalized domain of the page.
    Returns:
        bool: True if the resource is external, False otherwise.
    """
    if not link or not page_domain:
        return False
    resource_domain = extract_domain(link)
    return resource_domain != page_domain

def is_https(link: str) -> bool:
    """
    Check if a link uses HTTPS protocol.
    Args:
        link (str): The URL to check.
    Returns:
        bool: True if the link starts with 'https://', False otherwise.
    """
    return link.strip().lower().startswith("https://")

def extract_redirect_and_external_domain_features(all_tags, anchors, page_domain):
    """
    Extract features related to suspicious redirect patterns and unique external domains.
    Args:
        soup (BeautifulSoup): Parsed HTML soup.
        all_tags (list): List of all tags in the document.
        anchors (list): List of all anchor tags with href.
        page_domain (str): The normalized domain of the page.
    Returns:
        dict: Dictionary with 'redirect_pattern_count' and 'external_domain_count'.
    """
    redirect_patterns = [
        r"redirect[\w%]*=", r"next[\w%]*=", r"url[\w%]*=", r"target[\w%]*="
    ]
    redirect_count = 0
    base64_regex = re.compile(r'^[A-Za-z0-9+/]{20,}={0,2}$')
    for a in anchors:
        href = a.get("href", "")
        for pat in redirect_patterns:
            if re.search(pat, href, re.IGNORECASE):
                redirect_count += 1
                break
            try:
                decoded_href = re.sub(r'%([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), href)
                if re.search(pat, decoded_href, re.IGNORECASE):
                    redirect_count += 1
                    break
            except (ValueError, TypeError):
                pass
            try:
                # Optimization: Only try base64 decode if href is long enough and matches stricter base64 regex
                base64_decoded = ''
                if len(href) > 32 and base64_regex.match(href):
                    base64_decoded = base64.b64decode(href + '===').decode('utf-8', errors='ignore')
                if re.search(pat, base64_decoded, re.IGNORECASE):
                    redirect_count += 1
                    break
            except (binascii.Error, ValueError, TypeError):
                pass
    external_domains = set()
    for tag in all_tags:
        for attr in ["href", "src"]:
            link = tag.get(attr)
            if link and is_external_resource(link, page_domain):
                ext = tldextract.extract(link)
                if ext.domain and ext.suffix:
                    external_domains.add(f"{ext.domain}.{ext.suffix}")
    return {
        "redirect_pattern_count": redirect_count,
        "external_domain_count": len(external_domains)
    }

def extract_html_features(html: str, url: str) -> dict:
    """
    Extract 26 structured features from an HTML page and its URL for phishing detection.
    Args:
        html (str): The HTML content of the page.
        url (str): The URL of the page.
    Returns:
        dict: Dictionary of extracted features keyed by feature name.
    """
    try:
        soup = BeautifulSoup(html or "", "html.parser")
        page_domain = extract_domain(url)
        features = {}

        # 1. Tag and Structure Counts
        all_tags = soup.find_all(True)
        anchors = soup.find_all("a", href=True)  # Cache and reuse
        features["html_tag_count"] = len(all_tags)
        features["form_count"] = len(soup.find_all("form"))
        features["input_count"] = len(soup.find_all("input"))
        features["anchor_count"] = len(anchors)
        features["script_count"] = len(soup.find_all("script"))
        features["iframe_count"] = len(soup.find_all("iframe"))
        features["img_count"] = len(soup.find_all("img"))
        features["meta_refresh_count"] = len([
            m for m in soup.find_all("meta")
            if m.get("http-equiv", "").lower() == "refresh"
        ])

        # Ad network asset count
        script_srcs = [tag.get("src") for tag in soup.find_all("script") if tag.get("src")]
        iframe_srcs = [tag.get("src") for tag in soup.find_all("iframe") if tag.get("src")]
        ad_count = 0
        for src in script_srcs + iframe_srcs:
            domain = extract_domain(src)
            if domain in AD_NETWORK_DOMAINS:
                ad_count += 1
        features["ad_network_asset_count"] = ad_count

        # 1.5. Favicon domain mismatch
        favicon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
        favicon_domain_mismatch = 0
        if favicon_link and favicon_link.get("href"):
            favicon_url = favicon_link["href"]
            favicon_domain = extract_domain(favicon_url)
            if favicon_domain and favicon_domain != page_domain:
                favicon_domain_mismatch = 1
        features["favicon_domain_mismatch"] = favicon_domain_mismatch

        # 1.6. Domain mismatch link ratio
        mismatch_count = 0
        for a in anchors:
            href = a.get("href", "")
            if href and is_external_resource(href, page_domain):
                mismatch_count += 1
        features["domain_mismatch_link_ratio"] = mismatch_count / (len(anchors) or 1)

        # 1.7. External stylesheet ratio
        stylesheets = soup.find_all("link", rel=lambda x: x and "stylesheet" in x.lower())
        external_stylesheets = [s for s in stylesheets if s.get("href") and is_external_resource(s.get("href"), page_domain)]
        features["external_stylesheet_ratio"] = len(external_stylesheets) / (len(stylesheets) or 1)

        # 1.8. Additional structural features
        features["html_length"] = len(html)
        features["script_to_html_ratio"] = len(script_srcs) / (len(html) or 1)
        features["form_to_input_ratio"] = features["form_count"] / (features["input_count"] or 1)
        # Unique script domains different from page domain
        unique_script_domains = set()
        for src in script_srcs:
            domain = extract_domain(src)
            if domain and domain != page_domain:
                unique_script_domains.add(domain)
        features["unique_script_domains"] = len(unique_script_domains)

        # 1.9. Script text entropy (optional enhancement)
        inline_scripts = [tag.string for tag in soup.find_all("script") if tag.string]
        script_text = " ".join(inline_scripts)
        features["script_text_entropy"] = shannon_entropy(script_text)

        # 2. Content Ratios & Text Stats
        title_tag = soup.find("title")
        features["title_length"] = len(title_tag.string.strip()) if title_tag and title_tag.string else 0
        raw_text = soup.get_text(separator=" ", strip=True)
        features["text_to_html_ratio"] = len(raw_text) / (len(html) or 1)
        features["document_text_entropy"] = shannon_entropy(raw_text)

        # 3. Suspicious Patterns
        lower_text = raw_text.lower()
        features["suspicious_keyword_count"] = sum(lower_text.count(word) for word in SUSPICIOUS_KEYWORDS)
        features["base64_asset_count"] = len(re.findall(r"base64,", html, re.IGNORECASE))
        features["data_uri_asset_count"] = len(re.findall(r"src=['\"]data:", html, re.IGNORECASE))
        features["inline_style_count"] = len([tag for tag in all_tags if tag.get("style")])
        features["password_field_count"] = len([inp for inp in soup.find_all("input") if inp.get("type", "").lower() == "password"])
        features["hidden_redirect_element_count"] = len([
            tag for tag in all_tags
            if (tag.get("style") and ("display:none" in tag.get("style", "").lower() or "opacity:0" in tag.get("style", "").lower()))
        ])

        # 4. External/Redirect Risks
        # Non-HTTPS resources
        resources = [t.get("src") for t in soup.find_all(["img", "script", "iframe"]) if t.get("src")]
        non_https_resources = [r for r in resources if r and not is_https(r)]
        features["non_https_resource_ratio"] = len(non_https_resources) / (len(resources) or 1)
        features["external_resource_count"] = len(resources)
        features["password_reset_link_count"] = len([
            a for a in anchors if any(word in a.get_text(" ").lower() for word in ["reset", "forgot"]) and "password" in a.get_text(" ").lower()
        ])

        # Use helper for redirect_pattern_count and external_domain_count
        redirect_external = extract_redirect_and_external_domain_features(all_tags, anchors, page_domain)
        features["redirect_pattern_count"] = redirect_external["redirect_pattern_count"]
        features["external_domain_count"] = redirect_external["external_domain_count"]
        
        return features
    
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        raise e
