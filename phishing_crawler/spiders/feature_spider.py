import csv
import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import scrapy
from models.content.utils.feature_helper import extract_html_features


class FeatureSpider(scrapy.Spider):
    name = "feature_spider"
    custom_settings = {
        # We’ll do robots.txt logic ourselves
        "ROBOTSTXT_OBEY": False,
    }

    def start_requests(self):
        # Read your seeds.csv of URLs + labels
        with open(self.settings.get('SEEDS_CSV'), newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row['url']
                label = row.get('label', '')
                # Kick off by checking robots.txt first
                yield scrapy.Request(
                    url=self._robots_url(url),
                    callback=self._on_robots,
                    errback=self._on_robots_error,
                    meta={'seed_url': url, 'label': label}
                )

    def _robots_url(self, page_url):
        # Build the base robots.txt URL for that domain
        parts = urlparse(page_url)
        return f"{parts.scheme}://{parts.netloc}/robots.txt"

    def _on_robots(self, response):
        seed_url = response.meta['seed_url']
        label = response.meta['label']

        txt = response.text.strip()
        status = response.status

        # If no robots.txt (404/410) or it’s empty → allow crawling
        if status in (404, 410) or not txt:
            allowed = True
        else:
            # Otherwise parse and ask
            rp = RobotFileParser()
            rp.parse(txt.splitlines())
            allowed = rp.can_fetch('*', seed_url)

        if allowed:
            yield scrapy.Request(
                seed_url,
                callback=self.parse,
                meta={'label': label},
            )
        else:
            logging.warning(f"Blocked by robots.txt, skipping {seed_url}")

    def _on_robots_error(self, failure):
        # Network error fetching robots.txt → treat as missing → allow
        seed_url = failure.request.meta['seed_url']
        label = failure.request.meta['label']
        logging.info(f"Could not fetch robots.txt for {seed_url}, proceeding anyway")
        yield scrapy.Request(
            seed_url,
            callback=self.parse,
            meta={'label': label},
        )

    def parse(self, response):
        label = response.meta['label']
        feats = extract_html_features(response.text, response.url)
        # Build your flat CSV row
        row = {'label': label, 'url': response.url}
        row.update(feats)
        yield row