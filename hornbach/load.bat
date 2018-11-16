del cats.json
del products.json
del products_detail.json

scrapy crawl hornbach_cats -o cats.json
scrapy crawl hornbach_products -o products.json
scrapy crawl hornbach_products_detail -o products_detail.json