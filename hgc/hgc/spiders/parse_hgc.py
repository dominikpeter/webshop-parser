import json
import os
from random import randint

import scrapy
from scrapy.exceptions import CloseSpider

from urllib.parse import urljoin, urlencode
from json.decoder import JSONDecodeError
from hgc.items import HgcItem
from scrapy.http import FormRequest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

chrome_options = Options()
chrome_options.add_argument("--headless")

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


class HGCSpider(scrapy.Spider):
    name = "hgc_backup"
    allowed_domains = ['shop.hgc.ch']
    start_urls = ['https://shop.hgc.ch']

    def __init__(self):
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.delete_all_cookies()
        self.driver.get('https://shop.hgc.ch')
        self.driver.find_element_by_xpath("//*[@class='content']/a").click()

        self.cat_id = self.driver.find_element_by_xpath(
            "//*[contains(@class, 'ui-state-default')]/a").get_attribute(
                "data-id")

        cookies = self.driver.get_cookies()
        self.cookies = {i['name']: i['value'] for i in cookies}
        self.headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-CH,de-DE;q=0.9,de;q=0.8,en-US;q=0.7,en;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://shop.hgc.ch/fis(bD1kZSZjPTAxMA==)/fisesales/search.htm?q=',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

        self.driver.close()
        self.i = 0
        self.post_url = 'https://shop.hgc.ch/FIS(bD1kZSZjPTAxMA==)/FISESALES/details.ws?event=GET_DETAILS&pitcher=search.htm&receiver='

    def parse(self, response):

        try:
            js = json.loads(response.text)

            if not js['response']['docs']:
                raise CloseSpider("No more items")

            for i in js['response']['docs']:
                id = i['matnr']
                product = HgcItem()
                product['id'] = id
                data = {'matnr': id}
                yield FormRequest(self.post_url,
                    callback=self.parse_json,
                    headers=self.headers, formdata=data,
                    cookies=self.cookies,
                    dont_filter = True,
                    meta = {"product": product})
            self.i += 50
        except JSONDecodeError:
            self.js = None
            self.log("Json Error")
            pass

        params = {
            'handler': 'search',
            'query': '*',
            'rows': '50',
            'start': str(self.i),
            'sort': 'score desc',
            'fuzzy': 'true',
            'catalogue_id': self.cat_id,
            'fq': '',
            'qf': ''#,
            # '_': str(random_with_N_digits(13))
        }

        url = "https://shop.hgc.ch/fis(bD1kZSZjPTAxMA==)/fisesales/search_solr.ws?" + urlencode(params)
        self.log("Batch = {}".format(self.i/50))


        yield scrapy.Request(url, headers=self.headers,
                             cookies=self.cookies, callback=self.parse,
                             dont_filter=True)


    def parse_json(self, response):
        product = response.meta['product']
        js = json.loads(response.text)
        product['detail'] = js
        yield(dict(product))
