import scrapy
import json
from scrapy.http import FormRequest
from urllib.parse import urljoin
from hgc.items import HgcItem
from selenium import webdriver

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


def load_ids():
    with open('ids.json') as f:
        js = json.load(f)
    return [i['id'] for i in js]


class ProductsSpider(scrapy.Spider):
    name = "hgc_item_detail"
    start_urls = [
        'https://shop.hgc.ch'
    ]
    allowed_domains = ['shop.hgc.ch']

    def __init__(self):
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.get('https://shop.hgc.ch')
        cookies = self.driver.get_cookies()
        self.cookies = {i['name']: i['value'] for i in cookies}
        self.ids = load_ids()
        self.post_url = 'https://shop.hgc.ch/FIS(bD1kZSZjPTAxMA==)/FISESALES/details.ws?event=GET_DETAILS&pitcher=search.htm&receiver='
        self.headers = {
            'Origin': 'https://shop.hgc.ch',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-CH,de-DE;q=0.9,de;q=0.8,en-US;q=0.7,en;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://shop.hgc.ch/FIS(bD1kZSZjPTAxMA==)/FISESALES/search.htm?q=',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }
        self.driver.close()
    def parse(self, response):

        for i, id in enumerate(self.ids):
            product = HgcItem()
            product['id'] = id
            data = {'matnr': id}
            yield FormRequest(self.post_url,
                callback=self.parse_json,
                headers=self.headers, formdata=data,
                cookies=self.cookies,
                dont_filter = True,
                meta = {"product": product})

    def parse_json(self, response):
        product = response.meta['product']
        js = json.loads(response.text)
        product['detail'] = js
        yield(dict(product))
