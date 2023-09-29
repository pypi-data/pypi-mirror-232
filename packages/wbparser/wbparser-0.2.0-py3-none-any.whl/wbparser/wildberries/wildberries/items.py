import scrapy


class WildberriesItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    priceU = scrapy.Field()
    salePriceU = scrapy.Field()
    picsAmt = scrapy.Field()
    colors = scrapy.Field()
    sizes = scrapy.Field()
    qty = scrapy.Field()
    supplierId = scrapy.Field()
    rating = scrapy.Field()
    feedbacksAmt = scrapy.Field()
