# coding=utf8
"""
Geektime CLI 主入口 - 基于 Click
"""

import sys
import traceback

import click

from geektime_dl.log import logger


def common_options(f):
    """公共选项装饰器"""
    options = [
        click.option('-a', '--account', envvar='GEEKTIME_ACCOUNT', help='账号手机号'),
        click.option('-p', '--password', envvar='GEEKTIME_PASSWORD', help='密码'),
        click.option('--area', envvar='GEEKTIME_AREA', default='86', help='国家代码'),
    ]
    for option in reversed(options):
        f = option(f)
    return f


@click.group()
def cli():
    """
    极客时间下载工具 - 把极客时间装进 Kindle

    使用 'geektime COMMAND --help' 查看各命令的详细帮助。
    """
    pass


def main():
    """主入口函数"""
    try:
        cli(auto_envvar_prefix='GEEKTIME')
    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        logger.error('ERROR: {}'.format(traceback.format_exc()))
        sys.exit(1)


# 导入子命令
from . import login  # noqa: F401,E402
from . import query  # noqa: F401,E402
from . import download  # noqa: F401,E402
from . import ebook  # noqa: F401,E402
