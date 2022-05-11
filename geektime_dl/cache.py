# coding=utf8

import datetime
import json
import traceback
from abc import ABC, abstractmethod

from peewee import (
    SqliteDatabase,
    Model,
    DoesNotExist,
    IntegerField,
    CharField,
    TextField,
    BooleanField,
    DateTimeField
)

from geektime_dl.utils import get_working_folder
from geektime_dl.log import logger


db_file = get_working_folder() / 'gt.sqlite'
db = SqliteDatabase(str(db_file))


class BaseModel(Model):
    class Meta:
        database = db


class ColumnIntro(BaseModel):
    id = IntegerField(primary_key=True)
    column_id = IntegerField(unique=True)
    column_title = CharField()
    author_name = CharField()
    column_intro = TextField()
    column_cover = CharField()
    column_type = IntegerField()
    update_frequency = CharField()
    is_finish = BooleanField()
    had_sub = BooleanField()
    articles = TextField()

    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        return super(ColumnIntro, self).save(*args, **kwargs)


class Article(BaseModel):
    id = IntegerField(primary_key=True)
    article_id = IntegerField(unique=True)
    article_title = CharField()
    article_cover = CharField()
    article_content = TextField()
    audio_download_url = CharField()
    comments = TextField()

    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        return super(Article, self).save(*args, **kwargs)


class TempKV(BaseModel):
    id = IntegerField(primary_key=True)
    key = CharField(unique=True)
    value = TextField()
    expire = IntegerField()  # seconds

    created = DateTimeField(default=datetime.datetime.now)
    modified = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        return super(TempKV, self).save(*args, **kwargs)

    def is_expired(self) -> bool:
        if self.expire <= 0:
            return False
        now = datetime.datetime.now()
        return (now - self.modified).seconds > self.expire


def init_cache():
    db.connect()
    db.create_tables([ColumnIntro, Article, TempKV], safe=True)


init_cache()


class GeektimeCache(ABC):

    @abstractmethod
    def get_column_intro(self, column_id: int) -> dict:
        """"""

    @abstractmethod
    def save_column_intro(self, course_intro: dict) -> None:
        """"""

    @abstractmethod
    def get_article(self, article_id: int) -> dict:
        """"""

    @abstractmethod
    def save_article(self, article_info: dict) -> None:
        """"""

    @abstractmethod
    def get(self, key: str) -> dict:
        """"""

    @abstractmethod
    def set(self, key: str, value: dict, expire: int) -> None:
        """"""


class EmptyCache(GeektimeCache):

    def get_column_intro(self, column_id: int) -> dict:
        return {}

    def save_column_intro(self, course_intro: dict) -> None:
        return

    def get_article(self, article_id: int) -> dict:
        return {}

    def save_article(self, article_info: dict) -> None:
        return

    def get(self, key: str) -> dict:
        return {}

    def set(self, key: str, value: dict, expire: int) -> None:
        pass


class SqliteCache(GeektimeCache):

    def get_column_intro(self, column_id: int) -> dict:
        try:
            column = ColumnIntro.get(
                ColumnIntro.column_id == column_id
            )

            cache = {
                "id": column.column_id,
                "column_id": column.column_id,
                "column_title": column.column_title,
                "author_name": column.author_name,
                "column_intro": column.column_intro,
                "column_cover": column.column_cover,
                "column_type": column.column_type,
                "update_frequency": column.update_frequency,
                "is_finish": column.is_finish,
                "had_sub": column.had_sub,
                "articles": json.loads(column.articles)
            }
            logger.info("get column intro from cache, column_title={}".format(
                cache['column_title']
            ))
            return cache
        except DoesNotExist:
            return {}
        except Exception:
            logger.error('ERROR: {}'.format(traceback.format_exc()))
            return {}

    def save_column_intro(self, course_intro: dict) -> None:
        try:
            try:
                column = ColumnIntro.get(
                    ColumnIntro.column_id == course_intro['id']
                )
            except DoesNotExist:
                column = ColumnIntro()
            column.column_id = course_intro['id']
            column.column_title = course_intro['column_title']
            column.author_name = course_intro['author_name']
            column.column_intro = course_intro['column_intro']
            column.column_cover = course_intro['column_cover']
            column.column_type = course_intro['column_type']
            column.update_frequency = course_intro['update_frequency']
            column.is_finish = course_intro['is_finish']
            column.had_sub = course_intro['had_sub']
            column.articles = json.dumps(course_intro['articles'])
            column.save()
            logger.info("save column intro to cache, column_title={}".format(
                course_intro['column_title']
            ))
        except Exception:
            logger.error('ERROR: {}'.format(traceback.format_exc()))

    def get_article(self, article_id: int) -> dict:
        try:
            article = Article.get(
                Article.article_id == article_id
            )

            cache = {
                "id": article.article_id,
                "article_id": article.article_id,
                "article_title": article.article_title,
                "article_cover": article.article_cover,
                "article_content": article.article_content,
                "audio_download_url": article.audio_download_url,
                "comments": json.loads(article.comments)
            }
            logger.info("get article from cache, article_title={}".format(
                cache['article_title']
            ))
            return cache
        except DoesNotExist:
            return {}
        except Exception:
            logger.error('ERROR: {}'.format(traceback.format_exc()))
            return {}

    def save_article(self, article_info: dict) -> None:
        try:
            try:
                article = Article.get(
                    Article.article_id == article_info['article_id']
                )
            except DoesNotExist:
                article = Article()
            article.article_id = article_info['article_id']
            article.article_title = article_info['article_title']
            article.article_cover = article_info['article_cover']
            article.article_content = article_info['article_content']
            article.audio_download_url = article_info['audio_download_url']
            article.comments = json.dumps(article_info['comments'])
            article.save()
            logger.info("save article to cache, article_title={}".format(
                article_info['article_title']
            ))
        except Exception:
            logger.error('ERROR: {}'.format(traceback.format_exc()))

    def get(self, key: str) -> dict:
        try:
            try:
                kv: TempKV = TempKV.get(TempKV.key == key)
            except DoesNotExist:
                return {}

            if kv.is_expired():
                logger.info("get kv expired, key={}".format(key))
                return {}
            val_dict = json.loads(str(kv.value))
            logger.info("get kv, key={}, value= {}".format(
                key, kv.value[:100]
            ))
            return val_dict
        except Exception:
            logger.error('ERROR: {}'.format(traceback.format_exc()))
            return {}

    def set(self, key: str, value: dict, expire: int) -> None:
        try:
            try:
                kv: TempKV = TempKV.get(TempKV.key == key)
            except DoesNotExist:
                kv = TempKV()

            val_str = json.dumps(value)
            kv.key = key
            kv.value = val_str
            kv.expire = expire
            kv.save()
            logger.info("set kv, key={}, value= {}, expire={}".format(
                key, val_str[:100], expire
            ))
        except Exception:
            logger.error('ERROR: {}'.format(traceback.format_exc()))
