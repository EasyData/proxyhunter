#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import task
from scrapy import log, signals
from scrapy.exceptions import NotConfigured
from proxyhunter.utils import rdb, mdb

class RedisToMongo(object):
    u'''Redis ⇒ Mongo'''

    def __init__(self):

        self.interval = 600 # 10min

    @classmethod
    def from_crawler(cls, crawler):

        o = cls()
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):

        if spider.name == 'checker':
            self.task = task.LoopingCall(self.redis_to_mongo)
            self.task.start(self.interval)

    def redis_to_mongo(self):

        up, down, ok, error = mdb.import_db(rdb.export_db())
        msg = 'UP:{}, DOWN:{}, OK:{}, ERROR:{}'.format(up, down, ok, error)
        log.msg('redis => mongo ({})'.format(msg), level=log.INFO)

    def spider_closed(self, spider):

        if spider.name == 'checker' and self.task.running:
            self.task.stop()

