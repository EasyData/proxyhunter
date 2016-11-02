#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import redis
from scrapy.exceptions import DropItem
from proxyhunter import settings
from proxyhunter.utils import rdb

class BasicPipeline(object):

    def process_item(self, item, spider):

        for k in item.fields:
            v = item[k]
            if isinstance(v, list):
                v = v[0]
            item[k] = v

        if self.check(item):
            return item
        else:
            raise DropItem('bad proxy')

    def check(self, item):
        '''校验item是否合法, 并且进行数据清洗
           1. 协议(prot): [http, https]
           2. 地址(ip): xxx.xxx.xxx.xxx
           3. 端口(port): (0,65535]
        '''

        prot = item['prot'].strip().lower()
        if prot not in ['http', 'https']:
            return False
        item['prot'] = prot

        ip = item['ip'].strip()
        if not re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
            return False
        item['ip'] = ip

        port = int(item['port'].strip())
        if not 0<port<65536:
            return False
        item['port'] = port

        return True


class DebugPipeline(object):

    def open_spider(self, spider):

        self.enabled = hasattr(spider, 'debug') and spider.debug

    def process_item(self, item, spider):

        if self.enabled:
            print item
        return item


class RedisPipeline(object):

    def open_spider(self, spider):

        pass

    def process_item(self, item, spider):

        proxy = str(item)
        if rdb.add(proxy):
            return item
        else:
            raise DropItem('duplicated item')

    def close_spider(self, spider):

        pass

