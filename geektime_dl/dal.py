# coding=utf8

import json
import threading

from tqdm import tqdm

from geektime_dl.gt_apis import GkApiClient
from geektime_dl.utils import synchronized, read_local_cookies
from geektime_dl.cache import GeektimeCache, EmptyCache, SqliteCache


class DataClient:

    def __init__(self, gk: GkApiClient, cache: GeektimeCache):
        self._gt = gk
        self._cache: GeektimeCache = cache
        self._lock = threading.Lock()  # 限制并发

    def get_column_list(self, **kwargs) -> dict:
        """
        获取专栏列表
        """
        use_cache = not kwargs.get("no_cache", False)
        key = "column_all"
        expire = 1 * 24 * 3600  # 1 day
        if use_cache:
            value = self._cache.get(key)
            if value:
                return value
        data = self._gt.get_course_list()
        if use_cache:
            self._cache.set(key, data, expire)

        return data

    @synchronized()
    def get_column_intro(self, column_id: int, **kwargs) -> dict:
        """
        获取专栏简介
        """
        use_cache = not kwargs.get("no_cache", False)
        if use_cache:
            cache = self._cache.get_column_intro(column_id)
            if cache and cache['is_finish'] and cache['had_sub']:
                return cache

        course_intro = self._gt.get_course_intro(column_id)
        course_intro['column_id'] = course_intro['id']
        articles = self._gt.get_post_list_of(column_id)
        course_intro['articles'] = articles

        if use_cache:
            self._cache.save_column_intro(course_intro)

        return course_intro

    @synchronized()
    def get_article_content(self, article_id: int, **kwargs) -> dict:
        """
        获取 article 的所有内容，包括评论
        """
        use_cache = not kwargs.get("no_cache", False)
        if use_cache:
            cache = self._cache.get_article(article_id)
            if cache:
                return cache

        article_info = self._gt.get_post_content(article_id)
        article_info['article_id'] = article_info['id']
        article_info['comments'] = self._get_article_comments(article_id)

        if use_cache:
            self._cache.save_article(article_info)

        return article_info

    def _get_article_comments(self, article_id: int) -> list:
        """
        获取 article 的评论
        """
        data = self._gt.get_post_comments(article_id)
        for c in data:
            c['replies'] = json.dumps(c.get('replies', []))
        return data

    def get_video_collection_list(self, **kwargs) -> list:
        """
        获取每日一课合辑列表
        """
        return self._gt.get_video_collection_list()

    @synchronized()
    def get_video_collection_intro(self, collection_id: int, **kwargs) -> dict:
        """
        获取每日一课合辑简介
        """
        data = self._gt.get_video_collection_intro(collection_id)
        return data

    @synchronized()
    def get_daily_content(self, video_id: int, **kwargs) -> dict:
        """
        获取每日一课内容
        """
        data = self._gt.get_post_content(video_id)
        return data

    def get_video_collection_content(self, collection_id: int,
                                     force: bool = False,
                                     pbar=True, pbar_desc='') -> list:
        """
        获取每日一课合辑ID 为 collection_id 的所有视频内容
        """
        data = []
        v_ids = self._gt.get_video_list_of(collection_id)
        if pbar:
            v_ids = tqdm(v_ids)
            v_ids.set_description(pbar_desc)
        for v_id in v_ids:
            v = self.get_daily_content(v_id['article_id'], force=force)
            data.append(v)
        return data


dc_global = None
_dc_global_lock = threading.Lock()


def get_data_client(cfg: dict) -> DataClient:
    with _dc_global_lock:
        global dc_global
        if dc_global is not None:
            return dc_global

        gk = GkApiClient(
            account=cfg['account'],
            password=cfg['password'],
            area=cfg['area'],
            no_login=cfg['no_login'],
            lazy_login=True,
            cookies=read_local_cookies()
        )

        if cfg.get('no_cache', False):
            cache = EmptyCache()
        else:
            cache = SqliteCache()

        dc = DataClient(gk, cache=cache)
        dc_global = dc

    return dc
