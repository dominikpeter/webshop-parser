# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bauhaus.items import BauhausItem

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

        details = response.xpath(
            "//*[@class='table']/tbody/tr/td/text()").extract()

        try:
            details_header =  [details[i] for i in range(0, len(details), 2)]
            details_value = [details[i] for i in range(1, len(details)+1, 2)]

            details = dict(zip(details_header,
                               details_value))
        except IndexError:
            details = {}

        product = BauhausItem()

        product['head'] = txt
        product['desc'] = desc
        product['price'] = price
        product['cat'] = cat
        product['url'] = response.url
        product['details'] = details


        yield dict(product)
