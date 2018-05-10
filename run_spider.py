# coding=utf8

from spider.spider import Spider
from spider import geektime

start_url = 'https://time.geekbang.org/serv/v1/column/all'
headers = {
    'Referer': 'https://time.geekbang.org/paid-content',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:59.0) Gecko/20100101 Firefox/59.0'
}
spider = Spider(geektime.parse, geektime.save)
spider.set_start_url(start_url, headers=headers, cookies=geektime.get_cookies())

spider.start_crawl()
