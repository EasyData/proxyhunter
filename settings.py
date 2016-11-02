#!/usr/bin/env python
# -*- coding: utf-8 -*-

BOT_NAME = 'proxyhunter'
LOG_LEVEL = 'INFO'

SPIDER_MODULES = ['proxyhunter.spiders']
NEWSPIDER_MODULE = 'proxyhunter.spiders'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:31.0) Gecko/20100101 Firefox/31.0'

ITEM_PIPELINES = {
    'proxyhunter.pipelines.BasicPipeline': 0,
    'proxyhunter.pipelines.DebugPipeline': 1,
    'proxyhunter.pipelines.RedisPipeline': 2,
    'proxyhunter.pipelines.StatsPipeline': 3,
}

EXTENSIONS = {
    'proxyhunter.extensions.RedisToMongo': 999
}

DOWNLOAD_DELAY = 0.5

REDIS_URI = 'redis://localhost:6379/0'
MONGO_URI = 'mongodb://localhost:27017/easydata.proxyhunter'

TELNETCONSOLE_ENABLED = False
WEBSERVICE_ENABLED = False

