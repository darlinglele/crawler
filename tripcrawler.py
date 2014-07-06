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


class TripCrawler(Crawler):

    def __init__(self, urls, url_pattern, timeout=30, pool_size=50, depth=4, encoding='utf-8'):
        Crawler.__init__(self, urls, url_pattern=url_pattern,
                         timeout=timeout, pool_size=pool_size, depth=depth, encoding=encoding)

    def save(self, url, soup):
        try:
            body = soup.find(_class='article-content')
            if body:
                soup = body.find(['script', 'style'])

                if soup:
                    [x.extract() for x in body(['script', 'style'])]
                content = body.text
                print '******', content.encode('utf-8'), '******'
                self.write('trip/' + str(hash(url)), content.encode('utf-8'))
        except Exception, e:
            print e

if __name__ == '__main__':
    db = MongoClient().trip.pages
    # db.remove()
    pattern = u'(http://trip.elong.com/news/.*)'
    crawler = TripCrawler(["http://trip.elong.com/"],
                          encoding='utf-8', depth=20, url_pattern=pattern)
    crawler.crawl()
