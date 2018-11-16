import scrapy
import json
import os
from urllib.parse import urljoin

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

class iDSpider(scrapy.Spider):
    name = "hgc_ids_old"
    allowed_domains = ['shop.hgc.ch']
    start_urls = ['https://shop.hgc.ch/FIS(bD1kZSZjPTAxMA==)/FISESALES/search.htm?q=']

    def __init__(self):
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        # self.driver = webdriver.Chrome()

        self.driver.delete_all_cookies()

    def parse(self, response):
        ids = set()
        self.driver.get(response.url)
        start = 0
        end = 9999
        while start != end:
            try:
                self.wait(100)
                elems = self.driver.find_elements_by_xpath(
                    "//*[contains(@id, 'searchResults')]/tr")
                for elem in elems:
                    ids.add(elem.get_attribute("data-matnr"))
            except (StaleElementReferenceException,
                    NoSuchElementException,
                    ElementNotVisibleException,
                    WebDriverException):
                continue
            try:
                next = self.driver.find_element_by_xpath(
                    '//*[contains(@class, "next pagination esi-button")]')
                next.click()
                self.wait(100)
            except (StaleElementReferenceException,
                    NoSuchElementException,
                    ElementNotVisibleException,
                    WebDriverException):
                break

            page =self.driver.find_elements_by_xpath(
                "//*[contains(@class, 'pagecount')]")
            page = page[0].text
            print("============\n{}\n============\n".format(page))
            page_split = page.split(" ")
            start = int(page_split[1])
            end = int(page_split[3])


        for i in ids:
            yield {"id": i}


    def wait(self, delay):
        try:
            WebDriverWait(self.driver,
                delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'addToCheckbox')))
            print("Page is ready!")
        except TimeoutException:
            print("Loading took too much time!")
