# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from bauundhobby.items import BauundhobbyItem

from urllib.parse import urljoin, urlencode
import re


class ParseBauundhobbySpider(CrawlSpider):
    name = 'bauundhobby'
    allowed_domains = ['bauundhobby.ch']
    start_urls = (
        'https://www.bauundhobby.ch/maschinen-werkstatt/c/04',
        'https://www.bauundhobby.ch/bad-sanit%C3%A4r/c/05',
        'https://www.bauundhobby.ch/bauen-renovieren/c/06',
    )

    rules = (
        Rule(LinkExtractor(allow=('', ),
                           restrict_xpaths=(
                            '//*[contains(@class, "link-has-icon")]',)),
             follow=True, callback="parse_page"),
    )

    def parse_page(self, response):
        full_url = response.urljoin("?page=999999")
        yield Request(full_url, callback=self.parse_article)

    def parse_article(self, response):
        product_url = response.xpath(
            "//*[@class='product-tile__link']/@href").extract()
        for i in product_url:
            new_url = response.urljoin(i)
            yield Request(new_url, callback=self.parse_article_detail)

    def parse_article_detail(self, response):
        header = response.xpath(
            "//*[@class = 'product-detail__headline']/text()").extract_first()
        price = response.xpath(
            "//*[@class = 'pricing__price']/text()").extract_first()
        price = re.sub("\s", "", price)
        price = re.sub("-", "00", price)

        table = response.xpath("*//tbody/tr")
        table_title = table.xpath("./th/text()").extract()
        table_detail = table.xpath(
            "./td/text()").extract() + table.xpath(
            "./td/span/text()").extract()
        table_detail = [re.sub("\s", "", i) for i in table_detail]
        details = dict(zip(table_title, table_detail))

        product = BauundhobbyItem()
        product['header'] = header
        product['price'] = price
        product['details'] = details

        yield dict(product)
