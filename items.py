#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy import Item, Field

class ProxyHunterItem(Item):

    prot = Field()  # 协议
    ip   = Field()  # 地址
    port = Field()  # 端口

    def __str__(self):
        return '{0[prot]}://{0[ip]}:{0[port]}'.format(self)


class ProxyInfoItem(Item):

    proxy    = Field()  # 代理地址 : prot://ip:port
    created  = Field()  # 创建时间 : unix-timestamp
    updated  = Field()  # 更新时间 : unix-timestamp
    latency  = Field()  # 访问延时 : (second)
    uptime   = Field()  # 在线累计 : (second)
    downtime = Field()  # 离线累计 : (second)
    status   = Field()  # 当前状态 : (bool)
    health   = Field()  # 健康状态 = uptime÷(uptime+downtime)×100%
    country  = Field()  # 国家代码 ∈ {CN, US, ID, ...}
    city     = Field()  # 城市名称 ∈ {bejing, shanghai, ...}
    anon     = Field()  # 是否匿名 : (bool)

