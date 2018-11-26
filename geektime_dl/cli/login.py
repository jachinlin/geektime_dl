# coding=utf8

from geektime_dl.data_client.gk_apis import *
from . import Command


class Login(Command):
    """登录极客时间，保存登录token
    geektime login  [--account=<account>] [--password=<password>] [--area=<area>]

    `[]`表示可选，`<>`表示相应变量值

    --area: 注册手机号所属地区，默认86
    --account: 手机账号，不提供可稍后手动输入
    --password: 账号密码，不提供可稍后手动输入

    notice: 登录后，token会保存至 cookie.json
    e.g.: geektime login
    """
    def run(self, args):

        for arg in args:
            if '--area=' in arg:
                area = arg.split('--area=')[1] or '86'
                break
        else:
            area = '86'

        for arg in args:
            if '--account=' in arg:
                account = arg.split('--account=')[1] or ''
                break
        else:
            account = None

        for arg in args:
            if '--password=' in arg:
                password = arg.split('--password=')[1] or ''
                break
        else:
            password = None

        if not account:
            account = input("enter your registered account(phone): ")
        if not password:
            password = input("enter password: ")

        gk = GkApiClient()
        gk.login(account, password, area)
        print('登录成功')



