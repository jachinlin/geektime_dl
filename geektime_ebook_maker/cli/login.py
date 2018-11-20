# coding=utf8

from ..gk_apis import *
from . import Command

output_dir = None


class Login(Command):
    def run(self, args):
        gk = GkApiClient()
        area = '86'
        account = None
        password = None
        if not account:
            account = input("enter your registered account(phone): ")
        if not password:
            password = input("enter password: ")
        try:
            gk.login(account, password, area)
            print('登录成功')
        except Exception as e:
            print(e.message)
