# coding=utf8

from multiprocessing import Queue, Process
import requests


try:
    from queue import Empty as QueueEmpty                    # python3
except ImportError:
    from multiprocessing.queues import Empty as QueueEmpty   # python2


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

        self.q_fetch = Queue()   # element (url, content_dict) content_dict is request_params
        self.q_parse = Queue()   # element (url, content_dict) content_dict is {'content': response.content}
        self.q_save = Queue()    # element (url, content_dict) content_dict is key_value_pair to save

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

                self.q_parse.put_nowait((url, {'html_content': html_content}))

            except QueueEmpty:
                break

    def start_parse(self):
        while True:
            try:
                url, content = self.q_parse.get(block=True, timeout=5)

                print('----- parse start: url={} -----\n'.format(url))
                url_to_fetch_list, content_to_save = self._parse(url, html_content=content['html_content'])
                print('----- parse end: url={} -----\n'.format(url))

                # put new url to q_fetch
                for item in url_to_fetch_list:
                    self.q_fetch.put_nowait(item)

                # put to q_save
                self.q_save.put_nowait((url, {'content_to_save': content_to_save}))

            except QueueEmpty:
                break

    def start_save(self):
        while True:
            try:
                url, content = self.q_save.get(block=True, timeout=5)

                print('----- save start: url={} -----\n'.format(url))
                result = self._save(url, content=content['content_to_save'])
                print('----- save end: url={} -----\n'.format(url))

            except QueueEmpty:
                break

    def start_crawl(self):
        p_fetch = Process(target=self.start_fetch, args=())
        p_parse = Process(target=self.start_parse, args=())
        p_save = Process(target=self.start_save, args=())

        p_fetch.start()
        p_parse.start()
        p_save.start()

        p_fetch.join()
        p_parse.join()
        p_save.join()


def parse(url, html_content):
    """
    parse content in html_content based on url
    :param url:
    :param html_content: http response body of url
    :return:
    """
    raise NotImplemented


def save(url, content):
    """
    save content based on url
    :param url:
    :param content:
    :return:
    """
    raise NotImplemented


if __name__ == '__main__':

    def parse(url, html_content):
        print(html_content)

        result = ([], '')

        if url == 'http://www.baidu.com':
            result = ([('http://www.sina.com', {}), ('http://www.qq.com', {})], 'welcome to baidu')

        if url == 'http://www.sina.com':
            result = ([], 'welcome to sina')

        if url == 'http://www.qq.com':
            result = ([], 'welcome to qq')

        return result


    def save(url, content):
        print(content)

    spider = Spider(parse, save)
    spider.set_start_url('http://www.baidu.com')
    spider.start_crawl()

