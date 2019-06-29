# coding=utf8

import os
import json
import time
import datetime
import requests
import traceback

from multiprocessing import Pool

from geektime_dl.data_client import DataClient
from . import Command
from ..utils.m3u8_downloader import Downloader
from ..utils import format_path
from ..geektime_ebook import maker

from aliyunsdkcore.vendored.six import iteritems
from aliyunsdkcore.vendored.six.moves.urllib.parse import urlencode
from aliyunsdkcore.vendored.six.moves.urllib.request import pathname2url
from aliyunsdkcore.auth.algorithm import sha_hmac1 as mac1
from aliyunsdkcore.utils import parameter_helper as helper

from configparser import ConfigParser

def __refresh_sign_parameters(
        parameters,
        access_key_id,
        accept_format="JSON",
        signer=mac1):
    if parameters is None or not isinstance(parameters, dict):
        parameters = dict()
    if 'Signature' in parameters:
        del parameters['Signature']
    parameters["Timestamp"] = helper.get_iso_8061_date()
    parameters["SignatureMethod"] = signer.get_signer_name()
    parameters["SignatureType"] = signer.get_signer_type()
    parameters["SignatureVersion"] = signer.get_signer_version()
    parameters["SignatureNonce"] = helper.get_uuid()
    parameters["AccessKeyId"] = access_key_id
    if accept_format is not None:
        parameters["Format"] = accept_format
    return parameters


def __pop_standard_urlencode(query):
    ret = query.replace('+', '%20')
    ret = ret.replace('*', '%2A')
    ret = ret.replace('%7E', '~')
    return ret


def __compose_string_to_sign(method, queries):
    sorted_parameters = sorted(iteritems(queries), key=lambda queries: queries[0])
    sorted_query_string = __pop_standard_urlencode(urlencode(sorted_parameters))
    canonicalized_query_string = __pop_standard_urlencode(pathname2url(sorted_query_string))
    string_to_sign = method + "&%2F&" + canonicalized_query_string
    return string_to_sign

def __get_signature(string_to_sign, secret, signer=mac1):
    return signer.get_sign_string(string_to_sign, secret + '&')

def get_signed_url(params, ak, secret, accept_format, method, body_params, signer=mac1):
    url_params = __refresh_sign_parameters(params, ak, accept_format, signer)
    sign_params = dict(url_params)
    sign_params.update(body_params)
    string_to_sign = __compose_string_to_sign(method, sign_params)
    signature = __get_signature(string_to_sign, secret, signer)
    url_params['Signature'] = signature
    url = '/?' + __pop_standard_urlencode(urlencode(url_params))
    return url, string_to_sign

class Mp4(Command):

    """保存视频课程视频
    geektime mp4 <course_id>
    course_id: 课程ID，可以从 query subcmd 查看
    """
    def __init__(self):
        cfg = ConfigParser()
        cfg.read('config.ini')
        self.mp4_out_dir = cfg.get('output','mp4_out_dir')

    def run(self, args):

        course_id = args[0]
        out_dir = self.mp4_out_dir
        workers = 1

        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        dc = DataClient()

        course_data = dc.get_course_intro(course_id)

        if int(course_data['column_type']) != 3:
            raise Exception('该课程不是视频课程:%s' % course_data['column_title'])

        out_dir = os.path.join(out_dir, maker.format_file_name(course_data['column_title']))
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        data = dc.get_course_content(course_id)
        for post in data: 
            try:
                play_auth = dc.get_video_play_auth(post)
                time.sleep(1)
                print("course_id:", course_id, "id:", post['id'], "video_id:", post['video_id'],"play_auth VideoId:", play_auth.get('VideoMeta').get('VideoId'), "sku", post['sku'])

                url, string_to_sign = get_signed_url({
                    'Action': 'GetPlayInfo',
                    'AuthInfo': play_auth.get('AuthInfo'),
                    'AuthTimeout': 7200,
                    'Channel': 'HTML5',
                    'Format': 'JSON',
                    'Formats': '',
                    'PlayConfig': {},
                    'PlayerVersion': '2.8.2',
                    #'Rand': '',
                    'ReAuthInfo': {},
                    'SecurityToken': play_auth.get('SecurityToken'),
                    'Version':'2017-03-21',
                    'VideoId': play_auth.get('VideoMeta').get('VideoId'),
                    'StreamType': 'video'
                }, play_auth.get('AccessKeyId'), play_auth.get('AccessKeySecret'), 'JSON', 'GET', {}, signer=mac1)
       
                headers = {
                    'Referer': 'https://time.geekbang.org/course/detail/190-{}'.format(str(post['id'])),
                    'Origin': 'https://time.geekbang.org',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
                }
                url = 'https://vod.cn-beijing.aliyuncs.com' + url
                resp = requests.get(url, headers=headers, timeout=10)
                PlayInfo = resp.json().get('PlayInfoList').get('PlayInfo')
                for play_info in PlayInfo:
                    if play_info.get('Specification') != "H264.SD":
                        continue
                    dl = Downloader()
                    p = Pool(workers)
                    start = time.time()
                    file_name = format_path(maker.format_file_name(post['article_title']) + '.sd')
                    if os.path.isfile(os.path.join(out_dir, file_name) + '.ts'):
                        print(file_name + ' exists')
                        break
                    
                    play_url = play_info.get('PlayURL')
                    p.apply_async(dl.run, (play_url, out_dir, file_name))

                    p.close()
                    p.join()
                    print('download {} done, cost {}s\n'.format(course_data['column_title'], int(time.time() - start)))
                      
            except Exception as e:
                print (e)
                print(traceback.format_exc())
            time.sleep(1)

class Mp4Batch(Mp4):
    # 批量下载 mp4
    def run(self, args):
        if '--all' in args:
            dc = DataClient()
            data = dc.get_course_list()
            cid_list = []
            for c in data['3']['list']:
                if c['had_sub']:
                    cid_list.append(str(c['id']))
        else:
            course_ids = args[0]
            cid_list = course_ids.split(',')
        for cid in cid_list:
            super(Mp4Batch, self).run([cid.strip()] + args)
            time.sleep(5)
