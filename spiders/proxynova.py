#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.utils.markup import remove_tags
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from proxyhunter.items import ProxyHunterItem

class ProxynovaSpider(Spider):

    name = "proxynova"
    allowed_domains = ["www.proxynova.com"]
    start_urls = ['http://www.proxynova.com/proxy-server-list/']

    def parse(self, response):

        for e in response.xpath('//table[@id="tbl_proxy_list"]//tr[count(td)=6]'):
            l = ItemLoader(ProxyHunterItem(), selector=e)
            l.add_value('prot', 'http')
            l.add_xpath('ip', 'td[1]', TakeFirst(), remove_tags, unicode.strip)
            l.add_xpath('port', 'td[2]', TakeFirst(), remove_tags, unicode.strip)
            yield l.load_item()

