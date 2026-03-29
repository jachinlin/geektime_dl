# coding=utf8
"""
API 层异常定义
"""


class GeektimeAPIError(Exception):
    """API 调用错误基类"""

    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(GeektimeAPIError):
    """认证失败 - 账号或密码错误"""
    pass


class CourseNotFoundError(GeektimeAPIError):
    """课程不存在"""
    pass


class ArticleNotFoundError(GeektimeAPIError):
    """文章不存在"""
    pass


class NetworkError(GeektimeAPIError):
    """网络错误 - 连接超时、DNS 解析失败等"""
    pass


class RateLimitError(GeektimeAPIError):
    """请求频率限制"""
    pass


class ServerError(GeektimeAPIError):
    """服务器错误 - 5xx 状态码"""
    pass


class ParseError(GeektimeAPIError):
    """响应解析错误 - JSON 解析失败等"""
    pass
