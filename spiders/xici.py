#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from scrapy import Spider
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from proxyhunter.items import ProxyHunterItem


class XiciSpider(Spider):

    name = 'xici'
    allowed_domains = ['www.xici.net.co']
    start_urls = ['http://www.xici.net.co/']

    def parse(self, response):

        for e in response.xpath('//table[@id="ip_list"]//tr[contains(td[6],"HTTP")]'):
            l = ItemLoader(ProxyHunterItem(), selector=e)
            l.add_xpath('prot', 'td[6]/text()')
            l.add_xpath('ip', 'td[2]/text()')
            l.add_xpath('port', 'td[3]/text()')
            yield l.load_item()


class Xici2Spider(CrawlSpider):

    name = "xici2"
    allowed_domains = ["www.xici.net.co"]
    start_urls = ['http://www.xici.net.co/']

    rules = [
        Rule(LinkExtractor(restrict_xpaths=u'//ul[@id="nav"]//a[contains(.,"国")]'),             follow=True, callback='parse_item'),
        Rule(LinkExtractor(restrict_xpaths=u'//div[@class="pagination"]/a[@class="next_page"]'), follow=True, callback='parse_item'),
    ]

    def parse_item(self, response):

        for e in response.xpath('//table[@id="ip_list"]//tr[contains(td[6],"HTTP")]'):
            l = ItemLoader(ProxyHunterItem(), selector=e)
            l.add_xpath('prot', 'td[6]/text()')
            l.add_xpath('ip', 'td[2]/text()')
            l.add_xpath('port', 'td[3]/text()')
            yield l.load_item()

