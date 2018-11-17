# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request


class ParseObiSpider(CrawlSpider):
    name = 'obi'
    allowed_domains = ['obi.ch']
    start_urls = (
        'https://www.obi.ch/bauen/c/877',
        'https://www.obi.ch/technik/c/876',
        'https://www.obi.ch/kueche/c/875',
        'https://www.obi.ch/bad/c/4159',
    )

    rules = (
        Rule(LinkExtractor(allow=('', ),
                           restrict_xpaths=('//*[contains(@wt_name, "level2")]',)),
             follow=True),
        Rule(LinkExtractor(allow=('', ),
                           restrict_xpaths=('//*[contains(@wt_name, "level3")]',)),
             follow=True),
        Rule(LinkExtractor(allow=(''),
                           restrict_xpaths=('//*[contains(@wt_name, "level4")]',)),
             follow=True),
        Rule(LinkExtractor(allow=(''),
                           restrict_xpaths=('//*[contains(@tm-data, "content.pagination.next-page.link")]',)),
             follow=True),
        Rule(LinkExtractor(allow=(''),
                           restrict_xpaths=('//*[contains(@class, "product-wrapper")]',)),
             follow=True, callback='parse_page'),
    )

    def parse_page(self, response):
        yield {"url": response.url}
