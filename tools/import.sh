#!/bin/bash
# -*- coding: utf-8 -*-
#
# import proxy list to redis
#

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS="redis-cli --raw -h $REDIS_HOST -p $REDIS_PORT -n $REDIS_DB"

grep -P '^https?://\d+\.\d+\.\d+\.\d+:\d+$' |
    while read proxy
    do
        ok=$($REDIS SADD index $proxy)
        if ((ok==1))
        then
            echo -n .
            NOW=$(date +%s)
            >/dev/null $REDIS LPUSH queue $proxy
            >/dev/null $REDIS HMSET $proxy created $NOW updated $NOW latency 15 status 0 uptime 0 downtime 0 health 0
        else
            echo -n x
        fi
    done

