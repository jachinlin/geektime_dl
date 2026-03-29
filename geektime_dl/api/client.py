# coding=utf8
"""
API 客户端 - 面向对象风格
"""

import time
import functools
import inspect
from typing import Optional, Dict, List, Any

import requests

from geektime_dl.utils import get_random_user_agent
from geektime_dl.log import logger
from .exceptions import (
    GeektimeAPIError,
    AuthenticationError,
    CourseNotFoundError,
    NetworkError,
    ServerError,
    RateLimitError,
    ParseError,
)


def _retry(
    max_retries: int = 10,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_exceptions: tuple = (NetworkError, ServerError, RateLimitError)
):
    """
    可配置的重试装饰器，支持自动重新登录

    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟（秒）
        max_delay: 最大延迟（秒）
        retry_exceptions: 需要重试的异常类型元组

    Returns:
        装饰器函数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if first arg is 'self' (an instance with login method)
            self = args[0] if args and hasattr(args[0], 'login') else None
            
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.warning(f"Request failed after {max_retries} retries: {e}")
                        raise
                    
                    # 第 5 次失败（attempt == 4）时触发 self.login()
                    if attempt == 4 and self:
                        logger.info("Consecutive failures detected, attempting to re-login...")
                        try:
                            self.login()
                        except Exception as login_err:
                            logger.error(f"Re-login failed during retry: {login_err}")
                            # 继续重试
                    
                    delay = min(initial_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries + 1}), "
                                   f"retrying in {delay}s: {e}")
                    time.sleep(delay)
                except GeektimeAPIError:
                    raise
                except Exception as e:
                    raise GeektimeAPIError(f"geektime api error: {e}") from e
            raise last_exception
        return wrapper
    return decorator


class GeektimeClient:
    """极客时间 API 客户端类"""

    def __init__(self, account: str, password: str, area: str = '86'):
        self.account = account
        self.password = password
        self.area = area
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Content-Type': 'application/json',
        })

    def _post(
        self,
        url: str,
        data: dict = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """通用 POST 请求辅助方法"""
        data = data or {}
        headers = headers or {}

        try:
            log_data = data.copy()
            if "password" in log_data:
                log_data["password"] = 'xxx'
            logger.info(f"request geektime api, {url}, {log_data}")
        except Exception:
            pass

        try:
            resp = self._session.post(url, json=data, timeout=10, headers=headers)
            resp.raise_for_status()
        except requests.HTTPError as e:
            if 500 <= resp.status_code < 600:
                raise ServerError(f"Server error: {resp.status_code}", status_code=resp.status_code)
            raise NetworkError(f"HTTP error: {e}") from e
        except requests.RequestException as e:
            raise NetworkError(f"Network error: {e}") from e

        try:
            result = resp.json()
        except ValueError as e:
            raise ParseError(f"Failed to parse JSON response: {e}") from e

        if result.get('code') != 0:
            error_msg = result.get('error', {}).get('msg', 'Unknown error')
            raise GeektimeAPIError(f'geektime api fail: {error_msg}')

        return resp

    def login(self) -> None:
        """
        登录极客时间，返回并更新 cookies

        Raises:
            AuthenticationError: 认证失败
        """
        url = 'https://account.geekbang.org/account/ticket/login'

        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Host': 'account.geekbang.org',
            'Referer': 'https://account.geekbang.org/signin?redirect=https%3A%2F%2Fwww.geekbang.org%2F',
        }

        data = {
            "country": self.area,
            "cellphone": self.account,
            "password": self.password,
            "captcha": "",
            "remember": 1,
            "platform": 3,
            "appid": 1
        }

        try:
            self._post(url, data, headers=headers)
            logger.info(f"Login successful for account {self.account}")
            return
        except GeektimeAPIError as e:
            raise AuthenticationError(f"Login failed: {e.message}") from e

    @_retry()
    def get_course_list(self) -> Dict[str, Any]:
        """获取课程列表"""
        url = 'https://time.geekbang.org/serv/v1/column/all'
        headers = {
            'Referer': 'https://time.geekbang.org/paid-content',
        }

        resp = self._post(url, headers=headers)
        return resp.json()['data']

    @_retry()
    def get_post_list_of(self, course_id: int) -> List[Dict[str, Any]]:
        """获取课程所有章节列表"""
        url = 'https://time.geekbang.org/serv/v1/column/articles'
        data = {
            "cid": str(course_id), "size": 1000, "prev": 0, "order": "newest"
        }
        headers = {
            'Referer': f'https://time.geekbang.org/column/{course_id}',
        }

        resp = self._post(url, data, headers=headers)

        if not resp.json()['data']:
            raise CourseNotFoundError(f'Course not exists: {course_id}')

        return resp.json()['data']['list'][::-1]

    @_retry()
    def get_course_intro(self, course_id: int) -> Dict[str, Any]:
        """获取课程简介"""
        url = 'https://time.geekbang.org/serv/v1/column/intro'
        headers = {
            'Referer': f'https://time.geekbang.org/column/{course_id}',
        }

        resp = self._post(
            url, {'cid': str(course_id)}, headers=headers
        )

        data = resp.json()['data']
        if not data:
            raise CourseNotFoundError(f'无效的课程 ID: {course_id}')
        return data

    @_retry()
    def get_post_content(self, post_id: int) -> Dict[str, Any]:
        """获取课程章节详情"""
        url = 'https://time.geekbang.org/serv/v1/article'
        headers = {
            'Referer': f'https://time.geekbang.org/column/article/{post_id}'
        }

        resp = self._post(
            url, {'id': post_id}, headers=headers
        )

        return resp.json()['data']

    @_retry()
    def get_post_comments(self, post_id: int) -> List[Dict[str, Any]]:
        """获取课程章节评论"""
        url = 'https://time.geekbang.org/serv/v1/comments'
        headers = {
            'Referer': f'https://time.geekbang.org/column/article/{post_id}'
        }

        resp = self._post(
            url, {"aid": str(post_id), "prev": 0},
            headers=headers
        )

        return resp.json()['data']['list'][:5]


# 工厂方法及兼容性包装

def login(account: str, password: str, area: str = '86') -> Dict[str, str]:
    """兼容旧有的 login 调用"""
    client = GeektimeClient(account, password, area)
    return client.login()


def get_course_list(cookies: Dict[str, str]) -> Dict[str, Any]:
    """兼容旧有的 get_course_list 调用"""
    client = GeektimeClient("", "", "")
    client._session.cookies.update(cookies)
    return client.get_course_list()


def get_post_list_of(course_id: int, cookies: Dict[str, str]) -> List[Dict[str, Any]]:
    """兼容旧有的 get_post_list_of 调用"""
    client = GeektimeClient("", "", "")
    client._session.cookies.update(cookies)
    return client.get_post_list_of(course_id)


def get_course_intro(course_id: int, cookies: Dict[str, str]) -> Dict[str, Any]:
    """兼容旧有的 get_course_intro 调用"""
    client = GeektimeClient("", "", "")
    client._session.cookies.update(cookies)
    return client.get_course_intro(course_id)


def get_post_content(post_id: int, cookies: Dict[str, str]) -> Dict[str, Any]:
    """兼容旧有的 get_post_content 调用"""
    client = GeektimeClient("", "", "")
    client._session.cookies.update(cookies)
    return client.get_post_content(post_id)


def get_post_comments(post_id: int, cookies: Dict[str, str]) -> List[Dict[str, Any]]:
    """兼容旧有的 get_post_comments 调用"""
    client = GeektimeClient("", "", "")
    client._session.cookies.update(cookies)
    return client.get_post_comments(post_id)
