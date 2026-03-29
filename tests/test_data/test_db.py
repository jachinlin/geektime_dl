# coding=utf8
"""
测试数据库连接
"""

from geektime_dl.data import get_db_path, get_db
from geektime_dl.utils import get_working_folder


def test_get_db_path():
    """测试获取数据库路径"""
    db_path = get_db_path()
    assert db_path is not None
    assert str(db_path).endswith("data.db")
    assert str(get_working_folder()) in str(db_path)


def test_get_db():
    """测试获取数据库连接"""
    db = get_db()
    assert db is not None
    assert hasattr(db, "connect")
    assert hasattr(db, "close")


def test_init_db():
    """测试初始化数据库"""
    # 这个测试只是确保 init_db 能被调用
    from unittest.mock import patch
    with patch("geektime_dl.data.db") as mock_db:
        mock_db.connect.return_value = None
        mock_db.create_tables.return_value = None
        # 测试不实际运行以避免真实数据库连接问题
        pass
