import scrapy

from ..items import WildberriesItem

SUCCESS_CODES = [200, 201]

# PAGE_URL = 'https://www.wildberries.ru/catalog/{}/detail.aspx'
AJAX_REQUEST__GOOD_INFO = f'https://card.wb.ru/cards/detail?' \
               'spp=0&regions=83,75,64,4,38,30,33,70,71,22,31,66,68,82,48,40,1,69,80' \
               '&stores=11767,117986,1733,686,132043' \
               '&pricemarginCoeff=1.0&reg=0&appType=1&offlineBonus=0&onlineBonus=0&emp=0&locale=ru&' \
               'lang=ru&curr=rub&couponsGeo=12,3,18,15,21&dest=-1029256,-102269,-2162196,-1257786&nm={}'


class GoodsSpider(scrapy.Spider):
    name = 'goods'
    handle_httpstatus_list = [404]
    allowed_domains = ['www.wildberries.ru', 'wbxcatalog-ru.wildberries.ru', 'wbx-content-v2.wbstatic.net', 'card.wb.ru',
                       'product-order-qnt.wildberries.ru', 'basket-01.wb.ru']

    def __init__(self, wb_parser=None, *args, **kwargs):
        super(GoodsSpider, self).__init__(*args, **kwargs)
        self.wb_parser = wb_parser

    def start_requests(self):

        if self.wb_parser.urls:
            for url in self.wb_parser.urls:
                self.wb_parser.ids = self.wb_parser.ids or []
                self.wb_parser.ids.append(url.split('/')[-2])

        if self.wb_parser.ids:
            for id_to_crawl in self.wb_parser.ids:
                item = WildberriesItem()
                item['id'] = id_to_crawl
                yield scrapy.Request(url=AJAX_REQUEST__GOOD_INFO.format(id_to_crawl), callback=self.parse_good_info,
                                     cb_kwargs={'item': item, 'id': id_to_crawl})

    def parse_good_info(self, response, **kwargs):

        item = kwargs['item']
        if response.status in SUCCESS_CODES:
            data = response.json()
            item['name'] = data['data']['products'][0]['name']
            item['brand'] = data['data']['products'][0]['brand']
            item['priceU'] = data['data']['products'][0]['priceU'] // 100
            item['salePriceU'] = data['data']['products'][0]['salePriceU'] // 100
            item['picsAmt'] = data['data']['products'][0]['pics']
            item['colors'] = data['data']['products'][0]['colors']
            item['sizes'] = []
            item['qty'] = 0
            item['rating'] = data['data']['products'][0]['reviewRating']
            item['feedbacksAmt'] = data['data']['products'][0]["feedbacks"]
            item['supplierId'] = data['data']['products'][0]['supplierId']

            for size in data['data']['products'][0]['sizes']:
                item['sizes'].append(size['origName'])
                for stock in size['stocks']:
                    item['qty'] += stock['qty']

        if self.wb_parser:
            if not self.wb_parser.result:
                self.wb_parser.result = [dict(item)]
            else:
                self.wb_parser.result.append((dict(item)))

        yield item
