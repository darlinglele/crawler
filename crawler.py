import socket
import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
import threadpool
import re
from Queue import Queue
import os
from pymongo import MongoClient


class Crawler():

    def __init__(self, urls, url_pattern=u'.*', timeout=3, pool_size=30, depth=2, encoding='utf8'):
        socket.setdefaulttimeout(timeout)
        self.urls = urls
        self.new_urls = set()
        self.worker_pool = None
        self.pool_size = pool_size
        self.url_pattern = re.compile(url_pattern)
        self.depth = depth
        self.encoding = encoding
        self.indexed_urls = set()

    def crawl(self):
        if self.depth == 0:
            print 'reach the edge....'
            return
        self.depth -= 1
        self.worker_pool = self.worker_pool or threadpool.ThreadPool(
            self.pool_size)
        requests = threadpool.makeRequests(self.retrieval, self.urls, None)
        for req in requests:
            self.worker_pool.putRequest(req)
        self.worker_pool.wait()
        self.urls = self.new_urls
        self.new_urls = set()
        print len(self.urls)
        print self.urls
        self.crawl()

    def retrieval(self, page):
        try:
            c = urllib2.urlopen(page)
        except:
            print 'could not open ', page.encode(self.encoding)
            return

        soup = BeautifulSoup(c.read(), from_encoding=self.encoding)
        self.indexed_urls.add(page)
        self.save(page, soup)
        links = soup('a')
        for link in links:
            if 'href' in dict(link.attrs):
                url = urljoin(page, link['href']).strip()
                if url.find("'") != -1:
                    continue
                url = url.split('#')[0]
                if url[0:4] == 'http' and self.url_pattern.match(url) and not self.isindexed(url) and url not in self.urls:
                    self.new_urls.add(url)

    def isindexed(self, page):
        return page in self.indexed_urls

    def write(self, file, content):
    	dir = file.split('/')[0]
    	if not os.path.exists(dir):
    		os.makedirs(dir)
    	f = open(file, 'w')
    	f.write(content)
    	f.close()

