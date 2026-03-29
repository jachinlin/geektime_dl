# coding=utf8
"""
数据模型定义
"""

import datetime
import json

from peewee import (
    Model,
    IntegerField,
    CharField,
    TextField,
    BooleanField,
    DateTimeField,
    ForeignKeyField,
    SQL,
)

from .db import db


class BaseModel(Model):
    """基础模型类"""

    class Meta:
        database = db


class Course(BaseModel):
    """课程表"""

    course_id = IntegerField(unique=True, index=True)
    title = CharField()
    author = CharField()
    intro = TextField()
    cover_url = CharField()
    column_type = IntegerField(default=1)
    update_frequency = CharField(default='')
    is_finished = BooleanField(default=False)
    had_sub = BooleanField(default=False)
    articles_json = TextField(default='[]')

    created_at = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )
    updated_at = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )

    class Meta:
        table_name = 'courses'

    @property
    def articles(self) -> list:
        """获取文章列表（从 JSON 解析）"""
        try:
            return json.loads(self.articles_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @articles.setter
    def articles(self, value: list):
        """设置文章列表（序列化为 JSON）"""
        self.articles_json = json.dumps(value, ensure_ascii=False)

    def save(self, *args, **kwargs):
        """保存时自动更新 updated_at"""
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)


class Article(BaseModel):
    """文章表"""

    article_id = IntegerField(unique=True, index=True)
    course = ForeignKeyField(Course, backref='article_set', on_delete='CASCADE')
    title = CharField()
    cover_url = CharField(default='', null=True)
    content = TextField()
    audio_url = CharField(default='', null=True)
    comments_json = TextField(default='[]')

    created_at = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )
    updated_at = DateTimeField(
        constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')]
    )

    class Meta:
        table_name = 'articles'

    @property
    def comments(self) -> list:
        """获取评论列表（从 JSON 解析）"""
        try:
            return json.loads(self.comments_json)
        except (json.JSONDecodeError, TypeError):
            return []

    @comments.setter
    def comments(self, value: list):
        """设置评论列表（序列化为 JSON）"""
        self.comments_json = json.dumps(value, ensure_ascii=False)

    def save(self, *args, **kwargs):
        """保存时自动更新 updated_at"""
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)
