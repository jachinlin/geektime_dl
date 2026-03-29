# coding=utf8
"""
Pytest 配置文件
"""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_output_folder():
    """临时输出目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_working_folder(monkeypatch):
    """临时工作目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        monkeypatch.setattr("geektime_dl.utils._working_folder", tmp_path)
        yield tmp_path


@pytest.fixture
def mock_api_client():
    """Mock API 客户端"""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.login.return_value = {"session_id": "test123"}
    mock.get_course_list.return_value = {
        "1": {"list": [
            {"id": 1, "column_title": "测试课程", "had_sub": True, "is_finish": True}
        ]}
    }
    mock.get_course_intro.return_value = {
        "id": 1,
        "column_title": "测试课程",
        "author_name": "测试作者",
        "column_intro": "课程简介",
        "column_cover": "https://example.com/cover.jpg",
        "column_type": 1,
        "update_frequency": "已完结",
        "is_finish": True,
        "had_sub": True,
    }
    mock.get_post_list_of.return_value = [
        {"id": 101, "article_title": "文章1"},
        {"id": 102, "article_title": "文章2"},
    ]
    mock.get_post_content.return_value = {
        "id": 101,
        "article_title": "文章1",
        "article_content": "文章内容",
        "audio_download_url": "https://example.com/audio.mp3",
    }
    mock.get_post_comments.return_value = []

    return mock


@pytest.fixture
def output_folder(temp_output_folder) -> str:
    return str(temp_output_folder)


