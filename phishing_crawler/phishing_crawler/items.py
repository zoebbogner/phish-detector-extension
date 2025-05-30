import scrapy

class PageItem(scrapy.Item):
    url               = scrapy.Field()
    raw_html          = scrapy.Field()
    label             = scrapy.Field()    # “phish” or “benign”—you’ll need a way to seed this