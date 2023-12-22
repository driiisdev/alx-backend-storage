#!/usr/bin/env python3

import functools
import redis
import requests
from requests_html import HTML
import typing


def counter(method: typing.Callable):
    """
    Counts the calls to the input method
    """

    @wraps(method)
    def count(self, url: str, *args, **kwargs) -> typing.Callable:
        """
        Caches the counts of visits to url
        """
        key = 'count:' + url
        self._redis.incr(key)
        self._redis.expire(key, 10)
        response = requests.get(url)
        content = HTML(response.content)
        return content

    return count


class Cache:
    """
    This class queries a webpage and monitors the number of visits to it
    """

    def __init__(self):
        """
        Initialize class
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @counter
    def get_page(self, url: str) -> typing.Union[str, HTML]:
        """
        This function ses the requests module to obtain
        the HTML content of a particular URL and returns it
        """
        key = 'count:' + url
        count = self._redis.get(key)
        if count:
            return HTML(count.decode('utf-8'))
        else:
            response = requests.get(url)
            content = HTML(response.content)
            self._redis.set(key, content.content.decode('utf-8'))
            self._redis.expire(key, 10)
            return content


if __name__ == '__main__':
    url = 'http://www.google.com'
    cache = Cache()
    print(cache.get_page(url))
