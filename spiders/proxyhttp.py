#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import operator
from scrapy import Spider
from scrapy.contrib.loader import ItemLoader
from scrapy.utils.markup import remove_tags
from proxyhunter.items import ProxyHunterItem


class ProxyhttpSpider(Spider):

    name = 'proxyhttp'
    allowed_domains = ['proxyhttp.net']
    start_urls = ['http://proxyhttp.net/free-list/anonymous-server-hide-ip-address/%d'%i for i in range(1,10)]

    def parse(self, response):

        js = response.xpath('//div[@id="proxylist"]/following-sibling::script/text()').extract()[0]
        self.js_init(js)

        for e in response.xpath('//table[@class="proxytbl"]//tr[td]'):
            l = ItemLoader(ProxyHunterItem(), selector=e)
            l.add_xpath('ip', 'td[1]/text()')
            l.add_xpath('port', 'td[2]/script/text()', lambda xs: self.js_calc(xs[0]))
            l.add_xpath('prot', 'td[5]', lambda xs:'http' if remove_tags(xs[0]).strip()=='-' else 'https')
            yield l.load_item()

    def js_init(self, js):
        '''extract variables from js

        //<![CDATA[
           Polymorth = 13145;BigProxy = 18945^52967;NineBeforeZero = 19465^BigProxy;
           DontGrubMe = 50816^NineBeforeZero;Defender = 9376^BigProxy;SmallBlind = Polymorth^NineBeforeZero;
        //]]>
        '''

        self.lookup = {}
        for x,y,z in re.findall(r'(\w+) = (\w+)(?:\^(\w+))?;', js):
            self.lookup[x] = self.js_get(y)^self.js_get(z)

    def js_get(self, x):
        '''variable lookup from hash'''

        return self.lookup[x] if x in self.lookup else int(x or 0)

    def js_calc(self, x):
        '''calculate js math expression

        //<![CDATA[
          document.write(ProxyMoxy^Xinemara^35378);
        //]]>
        '''

        port = reduce(operator.xor, [
            self.js_get(i) for i in re.search(r'\((\w+)\^(\w+)\^(\w+)\)', x).groups()
        ])
        return str(port)

