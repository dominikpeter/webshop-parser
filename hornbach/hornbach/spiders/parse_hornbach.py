from scrapy.spiders import Spider, CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from hornbach.items import HornbachItem
from scrapy.http import Request

import os
import json
from urllib.parse import urljoin
import re
import math


class HornbachSpider(Spider):
    name = "hornbach"
    start_urls =  (
        'https://www.hornbach.ch/cms/de/ch/sortiment/bad-sanitaer.html',
        'https://www.hornbach.ch/cms/de/ch/sortiment/baustoffe-holz-fenster-tueren.html',
        'https://www.hornbach.ch/cms/de/ch/sortiment/bodenbelaege.html',
        'https://www.hornbach.ch/cms/de/ch/sortiment/eisenwaren.html',
        'https://www.hornbach.ch/cms/de/ch/sortiment/farben-tapeten.html',
        'https://www.hornbach.ch/cms/de/ch/sortiment/garten.html',
        'https://www.hornbach.ch/cms/de/ch/sortiment/heizen-klima-lueftung.html',
        'https://www.hornbach.ch/cms/de/ch/sortiment/kueche.html',
        'https://www.hornbach.ch/cms/de/ch/sortiment/maschinen-werkzeuge-werkstatt.html',
        )
    allowed_domains = ['hornbach.ch']


    def __init__(self):
        self.n_pages = 72


    def parse(self, response):
        links =  response.xpath(
            "//*[contains(@class, 'sub')]/a/@href").extract()
        links = [i for i in links if i.startswith("/shop/")]

        for i in links:
            new_url = response.urljoin(i)
            yield Request(new_url,
                          callback = self.parse_cat)


    def parse_cat(self, response):
        article_count = response.xpath(
            "//*[contains(@class, 'sub-active')]/a/i/text()").extract_first()
        article_count = re.findall("\((\d*)\)", article_count)[0]
        pages = math.ceil(int(article_count) / self.n_pages)
        for i in range(pages):
            i += 1
            cat_id = re.findall("\/(\w*)\/artikelliste", response.url)[0]

            get_url = "/".join(
                ["https://www.hornbach.ch","mvc","article","load",
                 "article-list", "de", "750",
                 cat_id, str(self.n_pages), str(i), "sortModeDv"
                 ])

            yield Request(get_url,
                          headers={'Content-Type':'application/json'},
                          callback = self.parse_product_link)

    def parse_product_link(self, response):
        js = json.loads(response.text)
        for i in js['articles']:
            product_url = i['localizedExternalArticleLink']
            product_url = response.urljoin(product_url)
            yield Request(product_url,
                          callback=self.parse_product_detail)

    def parse_product_detail(self, response):
        header = response.xpath("//*[self::h1]/text()").extract_first()
        ean = response.xpath(
            "//*[contains(@class, 'ean')]/td/span/text()").extract_first()
        ean = re.sub("\D", "", ean)
        id = response.xpath(
            "//*[contains(@class, 'article-details-code')]/text()").extract_first()
        id = id[5:]
        price_url = urljoin(
            "https://www.hornbach.ch/mvc/hbprice/article-tracking-prices/",
            id+"/0")
        detail_header = response.xpath(
            "//*[contains(@class, 'techdata')]/tbody/tr/th/text()").extract()
        detail_header = [' '.join(i.split()) for i in detail_header]
        detail_info = response.xpath(
            "//*[contains(@class, 'techdata')]/tbody/tr/td/text()").extract()
        detail_info = [' '.join(i.split()) for i in detail_info]
        details = dict(zip(detail_header, detail_info))

        cats = response.xpath("//*[@class = 'breadcrumb']/a/text()").extract()

        product = HornbachItem()
        product['ean'] = ean
        product['header'] = header
        product['id'] = id
        product['details'] = details
        product['cat1'] = cats[2]
        product['cat2'] = cats[3]
        product['cat3'] = cats[4]

        yield Request(price_url,
                     headers={'Content-Type':'application/json'},
                     callback=self.parse_json,
                     meta={'product': product})

    def parse_json(self, response):
        product = response.meta['product']
        try:
            js = json.loads(response.text)
            product['price'] = js['basePrice']['price']
        except JSONDecodeError:
            product['price'] = ''

        yield dict(product)
