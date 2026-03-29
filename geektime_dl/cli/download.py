# coding=utf8
"""
download 命令 - 下载课程到 SQLite
"""

import click
from termcolor import colored

from geektime_dl.utils import parse_column_ids
from geektime_dl.services import CourseService
from geektime_dl.api import AuthenticationError
from .main import cli, common_options


@cli.command()
@common_options
@click.option('--no-cache', is_flag=True, default=False, help='不使用缓存，强制重新下载')
@click.argument('course_ids', type=str)
def download(account, password, area, no_cache, course_ids):
    """
    下载课程到 SQLite
      - 多个: 123,456,789
      - 范围: 1-10
      - 混合: 1-5,10,15-20

    示例:
      geektime download -a myaccount -p mypassword 123
      geektime download -a myaccount -p mypassword 1-10,15
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
        for course_id in ids:
            click.echo(colored(f'开始下载课程: {course_id}', 'green'))

            course = service.download_course(course_id, force_refresh=no_cache)

            if not course:
                click.secho(f'课程 {course_id} 不存在', fg='red', err=True)
                continue

            click.echo(colored(f'下载完成: {course_id} - {course.title}', 'green'))

        click.echo(colored(f'共完成 {len(ids)} 个课程的下载', 'green'))

    except AuthenticationError as e:
        click.secho(f'认证失败: {e}', fg='red', err=True)
        raise click.Abort()
    except Exception as e:
        click.secho(f'错误: {e}', fg='red', err=True)
        raise click.Abort()
