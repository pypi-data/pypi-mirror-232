# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,R0912,R0915,W0105,E0402,R0903


"caching"


from .object import Object


def __dir__():
    return (
            'Cache',
           ) 


class Cache(Object):

    cache = {}

    @staticmethod
    def size(chan):
        if chan in Cache.cache:
            return len(Cache.cache.get(chan, []))
        return 0
