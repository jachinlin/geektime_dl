# coding=utf8

from spider import spider as geektime_spider

import time
start = time.time()
geektime_spider.start_crawl()

print('time cost is %s' % (time.time() - start))

