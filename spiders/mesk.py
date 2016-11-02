#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from scrapy.utils.markup import remove_tags
from proxyhunter.items import ProxyHunterItem


class MeskSpider(CrawlSpider):

    name = 'mesk'
    allowed_domains = ['www.mesk.cn']
    start_urls = ['http://www.mesk.cn']

    rules = [
        Rule(LinkExtractor(restrict_xpaths=u'//div[contains(@class,"list-box") and contains(h2,"网页代理")]/li[1]'), callback='parse_item')
    ]

    def parse_item(self, response):

        txt = remove_tags(response.css('div.article').extract()[0])

        for ip, port, prot in re.findall(r'(\d+\.\d+\.\d+\.\d+):(\d+)@(HTTPS?)', txt):

            yield ProxyHunterItem(
                prot=prot,
                ip=ip,
                port=port
            )

