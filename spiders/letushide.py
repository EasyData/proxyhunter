#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import ItemLoader
from scrapy.utils.markup import remove_tags
from proxyhunter.items import ProxyHunterItem


class LetushideSpider(CrawlSpider):

    name = 'letushide'
    allowed_domains = ['letushide.com']
    start_urls = [
        'http://letushide.com/filter/http,all,all/list_of_free_HTTP_proxy_servers',
        'http://letushide.com/filter/https,all,all/list_of_free_HTTPS_proxy_servers',
    ]

    rules = [
        Rule(LinkExtractor(restrict_xpaths='//ul[@id="page"]'), callback='parse_item')
    ]

    def parse_item(self, response):

        for e in response.xpath('//table[@id="basic"]/tbody/tr'):
            l = ItemLoader(ProxyHunterItem(), selector=e)
            l.add_xpath('ip', 'td[2]/a/text()')
            l.add_xpath('port', 'td[3]/text()')
            l.add_xpath('prot', 'td[4]/a/text()')
            yield l.load_item()

    parse_start_url = parse_item

