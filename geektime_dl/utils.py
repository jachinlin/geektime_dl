# coding=utf8
import random
import pathlib
from typing import List


_working_folder = pathlib.Path.home() / '.geektime_dl'
_working_folder.mkdir(exist_ok=True)


def get_working_folder():
    return _working_folder


def parse_column_ids(ids_str: str) -> List[int]:
    def _int(num):
        try:
            return int(num)
        except Exception:
            raise ValueError('illegal column ids: {}'.format(ids_str))
    res = list()
    segments = ids_str.split(',')
    for seg in segments:
        if '-' in seg:
            s, e = seg.split('-', 1)
            res.extend(range(_int(s), _int(e) + 1))
        else:
            res.append(_int(seg))
    res = list(set(res))
    res.sort()
    return res


_ua_list = [
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36",  # noqa: E501
]


def get_random_user_agent() -> str:
    return random.choice(_ua_list)
