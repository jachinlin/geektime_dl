# coding=utf8

import sys

from geektime_dl.data_client.gk_apis import GkApiClient
from . import Command, save_cfg


class Login(Command):
    """登录极客时间，保存账号密码至配置文件
    geektime login  [--account=<account>] [--password=<password>] [--area=<area>]

    `[]`表示可选，`<>`表示相应变量值

    area: 注册手机号所属地区，默认86
    account: 手机账号，不提供可稍后手动输入
    password: 账号密码，不提供可稍后手动输入

    e.g.: geektime login
    """
    def run(self, args: dict):

        area = args.get('area')
        account = args.get('account')
        password = args.get('password')
        need_save = not (area and account and password)

        if not account:
            account = input("enter your registered account(phone): ")
        if not area:
            area = input("enter country code: ")
        if not password:
            password = input("account: +{} {}\n"
                             "enter password: ".format(area, account))

        if need_save:
            args.update({'account': account, 'password': password, 'area': area})
            save_cfg(args)

        GkApiClient(account=account, password=password, area=area)
        sys.stdout.write("Login succeed\n")





