# coding=utf8
"""
login 命令 - 验证账号密码
"""

import click

from geektime_dl.api import GeektimeClient, AuthenticationError
from .main import cli, common_options


@cli.command()
@common_options
def login(account, password, area):
    """
    验证账号密码

    验证极客时间账号密码是否正确，不保存任何配置。

    示例:
      geektime login -a myaccount -p mypassword
      geektime login  # 会提示输入账号密码
    """

    # 如果没有提供参数，提示输入
    if not account:
        account = click.prompt('请输入账号手机号')

    if not password:
        password = click.prompt('请输入密码', hide_input=True)

    if not area:
        area = click.prompt('请输入国家代码', default='86')

    click.echo(f"正在验证账号: +{area} {account}")

    try:
        client = GeektimeClient(account, password, area)
        client.login()
        click.secho('验证成功！', fg='green')
    except AuthenticationError as e:
        click.secho(f'验证失败: {e}', fg='red', err=True)
        raise click.Abort()
