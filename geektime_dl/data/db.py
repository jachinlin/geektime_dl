# coding=utf8
"""
数据库连接管理
"""

from pathlib import Path
from peewee import SqliteDatabase

from geektime_dl.utils import get_working_folder


def get_db_path() -> Path:
    """获取数据库文件路径"""
    return get_working_folder() / 'data.db'


def get_db() -> SqliteDatabase:
    """
    获取数据库连接

    Returns:
        Peewee SqliteDatabase 实例
    """
    db_path = get_db_path()
    return SqliteDatabase(str(db_path))


# 全局数据库实例
db = get_db()


def init_db():
    """
    初始化数据库，创建表

    调用此函数前需要确保已连接数据库
    """
    from .models import Course, Article
    db.connect(reuse_if_open=True)
    db.create_tables([Course, Article], safe=True)
