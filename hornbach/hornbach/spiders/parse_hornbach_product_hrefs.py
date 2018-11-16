import scrapy
import json
import os
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")

def load_cat_hrefs():
    try:
        with open("cats.json") as f:
            js = json.load(f)
        links = [i['url'] for i in js]
        return links
    except FileNotFoundError:
        pass


class ProductsSpider(scrapy.Spider):
    name = "hornbach_products"
    allowed_domains = ['hornbach.ch']
    start_urls = ['https://www.hornbach.ch']

    def __init__(self):
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def parse(self, response):
        urls = load_cat_hrefs()
        links = []
        for url in urls:
            self.driver.get(url)
            while True:
                try:
                    elems = self.driver.find_elements_by_xpath(
                        "//*[contains(@class, 'title-link')]")
                    for elem in elems:
                        links.append(elem.get_attribute("href"))
                except (StaleElementReferenceException,
                        NoSuchElementException,
                        ElementNotVisibleException,
                        WebDriverException):
                    continue
                try:
                    next = self.driver.find_element_by_xpath(
                        '//*[@class="paging-btn right"]')
                    next.click()
                except (StaleElementReferenceException,
                        NoSuchElementException,
                        ElementNotVisibleException,
                        WebDriverException):
                    break
        for i in links:
            yield {"url": i}
