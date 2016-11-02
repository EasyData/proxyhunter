#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import redis
import pymongo
from scrapy import log

class MongoStorage(object):
    '''persistent storage'''

    def __init__(self, mongo_uri):
        '''connect mongo'''

        parts = pymongo.uri_parser.parse_uri(mongo_uri)
        host, port = parts['nodelist'][0]
        database = parts['database']
        collection = parts['collection']
        self.mdb = pymongo.MongoClient(host=host, port=port)[database][collection]

    def import_db(self, proxies):
        '''import proxies'''

        up = down = ok = error = 0

        for proxy, info in proxies:
            try:
                self.update(proxy, info)
                if info.get('status'):
                    up += 1
                else:
                    down += 1
                ok += 1
            except:
                error += 1

        return up, down, ok, error

    def update(self, proxy, info):
        '''update proxy meta-data'''

        info['proxy'] = proxy
        self.mdb.update({'proxy':proxy}, info, upsert=True)

class RedisStorage(object):
    '''caching storage

    KEY     TYPE    NOTE
    ----    ----    ----
    index   set     all proxies can be found here
    queue   list    round-robin queue (rpop/lpush)
    proxy   zset    good proxies (sorted by latency)
    trash   set     bad proxies to be deleted
    ----    ----    ----
    '''

    def __init__(self, redis_uri):

        self.rdb = redis.StrictRedis.from_url(redis_uri)

        # NO GC for some reason
        #from twisted.internet import task
        #self.task = task.LoopingCall(self.gc)
        #self.task.start(600, now=False) # 10min

    def add(self, proxy):
        '''add proxy to storage'''

        if self.rdb.sismember('trash', proxy):
            return False

        if self.rdb.sadd('index', proxy):
            log.msg('+++ '+proxy)
            now = time.time()
            self.rdb.lpush('queue', proxy)
            self.rdb.hmset(proxy, {
                'created': now,     # init
                'updated': now,     # update
                'latency': 15,      # update
                'status': 0,        # update
                'uptime': 0,        # calc
                'downtime': 0,      # calc
                'health': 0,        # calc
            })
            return True
        else:
            return False

    def kill(self, proxy):
        '''remove proxy from storage'''

        if self.rdb.sismember('trash', proxy):
            return

        log.msg('--- '+proxy)
        self.rdb.sadd('trash', proxy)

    def get(self, proxy):
        '''get proxy meta-data'''

        if not self.rdb.sismember('index', proxy):
            raise Exception('no such proxy')

        if not self.rdb.exists(proxy):
            raise Exception('no such proxy')

        info = self.rdb.hgetall(proxy)
        for k,v in info.iteritems():
            if k in ['country', 'city']:
                pass
            elif k in ['status', 'anon']:
                info[k] = bool(int(v))
            else:
                info[k] = float(v)
        info['health'] = info['uptime']/(info['uptime']+info['downtime']+0.01)
        return info

    def update_anon(self, proxy, anon):
        '''update proxy meta-data(anonymous)'''

        try:
            info = self.get(proxy)
            self.rdb.hset(proxy, 'anon', int(anon))
            return True
        except:
            return False

    def update(self, proxy, info):
        '''update proxy meta-data'''

        try:

            ori_info = self.get(proxy)
            diff = info['updated'] - ori_info['updated']
            status = info['status']

            if 'anon' in ori_info:
                anon = ori_info['anon']
                ori_info['anon'] = int(anon)

            ori_info['status'] = int(status)
            ori_info['uptime' if status else 'downtime'] += diff
            ori_info['latency'] = info['latency']
            ori_info['updated'] = info['updated']
            ori_info['country'] = info['country']
            ori_info['city'] = info['city']

            self.rdb.hmset(proxy, ori_info)

            if status:
                self.rdb.zadd('proxy', info['latency'], proxy)
            else:
                self.rdb.zrem('proxy', proxy)

            return True

        except:

            return False

    def poll(self):
        '''poll proxy from round-robin queue'''

        while True:
            proxy = self.rdb.rpop('queue')
            if not proxy:
                time.sleep(1)
                raise Exception('queue is empty')
            elif self.rdb.sismember('trash', proxy):
                self.rdb.delete(proxy)
                self.rdb.srem('index', proxy)
                self.rdb.srem('trash', proxy)
            elif not self.rdb.sismember('index', proxy):
                pass
            else:
                self.rdb.lpush('queue', proxy)
                return proxy

    def gc(self):
        '''
        Garbage Collection
        ==================

        KILL
        ----
        1. old enough
        2. not healthy
        3. host is down
        '''

        gc_age = 3600
        gc_health = 0.05

        log.msg('=== Garbage Collection ===')

        now = time.time()
        cur = 0

        while True:

            cur, proxies = self.rdb.sscan('index', cur)
            for proxy in proxies:
                info = self.get(proxy)
                age = now - info['created']
                if (age > gc_age) and (info['health'] < gc_health) and (not info['status']):
                    self.kill(proxy)

            if not cur:
                break

    def export_db(self):
        '''export proxies'''

        for proxy in self.rdb.smembers('index'):
            try:
                info = self.get(proxy)
                yield (proxy, info)
            except:
                pass

