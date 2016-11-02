#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import time
import redis
from urlparse import urlparse
from scrapy import Spider
from scrapy import log
from scrapy.http import Request
from proxyhunter import settings
from proxyhunter.items import ProxyInfoItem
from proxyhunter.utils import rdb


class CheckerSpider(Spider):
    '''proxy checker'''

    name = 'checker'
    allowed_domains = ['freegeoip.net', 'httpbin.org']
    download_timeout = 15
    download_delay = 0

    rdb = redis.StrictRedis.from_url(settings.REDIS_URI)

    def start_requests(self):

        # TODO: check HTTPS protocol
        url = 'http://freegeoip.net/json/'
        while True:
            now = time.time()
            proxy = rdb.poll()
            meta = {'proxy':proxy, 'dont_retry':True}
            yield Request(url, meta=meta, dont_filter=True, callback=self.parse_geo, errback=self.error_geo)

    def parse_geo(self, response):

        meta = response.meta
        proxy = meta['proxy']
        obj = {
            'latency': meta['download_latency']
        }

        try:
            obj.update(json.loads(response.body))
            ip1 = urlparse(proxy).netloc.split(':')[0]
            ip2 = obj['ip']
            return self.store(proxy, obj, ip1==ip2)
        except:
            self.store(proxy, obj, False)

    def error_geo(self, failure):

        meta = failure.request.meta
        proxy = meta['proxy']
        obj = {
            'latency': self.download_timeout
        }
        self.store(proxy, obj, False)

    def store(self, proxy, obj, status):

        info = {}
        info['updated'] = time.time()
        info['latency'] = obj['latency']
        info['status'] = status
        info['country'] = obj.get('country_code', '').upper()
        info['city'] = obj.get('city', '').lower()

        ok = rdb.update(proxy, info)
        result = 'accept' if ok else 'reject'
        msg = '{0} ({1[latency]:.2f}s) [{1[status]}]({2})'.format(proxy, info, result)
        self.log(msg, level=log.DEBUG)

        if status:
            return self.check_anon(proxy)

    def check_anon(self, proxy):

        info = rdb.get(proxy)
        if 'anon' not in info:
            url = 'http://httpbin.org/ip'
            meta = {'proxy':proxy, 'dont_retry':True}
            return Request(url, meta=meta, dont_filter=True, callback=self.parse_anon)

    def parse_anon(self, response):

        meta = response.meta
        proxy = meta['proxy']

        try:
            obj = json.loads(response.body)
            anon = ',' not in obj['origin']
            rdb.update_anon(proxy, anon)
        except:
            pass

