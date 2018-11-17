# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class ParseObiSpider(CrawlSpider):
    name = 'obi'
    allowed_domains = ['www.obi.ch']
    start_urls = (
        'https://www.obi.ch/bauen/c/877',
        'https://www.obi.ch/technik/c/876',
        'https://www.obi.ch/kueche/c/875',
        'https://www.obi.ch/bad/c/4159',
        )

    rules = (
    Rule(LinkExtractor(allow=('cms/de/shop-content', ),
        restrict_xpaths=('//*[contains(@class, "item")]',)),
            follow=True),
    Rule(LinkExtractor(allow=('de/sortiment', ),
        restrict_xpaths=('//*[contains(@class, "item")]',)),
            follow=True),
    Rule(LinkExtractor(allow=(''),
        restrict_xpaths=('//*[contains(@class, "product-image")]',)),
            follow=True, callback = 'parse_page'),
    )


    def parse(self, response):
        pass
