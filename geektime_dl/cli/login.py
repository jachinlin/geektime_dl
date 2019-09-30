# coding=utf8

import sys

from geektime_dl.data_client.gk_apis import GkApiClient, GkApiError
from geektime_dl.cli import Command


class Login(Command):
    """登录极客时间，保存账号密码至配置文件"""

    def run(self, args: dict):
        area = args['area']
        account = args['account']
        password = args['password']
        need_save = not (area and account and password)

        if not account:
            account = input("enter your registered account(phone): ")
        if not area:
            area = input("enter country code: enter for 86 ") or '86'
        if not password:
            password = input("account: +{} {}\n"
                             "enter password: ".format(area, account))

        try:
            GkApiClient(account=account, password=password, area=area)
            if need_save:
                new_cfg = {
                    'account': account,
                    'password': password,
                    'area': area
                }
                Command.save_cfg(new_cfg, args['config'])

        except GkApiError as e:
            sys.stdout.write("{}\nEnter again\n".format(e))
            area = input("enter country code: enter for 86 ") or '86'
            account = input("enter your registered account(phone): ")
            password = input("account: +{} {}\n"
                             "enter password: ".format(area, account))

            GkApiClient(account=account, password=password, area=area)

            new_cfg = {
                'account': account,
                'password': password,
                'area': area
            }
            Command.save_cfg(new_cfg, args['config'])

        sys.stdout.write("Login succeed\n")





