import ConfigParser
import socket
import threading
import time
import urllib2
import bs4
import urlparse
import threadpool
import re
import os


class Crawler():
    def __init__(self, task):
        socket.setdefaulttimeout(task.timeout)
        self.task_name = task.name
        self.urls = [task.begin_page]
        self.new_urls = set()
        self.pool_size = task.thread_pool_size
        self.url_pattern = task.url_pattern
        self.worker_pool = None
        self.depth = task.max_depth
        self.encoding = task.page_encoding
        self.indexed_urls = set()

    def crawl(self):
        if self.depth == 0 or len(self.urls) == 0:
            self.worker_pool.wait()
            return
        self.depth -= 1
        self.worker_pool = self.worker_pool or threadpool.ThreadPool(
            self.pool_size)
        requests = threadpool.makeRequests(self.request, self.urls, None)
        for req in requests:
            self.worker_pool.putRequest(req)
        self.worker_pool.wait()
        self.urls = self.new_urls
        self.new_urls = set()
        self.crawl()

    def request(self, url):
        try:
            content = urllib2.urlopen(url).read()
        except Exception, e:
            print e
            return

        soup = bs4.BeautifulSoup(content, from_encoding=self.encoding)
        self.indexed_urls.add(url)
        self.save_page(url, content)
        links = soup('a')
        for link in links:
            if 'href' in dict(link.attrs):
                new_url = urlparse.urljoin(url, link['href']).strip()
                if new_url.find("'") != -1:
                    continue
                new_url = new_url.split('#')[0]
                if new_url[0:4] == 'http' and self.url_pattern.match(new_url) and not self.is_indexed(
                        new_url) and new_url not in self.urls:
                    self.new_urls.add(new_url)

    def is_indexed(self, page):
        return page in self.indexed_urls


    def save_page(self, url, page_content):
        try:
            dir_name = self.task_name
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            file_name = str(time.time()) + str(threading.current_thread().ident)
            f = open(os.path.join(dir_name, file_name), 'w')
            f.write(page_content)
            f.close()
        except  Exception, e:
            print e


class Task():
    def __init__(self, name, config_items):
        self.name = name
        self.begin_page = config_items['begin_page']
        self.url_pattern = re.compile(config_items['url_pattern'])
        self.page_encoding = config_items['page_encoding']
        self.thread_pool_size = int(config_items['thread_pool_size'])
        self.max_depth = int(config_items['max_depth'])
        self.timeout = int(config_items['timeout'])


class TaskManager():
    def __init__(self, config_file):
        try:
            config_parser = ConfigParser.ConfigParser()
            config_parser.read(config_file)
            task_sections = config_parser.sections()
            task_lst = [Task(task_section, {x[0]: x[1] for x in config_parser.items(task_section)}) for task_section in
                        task_sections]
            self.task_lst = task_lst
            self.crawler_lst = []
        except Exception, e:
            print 'Error raised when parse config file!'
            raise e


    def start_all(self):
        if len(self.task_lst) == 0:
            print 'there is no task assigned in config file!'
        for task in self.task_lst:
            self.crawler_lst.append(Crawler(task))

        for crawler in self.crawler_lst:
            if crawler is not None:
                print 'Task ', crawler.task_name, ' is begin...'
                crawler.crawl()

        print 'All tasks finished!'


if __name__ == '__main__':
    task_manager = TaskManager('task.config')
    task_manager.start_all()






