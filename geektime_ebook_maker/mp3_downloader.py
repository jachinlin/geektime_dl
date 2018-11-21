# coding=utf8

import requests
import os


class Downloader(object):
    def __init__(self):
        pass

    def run(self, mp3_url, out_file, out_dir):
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        r = requests.get(mp3_url)
        with open(os.path.join(out_dir, out_file), 'wb') as f:
            f.write(r.content)
