# coding=utf8
"""
课程服务 - 业务逻辑层
"""

from typing import Optional, Dict, Any
from tqdm import tqdm

from geektime_dl.api import (
    GeektimeClient,
    CourseNotFoundError,
)
from geektime_dl.data import Course, Article, init_db


class CourseService:
    """课程服务，协调 API 和数据层"""

    def __init__(self, account: str, password: str, area: str = '86'):
        self.account = account
        self.password = password
        self.area = area
        self.client = GeektimeClient(account, password, area)

        # 初始化数据库
        init_db()

    def login(self) -> Dict[str, str]:
        """
        登录并返回 cookies

        Returns:
            cookies 字典

        Raises:
            AuthenticationError: 认证失败
        """
        return self.client.login()

    def get_course_list(self) -> Dict[str, Any]:
        """
        获取课程列表，总是从 API 获取

        Returns:
            课程列表字典
        """
        return self.client.get_course_list()

    def get_course(self, course_id: int, force_refresh: bool = False) -> Optional[Course]:
        """
        获取课程，支持缓存

        Args:
            course_id: 课程 ID
            force_refresh: 是否强制刷新

        Returns:
            Course 对象，如果课程不存在返回 None
        """
        # 先查缓存
        if not force_refresh:
            course = Course.get_or_none(Course.course_id == course_id)
            if course:
                return course

        # 从 API 获取
        try:
            data = self.client.get_course_intro(course_id)
            articles = self.client.get_post_list_of(course_id)
            data['articles'] = articles
            return self._save_course(data)
        except CourseNotFoundError:
            return None

    def download_course(self, course_id: int, force_refresh: bool = False) -> Optional[Course]:
        """
        下载完整课程（包括所有文章）

        Args:
            course_id: 课程 ID
            force_refresh: 是否强制刷新（即使已缓存）

        Returns:
            Course 对象，如果课程不存在返回 None
        """
        # 获取课程基本信息
        course = self.get_course(course_id, force_refresh=force_refresh)
        if not course:
            return None

        # 下载每篇文章
        pbar = tqdm(course.articles)
        pbar.set_description(f"下载文章: {course.title[:15]}")

        for article_info in pbar:
            self._download_article(article_info, course, force_refresh=force_refresh)

        return course

    def _save_course(self, data: Dict[str, Any]) -> Course:
        """保存课程数据到数据库"""
        course_id = data['id']

        # 查找或创建课程
        course, created = Course.get_or_create(
            course_id=course_id,
            defaults={
                'title': data['column_title'],
                'author': data['author_name'],
                'intro': data['column_intro'],
                'cover_url': data['column_cover'],
                'column_type': data.get('column_type', 1),
                'update_frequency': data.get('update_frequency', ''),
                'is_finished': data.get('is_finish', False) or data.get('update_frequency') in ['全集', '已完结'],
                'had_sub': data.get('had_sub', False),
                'articles': data.get('articles', []),
            }
        )

        # 如果已存在，更新信息
        if not created:
            course.title = data['column_title']
            course.author = data['author_name']
            course.intro = data['column_intro']
            course.cover_url = data['column_cover']
            course.column_type = data.get('column_type', 1)
            course.update_frequency = data.get('update_frequency', '')
            course.is_finished = data.get('is_finish', False) or data.get('update_frequency') in ['全集', '已完结']
            course.had_sub = data.get('had_sub', False)
            course.articles = data.get('articles', [])
            course.save()

        return course

    def _download_article(self, article_info: Dict[str, Any], course: Course, force_refresh: bool = False) -> Article:
        """下载单篇文章"""
        article_id = article_info['id']

        # 检查是否已存在
        if not force_refresh:
            article = Article.get_or_none(Article.article_id == article_id)
            if article:
                return article

        # 获取完整内容
        full_data = self.client.get_post_content(article_id)

        # 获取评论
        try:
            comments = self.client.get_post_comments(article_id)
        except Exception:
            comments = []

        # 保存文章
        article, created = Article.get_or_create(
            article_id=article_id,
            course=course,
            defaults={
                'title': full_data.get('article_title', article_info.get('article_title', '')),
                'cover_url': full_data.get('article_cover', ''),
                'content': full_data.get('article_content', ''),
                'audio_url': full_data.get('audio_download_url', ''),
                'comments': comments,
            }
        )

        if not created:
            article.title = full_data.get('article_title', article_info.get('article_title', ''))
            article.cover_url = full_data.get('article_cover', '')
            article.content = full_data.get('article_content', '')
            article.audio_url = full_data.get('audio_download_url', '')
            article.comments = comments
            article.save()

        return article
