# coding=utf8
"""Test API client retry decorator"""

from unittest.mock import Mock, patch
import pytest

from geektime_dl.api.client import _retry
from geektime_dl.api.exceptions import (
    NetworkError,
    ServerError,
    RateLimitError,
    GeektimeAPIError,
    AuthenticationError,
)


def test_retry_success_on_first_attempt():
    """测试首次调用成功"""
    mock_func = Mock(return_value="success")

    @_retry()
    def test_func():
        return mock_func()

    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 1


def test_retry_network_error_eventually_succeeds():
    """测试网络错误后重试成功"""
    mock_func = Mock(side_effect=[NetworkError("fail"), "success"])

    @_retry()
    def test_func():
        return mock_func()

    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 2


def test_retry_server_error_eventually_succeeds():
    """测试服务器错误后重试成功"""
    mock_func = Mock(side_effect=[ServerError("500"), "success"])

    @_retry()
    def test_func():
        return mock_func()

    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 2


def test_retry_rate_limit_error_eventually_succeeds():
    """测试频率限制错误后重试成功"""
    mock_func = Mock(side_effect=[RateLimitError("429"), "success"])

    @_retry()
    def test_func():
        return mock_func()

    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 2


def test_retry_max_retries_exceeded():
    """测试超过最大重试次数"""
    mock_func = Mock(side_effect=NetworkError("always fail"))

    @_retry(max_retries=3)
    def test_func():
        return mock_func()

    with pytest.raises(NetworkError):
        test_func()
    assert mock_func.call_count == 4  # 1 次初始 + 3 次重试


def test_no_retry_for_non_retryable_exception():
    """测试不重试非重试异常"""
    mock_func = Mock(side_effect=AuthenticationError("invalid creds"))

    @_retry()
    def test_func():
        return mock_func()

    with pytest.raises(AuthenticationError):
        test_func()
    assert mock_func.call_count == 1


def test_exponential_backoff_timing():
    """测试指数退避时间"""
    delays = []

    def mock_sleep(seconds):
        delays.append(seconds)

    mock_func = Mock(side_effect=[NetworkError("1"), NetworkError("2"), NetworkError("3"), "success"])

    @_retry(max_retries=3, initial_delay=1.0, max_delay=4.0)
    def test_func():
        return mock_func()

    with patch('time.sleep', side_effect=mock_sleep):
        result = test_func()

    assert result == "success"
    assert mock_func.call_count == 4
    assert delays == [1.0, 2.0, 4.0]


def test_custom_retry_exceptions():
    """测试自定义重试异常"""
    mock_func = Mock(side_effect=[GeektimeAPIError("custom"), "success"])

    @_retry(retry_exceptions=(GeektimeAPIError,))
    def test_func():
        return mock_func()

    result = test_func()
    assert result == "success"
    assert mock_func.call_count == 2
