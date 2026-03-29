# coding=utf8
"""
测试 API 异常类
"""

from geektime_dl.api import (
    GeektimeAPIError,
    AuthenticationError,
    CourseNotFoundError,
    ArticleNotFoundError,
    NetworkError,
    RateLimitError,
    ServerError,
    ParseError,
)


def test_geektime_api_error():
    """测试基础异常类"""
    error = GeektimeAPIError("test error")
    assert str(error) == "test error"
    assert error.message == "test error"


def test_geektime_api_error_with_status_code():
    """测试带状态码的异常"""
    error = GeektimeAPIError("test error", status_code=404)
    assert str(error) == "[404] test error"
    assert error.status_code == 404


def test_geektime_api_error_with_response_data():
    """测试带响应数据的异常"""
    response_data = {"code": -1, "msg": "error"}
    error = GeektimeAPIError("test error", response_data=response_data)
    assert error.response_data == response_data


def test_authentication_error():
    """测试认证错误"""
    error = AuthenticationError("invalid credentials")
    assert isinstance(error, GeektimeAPIError)
    assert str(error) == "invalid credentials"


def test_course_not_found_error():
    """测试课程不存在错误"""
    error = CourseNotFoundError("course not found")
    assert isinstance(error, GeektimeAPIError)
    assert str(error) == "course not found"


def test_article_not_found_error():
    """测试文章不存在错误"""
    error = ArticleNotFoundError("article not found")
    assert isinstance(error, GeektimeAPIError)
    assert str(error) == "article not found"


def test_network_error():
    """测试网络错误"""
    error = NetworkError("connection timeout")
    assert isinstance(error, GeektimeAPIError)
    assert str(error) == "connection timeout"


def test_rate_limit_error():
    """测试频率限制错误"""
    error = RateLimitError("too many requests")
    assert isinstance(error, GeektimeAPIError)
    assert str(error) == "too many requests"


def test_server_error():
    """测试服务器错误"""
    error = ServerError("internal server error", status_code=500)
    assert isinstance(error, GeektimeAPIError)
    assert str(error) == "[500] internal server error"


def test_parse_error():
    """测试解析错误"""
    error = ParseError("invalid json")
    assert isinstance(error, GeektimeAPIError)
    assert str(error) == "invalid json"


def test_exception_hierarchy():
    """测试异常继承关系"""
    assert issubclass(AuthenticationError, GeektimeAPIError)
    assert issubclass(CourseNotFoundError, GeektimeAPIError)
    assert issubclass(ArticleNotFoundError, GeektimeAPIError)
    assert issubclass(NetworkError, GeektimeAPIError)
    assert issubclass(RateLimitError, GeektimeAPIError)
    assert issubclass(ServerError, GeektimeAPIError)
    assert issubclass(ParseError, GeektimeAPIError)
