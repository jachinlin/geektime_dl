# coding=utf8

from threading import Thread
try:
    from queue import Queue, Empty as QueueEmpty
except ImportError:
    from Queue import Queue, Empty as QueueEmpty

import requests

#
# try:
#     from queue import Empty as QueueEmpty                    # python3
# except ImportError:
#     from multiprocessing.queues import Empty as QueueEmpty   # python2


def fetch(url, method='GET', **kwargs):
    """
    fetch the url and return the http response body
    implement the same api as requests.request

    :param url:
    :param method: method for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of 'name': file-like-objects (or {'name': ('filename', fileobj)}) for multipart encoding upload.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) Float describing the timeout of the request.
    :param allow_redirects: (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :return: str (or unicode in python2) for the http response body

    """

    resp = requests.request(method, url, **kwargs)
    html_content = resp.text

    return html_content


class Spider(object):

    def __init__(self, parse_func, save_func):

        self.q_fetch = Queue()   # element (url, request_params_dict) content_dict is request_params
        self.q_parse = Queue()   # element (url, request_params_dict, content_dict) content_dict is {'content': response.content}
        self.q_save = Queue()    # element (url, request_params_dict, content_dict) content_dict is key_value_pair to save

        self._fetch = fetch
        self._parse = parse_func
        self._save = save_func

    def set_start_url(self, url, **kw):
        """

        :param url:
        :param kw:
        :return: None
        """
        self.q_fetch.put_nowait((url, kw))

    def start_fetch(self):
        while True:
            try:
                url, params = self.q_fetch.get(block=True, timeout=5)

                print('----- fetch start: url={} -----\n'.format(url))
                html_content = self._fetch(url, **params)
                print('----- fetch end: url={} -----\n'.format(url))

                self.q_parse.put_nowait((url, params, {'html_content': html_content}))

            except QueueEmpty:
                break

    def start_parse(self):
        while True:
            try:
                url, params, content = self.q_parse.get(block=True, timeout=5)

                print('----- parse start: url={} -----\n'.format(url))
                url_to_fetch_list, content_to_save = self._parse(url, params, html_content=content['html_content'])
                print('----- parse end: url={} -----\n'.format(url))

                # put new url to q_fetch
                for item in url_to_fetch_list:
                    self.q_fetch.put_nowait(item)

                # put to q_save
                self.q_save.put_nowait((url, params, {'content_to_save': content_to_save}))

            except QueueEmpty:
                break

    def start_save(self):
        while True:
            try:
                url, params, content = self.q_save.get(block=True, timeout=5)

                print('----- save start: url={} -----\n'.format(url))
                result = self._save(url, params, content=content['content_to_save'])
                print('----- save end: url={} -----\n'.format(url))

            except QueueEmpty:
                break

    def start_crawl(self):

        thread_pool_fetch = [Thread(target=self.start_fetch, args=()) for i in range(5)]
        thread_pool_parse = [Thread(target=self.start_parse, args=()) for i in range(5)]
        thread_pool_save = [Thread(target=self.start_save, args=()) for i in range(5)]

        for td in thread_pool_fetch:
            td.start()
        for td in thread_pool_parse:
            td.start()
        for td in thread_pool_save:
            td.start()

        for td in thread_pool_fetch:
            if td.is_alive():
                td.join()
        for td in thread_pool_parse:
            if td.is_alive():
                td.join()
        for td in thread_pool_save:
            if td.is_alive():
                td.join()


def parse(url, request_params, html_content):
    """
    parse content in html_content based on url
    :param url:
    :param html_content: http response body of url
    :return:
    """
    raise NotImplemented


def save(url, request_params, content):
    """
    save content based on url
    :param url:
    :param content:
    :return:
    """
    raise NotImplemented


if __name__ == '__main__':

    def parse(url, request_params, html_content):
        print(html_content)

        result = ([], '')

        if url == 'http://www.baidu.com':
            result = ([('http://www.sina.com', {}), ('http://www.qq.com', {})], 'welcome to baidu')

        if url == 'http://www.sina.com':
            result = ([], 'welcome to sina')

        if url == 'http://www.qq.com':
            result = ([], 'welcome to qq')

        return result


    def save(url, request_params, content):
        print(content)

    spider = Spider(parse, save)
    spider.set_start_url('http://www.baidu.com')
    spider.start_crawl()

