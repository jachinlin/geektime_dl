# coding=utf8

import sys
from ..gk_apis import *
from . import Command

output_dir = None


class Query(Command):
    def run(self, args):
        gk = GkApiClient()
        if not gk.cookies:
            login_now = input("尚未登录，是否现在登录(Y/N): ")
            if login_now.strip().upper() == 'Y':
                area = '86'
                account = input("enter your registered account(phone): ")
                password = input("enter password: ")

                gk.login(account, password, area)
                print('登录成功')

        data = gk.get_course_list()

        result_str = ''
        for i in ['1', '2', '3', '4']:
            columns = data[i]['list']
            result_str += {'1': '专栏', '2': '微课', '3': '视频', '4': '其他'}[i] + '\n'
            # TODO alignment
            result_str += "\t{:<10}{:<30}{:<20}{:<10}\n".format('课程ID', '课程标题', '已订阅', '更新频率')
            for c in columns:
                result_str += "\t{:<10}{:<30}{:<20}{:<10}\n".format(c['id'], c['column_title'], '是' if c['had_sub'] else '否', c['update_frequency'])

        print(result_str)

