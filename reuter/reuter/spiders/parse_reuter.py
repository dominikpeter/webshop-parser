import scrapy
import json
from urllib.parse import urljoin
from reuter.items import ReuterItem

def save_extract(d, key):
    try:
        extract = d[key]
    except KeyError:
        extract = None
    return extract

def load_json(file):
    with open('headers.json') as f:
        headers = json.load(f)
    return headers


class ProductsSpider(scrapy.Spider):
    name = "reuter"
    start_urls = [
        'https://www.reuter.de/bad.html',
        'https://www.reuter.de/kueche.html',
        'https://www.reuter.de/heizung.html'
    ]
    allowed_domains = ['reuter.de']

    def parse(self, response):
        products = response.xpath(
            "//*[contains(@class, 'c-product-tile')]/a/@href").extract()
        for p in products:
            url = urljoin(response.url, p)
            yield scrapy.Request(url, callback=self.parse_product)

        for next_page in response.css('.c-ajax-pagination__control > a'):
            yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        supplier = response.xpath(
            "//*[contains(@class, 'medium-5 columns')]/a/img/@title")
        supplier = supplier.extract_first()
        header = response.xpath(
            "//*[contains(@class, 'o-product-detail-title')]/span/text()")
        header = header.extract_first()
        price = response.xpath(
            "//*[contains(@class, 'c-price-block__price-price')]/text()")
        price = price.extract_first()
        val = response.xpath(
            "//*[contains(@class, 'c-definition-list__value')]/text()")
        val = val.extract()
        attr = response.xpath(
            "//*[contains(@class, 'c-definition-list__attribute')]/text()")
        attr = attr.extract()

        attribute = dict(zip(attr, val))

        product = ReuterItem()
        product['supplier'] = supplier
        product['header'] = header
        product['price'] = price
        product['attribute'] = attribute

        yield dict(product)

        ids = response.xpath(
            "//*[contains(@qa-data, 'product-model--list')]/li/@data-value")
        ids = ids.extract()

        for id in ids:
            headers = load_json('headers.json')
            referer = response.url
            headers['referer'] = referer

            url_link = urljoin("https://www.reuter.de/api/v1/product/", id)

            yield scrapy.Request(url_link, method="GET", headers=headers,
                                 callback=self.parse_json)


    def parse_json(self, response):
        js = json.loads(response.text)

        productConfig = js['databind']['productConfiguration']

        price = save_extract(productConfig, 'productPrice')
        supplier = save_extract(productConfig, 'manufacturerName')
        header = save_extract(productConfig, 'productName')

        attribute =  {"Artikelnummer:": save_extract(productConfig,
                                                     'productModel'),
                      "Serie:": save_extract(productConfig, 'series')}

        detailsTop = save_extract(productConfig, 'detailsTop')

        if detailsTop:
            for i, k in enumerate(detailsTop):
                attribute['key_{}'.format(i)] = detailsTop[k]['value']

        product = ReuterItem()
        product['supplier'] = supplier
        product['header'] = header
        product['price'] = price
        product['attribute'] = attribute

        yield dict(product)
