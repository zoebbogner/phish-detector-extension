# content_feature_extractor.py
import re
import requests
from lxml import html
import numpy as np

class ContentFeatureExtractor:
    """
    Given URLs, fetches each page and extracts DOM/HTML features:
      - num_tags
      - num_links
      - num_external_links
      - num_forms
      - num_inputs
      - num_hidden_inputs
      - num_scripts
      - num_iframes
      - num_images
      - num_onclick_attrs
      - num_meta_refresh
      - text_length
      - word_count
      - suspicious_word_count
    """
    def __init__(self, suspicious_tokens=None, timeout=5.0, headers=None):
        # compile phishing keywords
        self._suspicious_re = re.compile(
            '|'.join(suspicious_tokens or 
                     ['login','signin','secure','account','update','verify']),
            re.IGNORECASE
        )
        # prepare a session for connection reuse
        self.session = requests.Session()
        self.session.headers.update(headers or {
            'User-Agent': 'PhishExt/1.0 (+https://yourdomain.com)'
        })
        self.timeout = timeout

    def fit(self, X, y=None):
        return self

    def transform(self, urls):
        feats = []
        for url in urls:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                doc = resp.text
            except Exception:
                # on any fetch failure, record zeros
                feats.append([0]*14)
                continue

            tree = html.fromstring(doc)
            # count elements
            num_tags    = sum(1 for _ in tree.iter())
            links       = tree.xpath('//a')
            num_links   = len(links)
            num_external= sum(1 for a in links
                               if a.get('href','').lower().startswith(('http://','https://')))
            forms       = tree.xpath('//form')
            num_forms   = len(forms)
            inputs      = tree.xpath('//input')
            num_inputs  = len(inputs)
            num_hidden  = sum(1 for inp in inputs
                              if inp.get('type','').lower()=='hidden')
            num_scripts = len(tree.xpath('//script'))
            num_iframes = len(tree.xpath('//iframe'))
            num_images  = len(tree.xpath('//img'))
            num_onclick = len(tree.xpath('//*[@onclick]'))
            num_meta_ref= len(tree.xpath(
                '//meta[translate(@http-equiv,"REFRESH","refresh")="refresh"]'
            ))

            text        = tree.text_content() or ""
            text_length = len(text)
            words       = re.findall(r'\w+', text)
            word_count  = len(words)
            suspicious  = len(self._suspicious_re.findall(text))

            feats.append([
                num_tags, num_links, num_external, num_forms,
                num_inputs, num_hidden, num_scripts, num_iframes,
                num_images, num_onclick, num_meta_ref,
                text_length, word_count, suspicious
            ])

        return np.array(feats)
