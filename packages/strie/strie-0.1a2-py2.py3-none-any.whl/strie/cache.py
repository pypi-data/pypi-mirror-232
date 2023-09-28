# coding:utf-8

import os
from typing import Optional

from cachetools import LRUCache

from .trie import radix
from .utils import testkey

CACHE_DEFAULT = 4096
CACHE_MINIMUM = 1000
CACHE_MAXIMUM = 100000


class scache:

    def __init__(self,
                 start: Optional[str] = None,
                 maxkeys: int = CACHE_DEFAULT,
                 maxobjs: int = CACHE_DEFAULT):
        assert start is None or isinstance(start, str) and os.path.isdir(start)
        assert isinstance(maxkeys, int)
        assert isinstance(maxobjs, int)

        maxkeys = min(max(CACHE_MINIMUM, maxkeys), CACHE_MAXIMUM)
        maxobjs = min(max(CACHE_MINIMUM, maxobjs), CACHE_MAXIMUM)

        self.__start: Optional[str] = start
        self.__cache_keys: LRUCache[str, str] = LRUCache(maxsize=maxkeys)
        self.__cache_objs: LRUCache[str, rope] = LRUCache(maxsize=maxobjs)

    def __search_key(self, key: str) -> str:
        assert testkey(key=key)

        # find from cache
        if key in self.__cache_keys:
            return self.__cache_keys[key]

        suffix = key[2:]
        prefix = os.path.join(self.__start, key[:2])

        if not os.path.exists(prefix):
            os.mkdir(prefix)
        assert os.path.isdir(prefix)

        while not os.path.isfile(os.path.join(prefix, suffix)):
            if len(suffix) == 2:
                break
            suffix = suffix[:-2]

        # cache and return
        path = os.path.join(prefix, suffix)
        self.__cache_keys[key] = path
        return path

    def __search_obj(self, key: str) -> rope:
        # find from cache
        if key in self.__cache_objs:
            return self.__cache_objs[key]

        object = key

        # cache and return
        self.__cache_objs[key] = object
        return object
