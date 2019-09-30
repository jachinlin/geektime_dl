# coding: utf-8

import requests
from urllib.parse import urljoin
import os
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path

from tqdm import tqdm


class Downloader:

    def __init__(self, out_folder: str, workers: int = None):
        self._out_folder = out_folder
        if not os.path.isdir(out_folder):
            os.makedirs(out_folder)
        self._pool = ThreadPoolExecutor(max_workers=workers or 4)

    def run(self, url: str, file_name: str = 'outfile',
            pbar: bool = True) -> Future:
        return self._pool.submit(self._run, url, file_name, pbar)

    def _run(self, m3u8_url: str, file_name: str, pbar: bool):

        r = requests.get(m3u8_url, timeout=10)
        if not r.ok:
            raise Exception('message=requests_failed\turl={}'.format(r.url))
        body = r.content.decode()
        if not body:
            raise Exception('message=invalid_url:{}'.format(r.url))

        ts_list = [urljoin(m3u8_url, n.strip())
                   for n in body.split('\n') if n and not n.startswith("#")]
        if not ts_list:
            raise Exception('message=invalid_url:{}'.format(r.url))
        of = (file_name + '.'
              + ts_list[0].split('/')[-1].split('?')[0].split('.')[-1])
        with open(os.path.join(self._out_folder, of), 'wb') as outfile:
            if pbar:
                ts_list = tqdm(ts_list)
                ts_list.set_description('视频下载中:{}'.format(
                    Path(file_name).stem[:10]))
            for url in ts_list:
                r = requests.get(url, timeout=20)
                if r.ok:
                    outfile.write(r.content)

    def shutdown(self, wait: bool = True):
        return self._pool.shutdown(wait)
