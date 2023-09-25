import json
import re

import scrapy

from ..items import WildberriesItem

SUCCESS_CODES = [200, 201]

# PAGE_URL = 'https://www.wildberries.ru/catalog/{}/detail.aspx'
AJAX_REQUEST__GOOD_INFO = f'https://card.wb.ru/cards/detail?' \
               'spp=0&regions=83,75,64,4,38,30,33,70,71,22,31,66,68,82,48,40,1,69,80' \
               '&stores=11767,117986,1733,686,132043' \
               '&pricemarginCoeff=1.0&reg=0&appType=1&offlineBonus=0&onlineBonus=0&emp=0&locale=ru&' \
               'lang=ru&curr=rub&couponsGeo=12,3,18,15,21&dest=-1029256,-102269,-2162196,-1257786&nm={}'
# AJAX_REQUEST_PRICE_HISTORY = 'https://basket-01.wb.ru/vol{}/part{}/{}/info/price-history.json'
# AJAX_REQUEST_SELLERS = 'https://basket-01.wb.ru/vol{}/part{}/{}/info/sellers.json'


class GoodsSpider(scrapy.Spider):
    name = 'goods'
    handle_httpstatus_list = [404]
    allowed_domains = ['www.wildberries.ru', 'wbxcatalog-ru.wildberries.ru', 'wbx-content-v2.wbstatic.net', 'card.wb.ru',
                       'product-order-qnt.wildberries.ru', 'basket-01.wb.ru']

    def __init__(self, id=None, wb_parser=None, *args, **kwargs):
        super(GoodsSpider, self).__init__(*args, **kwargs)
        self.id = id
        self.wb_parser = wb_parser

    def start_requests(self):
        item = WildberriesItem()
        item['id'] = self.id
        yield scrapy.Request(url=AJAX_REQUEST__GOOD_INFO.format(self.id), callback=self.parse_good_info,
                             cb_kwargs={'item': item, 'id': self.id})

    # def parse_page(self, response, **kwargs):
    #     item = kwargs['item']
    #     id_ = kwargs['id']
    #     if response.status in SUCCESS_CODES:
    #         item['rating'] = response.xpath('//span[contains(@class, "product-review__rating")]//text()').get()
    #         #item['comments'] = response.xpath("//span[@class='same-part-kt__count-review']/text()").get()[1:]
    #         item['description'] = response.xpath('//*[@id="container"]'
    #                                              '/div[3]/div[1]/section[3]/div[2]/div[1]/p/text()').get()
    #         item['questions'] = response.xpath('/html/body/div[1]/main/div[2]/div/div[2]/'
    #                                            'section[2]/div[2]/ul/li[2]/a/span/text()').get()
    #         yield scrapy.Request(url=AJAX_REQUEST__GOOD_INFO.format(id_), callback=self.parse_good_info,
    #                              cb_kwargs={'item': item, 'id': id_})
    #     else:
    #         yield item

    def parse_good_info(self, response, **kwargs):
        item = kwargs['item']
        id_ = kwargs['id']
        if response.status in SUCCESS_CODES:
            data = response.json()
            item['name'] = data['data']['products'][0]['name']
            item['brand'] = data['data']['products'][0]['brand']
            item['priceU'] = data['data']['products'][0]['priceU']
            item['salePriceU'] = data['data']['products'][0]['salePriceU']
            item['pics'] = data['data']['products'][0]['pics']
            item['colors'] = data['data']['products'][0]['colors']
            item['sizes'] = []
            item['qty'] = 0
            item['rating'] = data['data']['products'][0]['reviewRating']
            item['questions'] = data['data']['products'][0]["feedbacks"]
            item['diffPrice'] = data['data']['products'][0]['diffPrice']
            for size in data['data']['products'][0]['sizes']:
                item['sizes'].append(size['origName'])
                for stock in size['stocks']:
                    item['qty'] += stock['qty']
            # yield scrapy.Request(url=AJAX_REQUEST_SELLERS.format(id_[:3], id_[:5], id_), callback=self.parse_sellers_info,
            #                      cb_kwargs={'item': item, 'id': id_})
        if self.wb_parser:
            self.wb_parser.result = item
        yield item

    # def parse_sellers_info(self, response, **kwargs):
    #     item = kwargs['item']
    #     id_ = kwargs['id']
    #     if response.status in SUCCESS_CODES:
    #         data = response.json()
    #         try:
    #             item['supplierId'] = data['supplierId']
    #             item['supplierName'] = data['supplierName']
    #             item['inn'] = data['inn']
    #             item['legalAddress'] = data['legalAddress']
    #         except KeyError:
    #             pass
    #         id_ = str(id_)
    #         yield scrapy.Request(url=AJAX_REQUEST_PRICE_HISTORY.format(id_[:3], id_[:5], id_), callback=self.parse_history_info,
    #                              cb_kwargs={'item': item, 'id': id_})
    #     else:
    #         yield item


    # def parse_history_info(self, response, **kwargs):
    #     item = kwargs['item']
    #     if response.status in SUCCESS_CODES:
    #         data = response.json()
    #         item['price_history'] = data
    #         yield scrapy.Request(url=f'https://product-order-qnt.wildberries.ru/by-nm/?nm={kwargs.get("id")}',
    #                              callback=self.parse_qnt_info, cb_kwargs={'item': item, 'id': kwargs.get("id")})
    #     else:
    #         yield scrapy.Request(url=f'https://product-order-qnt.wildberries.ru/by-nm/?nm={kwargs.get("id")}',
    #                              callback=self.parse_qnt_info, cb_kwargs={'item': item, 'id': kwargs.get("id")})
    #
    # def parse_qnt_info(self, response, **kwargs):
    #     item = kwargs['item']
    #     if response.status in SUCCESS_CODES:
    #         data = response.json()
    #         qnt = data[0]['qnt']
    #         item['qty'] = data[0]['qnt']
    #     yield item