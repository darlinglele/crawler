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


class CultureCrawler(Crawler):

    def __init__(self, urls, url_pattern, pool_size=30, depth=4, encoding='utf-8'):
        Crawler.__init__(self, urls, url_pattern=url_pattern,
                         pool_size=pool_size, depth=depth, encoding=encoding)

    def save(self, url, soup):
        try:
            body = soup.find(id='Cnt-Main-Article-QQ')
            if body:
                soup = body.find(['script', 'style'])

                if soup:
                    [x.extract() for x in body(['script', 'style'])]
                content = body.text
                self.write('culture/' + str(hash(url)), content.encode('utf-8'))
        except Exception, e:
			print e        

if __name__ == '__main__':
    db = MongoClient().culture.pages
    db.remove()
    pattern = u'(http://cul.qq.com/a/.*)'
    crawler = CultureCrawler(
        ["http://cul.qq.com"], encoding='gb18030', depth=20, url_pattern=pattern)
    crawler.crawl()
