import scrapy
from hornbach.items import HornbachItem

import json
import os
from urllib.parse import urljoin
import re

from json.decoder import JSONDecodeError

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")


def load_products_hrefs():
    try:
        with open("products.json") as f:
            js = json.load(f)
        links = [i['url'] for i in js]
        return links
    except FileNotFoundError:
        pass



class ProductDetailSpider(scrapy.Spider):
    name = "hornbach_products_detail"
    allowed_domains = ['hornbach.ch']
    start_urls = load_products_hrefs()

    def parse(self, response):
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

        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-CH,de-DE;q=0.9,de;q=0.8,en-US;q=0.7,en;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'undefined': 'undefined',
            'Referer': response.url,
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive'
            }

        product = HornbachItem()
        product['ean'] = ean
        product['header'] = header
        product['id'] = id
        product['details'] = details
        product['cat1'] = cats[2]
        product['cat2'] = cats[3]
        product['cat3'] = cats[4]

        yield scrapy.Request(price_url, headers=headers,
                             callback=self.parse_json,
                             meta={'product': product})

    def parse_json(self, response):
        product = response.meta['product']
        try:
            js = json.loads(response.text)
            product['price'] = js['basePrice']['price']
        except JSONDecodeError:
            product['price'] = ''

        yield(dict(product))
