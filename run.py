# coding=utf8

from spider import Spider
import geektime

start_url = 'todo'
spider = Spider(geektime.parse, geektime.save)
spider.set_start_url(start_url)
spider.start_crawl()

