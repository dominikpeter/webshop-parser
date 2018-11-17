import json
import os
from random import randint

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.selector import Selector


from urllib.parse import urljoin, urlencode
from json.decoder import JSONDecodeError
from hgc.items import HgcItem
from scrapy.http import FormRequest

import requests
import re
import time
import math


class HGCSpider(scrapy.Spider):
    name = "hgc"
    allowed_domains = ['shop.hgc.ch']
    start_urls = ['https://shop.hgc.ch']

    def __init__(self):

        session = requests.Session()
        resp = session.get('https://shop.hgc.ch')

        self.cookies = session.cookies.get_dict()
        self.headers = {
            'Origin': 'https://shop.hgc.ch',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

        params = {"handler": "getusercatalogues",
                  "lang": "D",
                  "getusercatalogues": "true"}

        self.url = re.sub("dashboard.*", "search_solr.ws?", resp.url)
        self.post_url = re.sub("dashboard.*", "details.ws?", resp.url)
        self.post_url = self.post_url + "event=GET_DETAILS&pitcher=search.htm&receiver="
        resp = session.get(self.url + urlencode(params),
                           headers=self.headers)
        self.cat_id = resp.json()['catalogues'][0]['id']
        self.rows = 50

        params = {"handler": "search",
                  "query": "*",
                  "rows": "50",
                  "start": "50",
                  "sort": "score desc",
                  "fuzzy": "true",
                  "catalogue_id": str(self.cat_id),
                  "_": str(self.timestamp())
                  }

        resp = session.get(self.url + urlencode(params),
                           headers=self.headers)

        js = resp.json()
        self.number_of_items = js['response']['numFound']

        self.pages = math.ceil(self.number_of_items / self.rows)
        print(self.pages)


    def parse(self, response):

        for i in range(self.pages + 1):
            start = i * self.rows
            params = {
                'handler': 'search',
                'query': '*',
                'rows': '50',
                'start': str(start),
                'sort': 'score desc',
                'fuzzy': 'true',
                'catalogue_id': self.cat_id,
                'fq': '',
                'qf': '',
                '_': str(self.timestamp())
            }
            url = self.url + urlencode(params)

            yield scrapy.Request(url, headers=self.headers,
                                 cookies=self.cookies,
                                 callback=self.parse_matnr)

    def parse_matnr(self, response):
        try:
            js = json.loads(response.text)
            for i in js['response']['docs']:
                id = i['matnr']
                product = HgcItem()
                product['id'] = id
                data = {'matnr': str(id)}
                yield FormRequest(self.post_url,
                                  callback=self.parse_json,
                                  headers=self.headers,
                                  formdata=data,
                                  cookies=self.cookies,
                                  meta={"product": product})
        except JSONDecodeError:
            self.log("Json Error")
            pass

    def parse_json(self, response):
        product = response.meta['product']
        js = json.loads(response.text)
        product['detail'] = js
        yield dict(product)

    def timestamp(self):
        return int(round(time.time() * 1000))
