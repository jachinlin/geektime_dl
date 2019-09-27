# coding=utf8

import os
import sys
from concurrent.futures import ThreadPoolExecutor, Future

import requests


class Downloader:
    def __init__(self, out_folder: str, workers: int = None):
        self._out_folder = out_folder
        if not os.path.isdir(out_folder):
            os.makedirs(out_folder)
        self._pool = ThreadPoolExecutor(max_workers=workers or 4)

    def run(self, url: str, file_name: str = 'outfile') -> Future:
        return self._pool.submit(self._run, url, file_name)

    def _run(self, url, out_file):
        r = requests.get(url)
        with open(os.path.join(self._out_folder, out_file), 'wb') as f:
            f.write(r.content)
            sys.stdout.write('音频下载完成:{}\n'.format(out_file))

    def shutdown(self, wait: bool = True):
        return self._pool.shutdown(wait)
