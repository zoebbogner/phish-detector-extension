import csv
import logging

import scrapy
from models.content.utils.feature_helper import extract_html_features


class FeatureSpider(scrapy.Spider):
    name = "feature_spider"
    custom_settings = {"ROBOTSTXT_OBEY": False}

    # Asynchronous start() that yields each Request from our old start_requests()
    async def start(self):
        for req in self.start_requests():
            yield req

    # Keep start_requests() as a normal (synchronous) generator of Request objects:
    def start_requests(self):
        with open(self.settings.get('SEEDS_CSV'), newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['url']
                label = row.get('label', '')

                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    errback=self.on_fetch_error,
                    meta={'label': label}
                )

    # ... rest of your spider (on_fetch_error(), parse(), etc.) ...
    def on_fetch_error(self, failure):
        url = failure.request.url
        self.logger.error(f"❌ Fetch failed for {url}: {failure.value}")

    def parse(self, response):
        label = response.meta.get('label', '')
        if response.status != 200:
            self.logger.warning(f"⚠️ Skipping {response.url} (status {response.status})")
            return

        content_type = response.headers.get('Content-Type', b"").decode('utf-8', errors='ignore')
        if not content_type.lower().startswith('text/') and 'html' not in content_type.lower():
            self.logger.warning(f"⚠️ Non‐HTML ({content_type}) at {response.url}")
            return

        try:
            feats = extract_html_features(response.text, response.url)
        except Exception as e:
            self.logger.warning(f"⚠️ Error parsing {response.url}: {e}")
            return

        row = {'label': label, 'url': response.url}
        row.update(feats)
        yield row