# coding: utf-8

import math
import requests
from urllib.parse import urljoin
import os


class Downloader:
    def __init__(self):
        pass

    def run(self, m3u8_url, out_dir='.', file_name='outfile'):

        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        r = requests.get(m3u8_url, timeout=10)
        if not r.ok:
            raise Exception('message=requests_failed\turl={}'.format(r.url))
        body = r.content.decode()
        if not body:
            raise Exception('message=invalid_url:{}'.format(r.url))

        ts_list = [urljoin(m3u8_url, n.strip()) for n in body.split('\n') if n and not n.startswith("#")]
        if not ts_list:
            raise Exception('message=invalid_url:{}'.format(r.url))

        with open(os.path.join(out_dir, file_name + '.' + ts_list[0].split('/')[-1].split('?')[0].split('.')[-1]), 'wb') as outfile:

            for i, url in enumerate(ts_list):
                percent = i * 1.0 / len(ts_list) * 100
                print("download {} {:20} {}%".format(file_name, '#' * math.ceil(percent*20/100), math.ceil(percent)))
                r = requests.get(url, timeout=20)

                if r.ok:
                    outfile.write(r.content)
            print("download {} {:20} {}%".format(file_name, '#' * 20, 100))


if __name__ == '__main__':
    downloader = Downloader()
    downloader.run('https://res001.geekbang.org/media/video/17/ae/17af9f0d61ff9df13b26f299082d81ae/sd/sd.m3u8', '.')
