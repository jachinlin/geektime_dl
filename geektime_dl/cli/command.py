# coding=utf8

import sys
import os
import traceback
import configparser
import argparse
import functools
from typing import List

from geektime_dl.utils.log import logger
from geektime_dl.data_client import get_data_client, DataClient


commands = {}

cwd = os.path.abspath('.')
geektime_cfg = os.path.join(cwd, 'geektime.cfg')


class CommandType(type):
    def __init__(cls, name, bases, attrs):
        super(CommandType, cls).__init__(name, bases, attrs)
        name = getattr(cls, name, cls.__name__.lower())
        cls.name = name
        if name != 'command':
            commands[name] = cls


class Help(metaclass=CommandType):
    """Display the list of available commands"""

    def work(self, args: list):
        result = ["Available commands:"]
        names = list(commands)
        padding = max([len(k) for k in names]) + 2
        for k in sorted(names):
            name = k.ljust(padding, ' ')
            doc = (commands[k].__doc__ or '').split('\n')[0]
            result.append("    %s%s" % (name, doc))
        result.append(
            "\nUse '{} <command> --help' for individual command help.".format(
                sys.argv[0].split(os.path.sep)[-1]))

        result = '\n'.join(result) + '\n'
        sys.stdout.write(result)
        return result


def add_argument(*args, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrap(*a, **kw):
            return func(*a, **kw)

        if not hasattr(wrap, 'save_cfg_keys'):
            wrap.save_cfg_keys = []
        if not hasattr(wrap, 'arguments'):
            wrap.arguments = []
        if kwargs.get('save'):
            kwargs.pop('save')
            if 'dest' in kwargs:
                wrap.save_cfg_keys.append(kwargs['dest'])
        wrap.arguments.append((args, kwargs))
        return wrap
    return decorator


class Command(metaclass=CommandType):
    _default_save_cfg_keys = ['area', 'account', 'password', 'output_folder']

    def __init__(self):
        self._parser = None

    @staticmethod
    def is_course_finished(course_info: dict):
        return course_info['update_frequency'] in ['全集', '已完结'] or \
            course_info['is_finish']

    @staticmethod
    def get_data_client(cfg: dict) -> DataClient:
        try:
            dc = get_data_client(cfg)
            return dc
        except Exception:
            raise ValueError(
                "invalid geektime account or password\n"
                "Use '{} login --help' for  help.\n".format(
                    sys.argv[0].split(os.path.sep)[-1]))

    def get_all_course_ids(self, dc: DataClient, type_: str) -> List[int]:
        raise NotImplementedError

    def parse_course_ids(self, ids_str: str, dc: DataClient) -> List[int]:

        if ids_str.startswith('all'):
            return self.get_all_course_ids(dc, type_=ids_str)

        def _int(num):
            try:
                return int(num)
            except Exception:
                raise ValueError('illegal course ids: {}'.format(ids_str))
        res = list()
        segments = ids_str.split(',')
        for seg in segments:
            if '-' in seg:
                s, e = seg.split('-', 1)
                res.extend(range(_int(s), _int(e) + 1))
            else:
                res.append(_int(seg))
        res = list(set(res))
        res.sort()
        return res

    @property
    def parser(self) -> argparse.ArgumentParser:
        if self._parser:
            return self._parser
        parser = argparse.ArgumentParser(
            prog='{} {}'.format(sys.argv[0], self.name),
            description=self.__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument("-a", "--account", dest="account",
                            help="specify the account phone number")
        parser.add_argument("-p", "--password", dest="password",
                            help="specify the account password")
        parser.add_argument("--area", dest="area", default='86',
                            help="specify the account country code")
        parser.add_argument("--config", dest="config", default=geektime_cfg,
                            help="specify alternate config file")
        parser.add_argument("-o", "--output-folder", dest="output_folder",
                            default=cwd, help="specify the output folder")

        parser.add_argument("--no-login", dest="no_login", action='store_true',
                            default=False, help="no login, just for test")
        for args, kwargs in getattr(self.run, 'arguments', []):
            parser.add_argument(*args, **kwargs)
        self._parser = parser
        return parser

    @staticmethod
    def load_cfg(cfg_file: str) -> dict:
        p = configparser.RawConfigParser()
        cfg = dict()
        try:
            p.read([cfg_file])
            for (name, value) in p.items('default'):
                cfg[name] = value
        except IOError:
            pass
        except configparser.NoSectionError:
            pass

        return cfg

    def _parse_config(self, args: list):

        cfg_file = geektime_cfg
        if '--config' in args:
            index = args.index('--config') + 1
            if index < len(args):
                cfg_file = args[index]
        saved_cfg = self.load_cfg(cfg_file)

        save_cfg_keys = (getattr(self.run, 'save_cfg_keys', []) +
                         self._default_save_cfg_keys)
        for key in save_cfg_keys:
            if key in saved_cfg:
                _ = ['--{}'.format(key.replace('_', '-')), saved_cfg[key]]
                # add saved configs in front so that
                # it has the chance to be overridden
                args = _ + args
        opt = self.parser.parse_args(args)
        cfg = vars(opt)

        saved_cfg.update({k: cfg[k] for k in save_cfg_keys if cfg.get(k)})
        self.save_cfg(saved_cfg, cfg_file)
        return cfg

    @classmethod
    def save_cfg(cls, cfg: dict, cfg_file: str) -> None:

        old_cfg = cls.load_cfg(cfg_file)
        old_cfg.update(cfg)
        cfg = old_cfg
        p = configparser.RawConfigParser()
        p.add_section('default')
        for opt in sorted(cfg):
            p.set('default', opt, cfg[opt])

        # try to create the directories and write the file
        cfg_exist = os.path.exists(cfg_file)
        if not cfg_exist and not os.path.exists(os.path.dirname(cfg_file)):
            try:
                os.makedirs(os.path.dirname(cfg_file))
            except OSError:
                sys.stderr.write(
                    "ERROR: couldn't create the config directory\n")
        try:
            with open(cfg_file, 'w') as f:
                p.write(f)
        except IOError:
            sys.stderr.write("ERROR: couldn't write the config file\n")

    def work(self, args: list):
        if '--help' in args or '-h' in args:
            self.parser.parse_args(args)
            return
        cfg = self._parse_config(args)
        return self.run(cfg)

    def run(self, args: dict):
        raise NotImplementedError


def main():
    args = sys.argv[1:]

    # default subcommand
    command = Help.name

    # subcommand discovery
    if len(args):
        command = args[0]
        args = args[1:]

    if command in commands:
        o = commands[command]()
        try:
            o.work(args)
        except Exception as e:
            sys.stderr.write("ERROR: {}\n".format(e))
            logger.error('ERROR: {}'.format(traceback.format_exc()))
    else:
        sys.stderr.write('Unknown command %r\n\n' % (command,))
        Help().work(args)
