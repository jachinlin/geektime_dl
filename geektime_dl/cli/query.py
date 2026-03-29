# coding=utf8
"""
query 命令 - 查询课程列表
"""

import click

from geektime_dl.services import CourseService
from geektime_dl.api import AuthenticationError
from .main import cli, common_options


_COLUMN_INDEX = "1"


@cli.command()
@common_options
def query(account, password, area):
    """
    查询课程列表

    显示用户已订阅的课程列表。

    示例:
      geektime query -a myaccount -p mypassword
    """

    # 验证必需参数
    if not account or not password:
        click.secho('错误: 需要提供账号和密码', fg='red', err=True)
        click.echo('使用 -a/--account 和 -p/--password 参数')
        raise click.Abort()

    try:
        service = CourseService(account, password, area)
        service.login() 

        click.echo('正在获取课程列表...')
        data = service.get_course_list()

        if _COLUMN_INDEX not in data:
            click.echo('未找到课程数据')
            return

        columns = data[_COLUMN_INDEX]['list']

        result = '专栏\n'
        result += "\t{:<12}{}\t{}\t{}\n".format(
            '课程ID', '已订阅', '已完结', '课程标题')

        for c in columns:
            is_finished = c.get('update_frequency') in ['全集', '已完结'] or c.get('is_finish')
            result += "\t{:<15}{}\t{}\t{}\n".format(
                str(c['id']),
                '是' if c.get('had_sub') else '否',
                '是' if is_finished else '否',
                c.get('column_title', ''),
            )

        click.echo(result)

    except AuthenticationError as e:
        click.secho(f'认证失败: {e}', fg='red', err=True)
        raise click.Abort()
    except Exception as e:
        click.secho(f'错误: {e}', fg='red', err=True)
        raise click.Abort()
