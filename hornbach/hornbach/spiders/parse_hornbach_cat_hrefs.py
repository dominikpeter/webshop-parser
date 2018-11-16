import scrapy
import json
import os
from urllib.parse import urljoin


class CatSpider(scrapy.Spider):
    name = "hornbach_cats"
    start_urls =  [
        'https://www.hornbach.ch/cms/de/ch/sortiment/bad-sanitaer.html?WT.z_navi=dd',
        'https://www.hornbach.ch/cms/de/ch/sortiment/baustoffe-holz-fenster-tueren.html?WT.z_navi=dd',
        'https://www.hornbach.ch/cms/de/ch/sortiment/bodenbelaege.html?WT.z_navi=dd',
        'https://www.hornbach.ch/cms/de/ch/sortiment/eisenwaren.html?WT.z_navi=dd',
        'https://www.hornbach.ch/cms/de/ch/sortiment/farben-tapeten.html?WT.z_navi=dd',
        'https://www.hornbach.ch/cms/de/ch/sortiment/garten.html?WT.z_navi=dd',
        'https://www.hornbach.ch/cms/de/ch/sortiment/heizen-klima-lueftung.html?WT.z_navi=dd',
        'https://www.hornbach.ch/cms/de/ch/sortiment/kueche.html?WT.z_navi=dd',
        'https://www.hornbach.ch/cms/de/ch/sortiment/maschinen-werkzeuge-werkstatt.html?WT.z_navi=dd'
        ]
    allowed_domains = ['hornbach.ch']

    def parse(self, response):
        xpath="//*[contains(@class, 'sub')]/a/@href"
        for i in response.xpath(xpath).extract():
            yield {"url": urljoin("https://www.hornbach.ch", i)}
