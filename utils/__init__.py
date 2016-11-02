#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import settings
from .storage import RedisStorage, MongoStorage

rdb = RedisStorage(settings.REDIS_URI)
mdb = MongoStorage(settings.MONGO_URI)

