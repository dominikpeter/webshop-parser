# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request

from urllib.parse import urljoin, urlencode
import re


class ParseJumboSpider(CrawlSpider):
    name = 'jumbo'
    allowed_domains = ['jumbo.ch']
    start_urls = (
        'https://www.jumbo.ch',
        )

    rules = (
        # Rule(LinkExtractor(allow=('', ),
        #     restrict_xpaths=('//*[contains(@class, "font__menu4")]/a',)),
        #         follow=True),
        Rule(LinkExtractor(allow=('de', )),
                follow=True),
        Rule(LinkExtractor(allow=('sku', )),
                follow=True, callback="parse_product"),
        )

    def parse_product(self, response):
        yield {"url": response.url}
