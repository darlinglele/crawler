# encoding=utf-8
import socket
import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
import threadpool
import re
from Queue import Queue
from pymongo import MongoClient
from crawler import Crawler


class MilitaryCrawler(Crawler):

    def __init__(self, urls, url_pattern, pool_size=50, depth=4, encoding='utf-8'):
        Crawler.__init__(self, urls, url_pattern=url_pattern,
                         pool_size=pool_size, depth=depth, encoding=encoding)

    def save(self, url, soup):
        try:
            body = soup.find(id='chan_newsDetail')
            if body:
                soup = body.find(['script', 'style'])

                if soup:
                    [x.extract() for x in body(['script', 'style'])]
                content = body.text
                self.write('military/'+ str(hash(url)),content)
        except Exception, e:
            print e

if __name__ == '__main__':
    pattern = u'(http://military.china.com/news/.*)'
    crawler = MilitaryCrawler(
        ["http://military.china.com/news/index.html"], encoding='gb18030', depth=20, url_pattern=pattern)
    crawler.crawl()
