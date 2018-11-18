# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from jumbo.items import JumboItem

from urllib.parse import urljoin, urlencode
import re


class ParseJumboSpider(CrawlSpider):
    name = 'jumbo'
    allowed_domains = ['jumbo.ch']
    start_urls = (
        'https://www.jumbo.ch',
        )

    rules = (
        Rule(LinkExtractor(allow=(r"de/bad-sanitaer")),
                follow=True),
        Rule(LinkExtractor(allow=(r"de/bodenbelaege-wandverkleidungen-farben")),
                follow=True),
        Rule(LinkExtractor(allow=(r"de/holz-baumaterial")),
                follow=True),
        Rule(LinkExtractor(allow=(r"de/maschinen-werkzeuge-arbeitsbekleidung")),
                follow=True),
        Rule(LinkExtractor(allow=(r"de/.*sku=")),
                follow=True, callback='parse_product'),
        )

    def parse_product(self, response):
        header =  " ".join(response.xpath(
            "//*[contains(@class, 'font__h1')]/span/text()").extract())
        table = response.xpath(
            "//*[contains(@class, 'product-Details-TechnicalAttributesTabs')]")
        desc = response.xpath("//*[@class='font__p1']/text()").extract()
        infos = table.xpath("./span/text()").extract()[1:]
        info_header = [infos[i] for i in range(0, len(infos), 2)]
        info_detail = [infos[i] for i in range(1, len(infos), 2)]
        details = dict(zip(info_header, info_detail))

        product = JumboItem()
        product['header'] = header
        product['description'] = desc
        product['details'] = details

        yield dict(product)
