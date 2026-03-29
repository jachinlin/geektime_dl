# coding=utf8
"""
测试数据模型
"""

import pytest
import json
import tempfile
import os
from peewee import SqliteDatabase

from geektime_dl.data import Course, Article


@pytest.fixture
def test_db():
    """创建临时测试数据库"""
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()

    test_db = SqliteDatabase(temp_db.name)
    test_db.bind([Course, Article])
    test_db.connect()
    test_db.create_tables([Course, Article])

    yield test_db

    test_db.drop_tables([Course, Article])
    test_db.close()
    os.unlink(temp_db.name)


def test_course_create(test_db):
    """测试创建课程"""
    course = Course.create(
        course_id=123,
        title="测试课程",
        author="测试作者",
        intro="课程简介",
        cover_url="https://example.com/cover.jpg",
        column_type=1,
        update_frequency="已完结",
        is_finished=True,
        had_sub=True,
        articles_json='[{"id": 1}, {"id": 2}]'
    )

    assert course.course_id == 123
    assert course.title == "测试课程"
    assert course.author == "测试作者"


def test_course_articles_property(test_db):
    """测试课程 articles 属性"""
    course = Course.create(
        course_id=123,
        title="测试课程",
        author="测试作者",
        intro="课程简介",
        cover_url="https://example.com/cover.jpg",
        articles_json='[{"id": 1, "title": "文章1"}, {"id": 2, "title": "文章2"}]'
    )

    articles = course.articles
    assert len(articles) == 2
    assert articles[0]["id"] == 1
    assert articles[1]["id"] == 2


def test_course_articles_setter(test_db):
    """测试设置课程 articles"""
    course = Course.create(
        course_id=123,
        title="测试课程",
        author="测试作者",
        intro="课程简介",
        cover_url="https://example.com/cover.jpg",
    )

    new_articles = [{"id": 100}, {"id": 200}]
    course.articles = new_articles
    course.save()

    assert json.loads(course.articles_json) == new_articles


def test_course_articles_invalid_json(test_db):
    """测试无效的 JSON 处理"""
    course = Course.create(
        course_id=123,
        title="测试课程",
        author="测试作者",
        intro="课程简介",
        cover_url="https://example.com/cover.jpg",
        articles_json='invalid json'
    )

    articles = course.articles
    assert articles == []


def test_article_create(test_db):
    """测试创建文章"""
    course = Course.create(
        course_id=123,
        title="测试课程",
        author="测试作者",
        intro="课程简介",
        cover_url="https://example.com/cover.jpg",
    )

    article = Article.create(
        article_id=456,
        course=course,
        title="测试文章",
        content="文章内容",
        audio_url="https://example.com/audio.mp3",
        comments_json='[{"id": 1, "content": "评论1"}]'
    )

    assert article.article_id == 456
    assert article.title == "测试文章"
    assert article.course == course


def test_article_comments_property(test_db):
    """测试文章 comments 属性"""
    course = Course.create(
        course_id=123,
        title="测试课程",
        author="测试作者",
        intro="课程简介",
        cover_url="https://example.com/cover.jpg",
    )

    article = Article.create(
        article_id=456,
        course=course,
        title="测试文章",
        content="文章内容",
        comments_json='[{"id": 1, "content": "评论1"}, {"id": 2, "content": "评论2"}]'
    )

    comments = article.comments
    assert len(comments) == 2
    assert comments[0]["id"] == 1


def test_article_comments_setter(test_db):
    """测试设置文章 comments"""
    course = Course.create(
        course_id=123,
        title="测试课程",
        author="测试作者",
        intro="课程简介",
        cover_url="https://example.com/cover.jpg",
    )

    article = Article.create(
        article_id=456,
        course=course,
        title="测试文章",
        content="文章内容",
    )

    new_comments = [{"id": 100, "content": "新评论"}]
    article.comments = new_comments
    article.save()

    assert json.loads(article.comments_json) == new_comments


def test_course_get_or_none(test_db):
    """测试获取不存在的课程"""
    course = Course.get_or_none(Course.course_id == 999)
    assert course is None


def test_article_get_or_none(test_db):
    """测试获取不存在的文章"""
    article = Article.get_or_none(Article.article_id == 999)
    assert article is None
