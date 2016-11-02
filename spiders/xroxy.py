#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy.contrib.loader import ItemLoader
from proxyhunter.items import ProxyHunterItem

class XroxySpider(Spider):

    name = "xroxy"
    allowed_domains = ["xroxy.com"]
    start_urls = ['http://www.xroxy.com/proxylist.php?port=&type=All_http&ssl=&country=&latency=&reliability=&sort=reliability&desc=true&pnum=%d'%i for i in range(10)]

    def parse(self, response):

        for e in response.xpath('//tr[contains(@class,"row")]'):
            l = ItemLoader(ProxyHunterItem(), selector=e)
            l.add_xpath('prot', 'td[5]/a/text()', lambda xs:'https' if xs[0].strip()=='true' else 'http')
            l.add_xpath('ip', 'td[2]/a/text()', lambda xs:xs[0].strip())
            l.add_xpath('port', 'td[3]/a/text()')
            yield l.load_item()

