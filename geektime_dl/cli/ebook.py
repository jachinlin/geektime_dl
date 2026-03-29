# coding=utf8
"""
ebook 命令 - 制作课程电子书
"""

import os
import pathlib
import datetime
import json

from termcolor import colored
from tqdm import tqdm
import click

from geektime_dl.utils import parse_column_ids
from geektime_dl.ebook import build_epub, format_file_name
from geektime_dl.services import CourseService
from geektime_dl.api import AuthenticationError
from geektime_dl.data import Article
from .main import cli, common_options


def is_course_finished(course_info: dict) -> bool:
    """判断课程是否已完结"""
    return course_info.get('update_frequency') in ['全集', '已完结'] or \
        course_info.get('is_finish')


def format_title(course_info: dict) -> str:
    """格式化课程文件名"""
    t = format_file_name(course_info['column_title'])
    if not course_info.get('had_sub'):
        t += '[免费试读]'
    elif is_course_finished(course_info):
        pass
    else:
        t += '[未完待续{}]'.format(datetime.date.today())
    return t


def make_output_folder(output_folder: str):
    """创建输出目录"""
    output_folder = os.path.expanduser(output_folder)
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    return output_folder


@cli.command()
@common_options
@click.option('--no-cache', is_flag=True, help='不使用缓存，强制重新生成')
@click.option('-o', '--output-folder', default='.', help='输出目录')
@click.argument('course_ids', type=str)
def ebook(account, password, area, no_cache, output_folder, course_ids):
    """
    制作课程电子书

    将指定课程下载并制作成 EPUB 电子书。

    COURSE_IDS 支持格式:
      - 单个: 123
      - 多个: 123,456,789
      - 范围: 1-10
      - 混合: 1-5,10,15-20

    示例:
      geektime ebook -a 13800138000 -p mypassword 123
    """

    # 验证必需参数
    if not account or not password:
        click.secho('错误: 需要提供账号和密码', fg='red', err=True)
        click.echo('使用 -a/--account 和 -p/--password 参数')
        raise click.Abort()

    # 解析课程 ID
    try:
        ids = parse_column_ids(course_ids)
    except ValueError as e:
        click.secho(f'错误: {e}', fg='red', err=True)
        raise click.Abort()

    if not ids:
        click.secho('错误: 请提供有效的课程 ID', fg='red', err=True)
        raise click.Abort()

    try:
        service = CourseService(account, password, area)
        service.login() 
        output_folder = make_output_folder(output_folder)

        for course_id in ids:
            _run_once(
                service, course_id, output_folder, no_cache
            )

    except AuthenticationError as e:
        click.secho(f'认证失败: {e}', fg='red', err=True)
        raise click.Abort()
    except Exception as e:
        click.secho(f'错误: {e}', fg='red', err=True)
        raise click.Abort()


def _run_once(service, course_id, output_folder, no_cache):
    """处理单个课程"""

    # 获取课程信息
    course = service.download_course(course_id, force_refresh=no_cache)

    if not course:
        click.secho(f'课程 {course_id} 不存在', fg='red', err=True)
        return

    # 构建 course_intro 格式
    course_intro = {
        'id': course.course_id,
        'column_id': course.course_id,
        'column_title': course.title,
        'author_name': course.author,
        'column_intro': course.intro,
        'column_cover': course.cover_url,
        'column_type': course.column_type,
        'update_frequency': course.update_frequency,
        'is_finish': course.is_finished,
        'had_sub': course.had_sub,
    }

    if int(course.column_type) not in (1, 2):
        click.secho(f"错误: 该课程不提供文本: {course.title}", fg='red', err=True)
        return

    click.echo(colored('开始制作电子书:{}-{}'.format(
        course_id, course.title), 'green'))

    # 获取文章数据
    article_ids = course.articles
    articles = []

    for a in tqdm(article_ids, desc='读取文章数据'):
        article = Article.get_or_none(Article.article_id == a['id'])
        if not article:
            continue
        article_data = {
            'article_id': article.article_id,
            'article_title': article.title,
            'article_content': article.content,
        }
        article_data['article_content'] += _render_comments(article.comments)
        articles.append(article_data)

    # 生成电子书
    ebook_name = '{}.epub'.format(format_title(course_intro))
    fp = pathlib.Path(output_folder) / ebook_name

    if (not no_cache and is_course_finished(course_intro) and fp.exists()):
        click.echo(colored("{} exists\n".format(ebook_name), 'green'))
    else:
        build_epub(
            course_intro=course_intro,
            articles=articles,
            output_path=str(fp)
        )
        click.echo(colored('制作电子书完成:{}-{}'.format(
            course_id, course.title), 'green'))


def _timestamp2str(timestamp: int) -> str:
    """时间戳转字符串"""
    if not timestamp:
        return ''
    return datetime.datetime.fromtimestamp(
        int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")


def _render_comment(comment: dict) -> str:
    """渲染单条评论"""
    try:
        replies = json.loads(comment.get('replies', '[]'))
    except (json.JSONDecodeError, TypeError):
        replies = []

    reply = replies[0] if replies else {}
    replies_html = """<br/>
<div>
    <div style="color:#888;font-size:15.25px;font-weight:400;\
        line-height:1.2">{}{}</div>
    <div style="color:#353535;font-weight:400;white-space:normal;\
        word-break:break-all;line-height:1.6">{}</div>
</div>
            """.format(
        reply.get('user_name', ''),
        _timestamp2str(reply.get('ctime', 0)),
        reply.get('content', '')
    ) if reply else ''

    likes = "[{}赞]".format(comment['like_count']) if comment.get('like_count') else ''
    c_html = """
<li>
    <div>
        <div style="color: #888;font-size:15.25px;font-weight:400;\
            line-height:1.2">
            {user_name}  {comment_time}
        </div>
        <div style="color:#353535;font-weight:400;white-space:normal;\
            word-break:break-all;line-height:1.6">
            {comment_content} {like_count}
        </div>
        {replies}
    </div>
</li>
            """.format(
        user_name=comment.get('user_name', ''),
        like_count=likes,
        comment_content=comment.get('comment_content', ''),
        comment_time=_timestamp2str(comment.get('comment_ctime', 0)),
        replies=replies_html
    )
    return c_html


def _render_comments(comments, comment_count: int = 5) -> str:
    """生成评论的 HTML 文本"""
    if not comments:
        return ''

    count = min(len(comments), int(comment_count))
    comments = comments[:count]

    html = '\n<br/>\n'.join([
        _render_comment(c)
        for c in comments
    ])
    h = """<h2>精选留言：</h2>
        <ul>
        """
    f = '</ul>'
    return h + html + f
