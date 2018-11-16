# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class BauhausSpider(CrawlSpider):
    name = "bauhaus"
    allowed_domains = ["bauhaus.ch"]
    start_urls = (
        'https://www.bauhaus.ch/cms/de/',
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

    def parse_page(self, response):

        txt = response.xpath("*//h1/text()").extract_first()
        price = response.xpath(
            "//*[contains(@id, 'price')]/text()").extract()[2]
        desc = " ".join(response.xpath(
            "//*[contains(@class, 'product-features')]/li/text()").extract())
        cat = response.xpath(
            "//*[contains(@class, 'breadcrumbs')]/li/a/text()").extract()

        yield({"head": txt,
               "desc": desc,
               "price": price,
               "cat": cat,
               "url": response.url})
