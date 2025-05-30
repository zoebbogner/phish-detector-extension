import csv
from scrapy import Spider, Request
from models.content.utils.feature_helper import extract_html_features

class FeatureSpider(Spider):
    name = "feature_spider"

    def start_requests(self):
        with open(self.settings.get('SEEDS_CSV'), newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield Request(row['url'], callback=self.parse, meta={'label': row.get('label')})
                
                
    def parse(self, response):
        feats = extract_html_features(response.text, response.url)
        # if you have more extractors, merge them in here:
        # feats.update(extract_redirect_and_external_domain_features(...))

        # Build one flat record
        record = {
            'url': response.url,
            'label': response.meta.get('label', '')
        }
        record.update(feats)    # <-- flatten every feature as its own key
        yield record