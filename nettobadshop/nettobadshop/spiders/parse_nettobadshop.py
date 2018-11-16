import scrapy
from urllib.parse import urljoin


class ProductsSpider(scrapy.Spider):
    name = "nettobadshop"
    start_urls = [
        'https://www.nettobadshop.ch'
    ]
    allowed_domains = ['www.nettobadshop.ch']

    def parse(self, response):
        cats = response.xpath(
            "//*[contains(@class, 'megamenu-content')]/div/div/a/@href")
        cats = cats.extract()

        for c in cats:
            url = urljoin(response.url, c)
            yield scrapy.Request(url, callback=self.parse_menu)

    def parse_menu(self, response):

        products = response.xpath(
            "//*[contains(@class, 'product-cell')]/a/@href")
        products = products.extract()

        for p in products:
            url = urljoin(response.url, p)
            yield scrapy.Request(url, callback=self.parse_product)

        for next_page in response.css('.next > a'):
            yield response.follow(next_page, self.parse_menu)


    def parse_product(self, response):
        header = response.xpath(
            "//*[contains(@class, 'fn product-title')]/text()")
        header = header.extract_first()

        supplier = response.xpath(
            "//*[contains(@class, 'manufacturer-row')]/a/@title")
        supplier = supplier.extract_first()

        category = response.xpath(
            "//*[contains(@class, 'product-category')]/a/text()")
        category = category.extract_first()

        id = response.xpath(
            "//*[contains(@class, 'text-muted product-sku')]/span/text()")
        id = id.extract_first()
        price = response.xpath(
            "//*[contains(@class, 'price')]/meta/@content")
        price = price.extract_first()

        yield {"id": id,
               "category": category,
               "supplier": supplier,
               "header": header,
               "price": price}

        for next_form in response.css('.product-offer > link'):
            yield response.follow(next_form, self.parse_product)
