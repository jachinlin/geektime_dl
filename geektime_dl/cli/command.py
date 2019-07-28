# coding=utf8

import sys
import os
import traceback
import configparser
import argparse

from ..utils._logging import logger


commands = {}


geektime_cfg = os.path.abspath('./geektime.cfg')
cwd = os.path.abspath('.')


class CommandType(type):
    def __init__(cls, name, bases, attrs):
        super(CommandType, cls).__init__(name, bases, attrs)
        name = getattr(cls, name, cls.__name__.lower())
        cls.name = name
        if name != 'command':
            commands[name] = cls


def work(self: 'Command', args: list):
    if '--help' in args or '-h' in args:
        result = (self.__doc__ or '').strip()
        sys.stdout.write("{}\n".format(result))
        return
    cfg = parse_config(args)
    return self.run(cfg)


Command = CommandType('Command', (object,), {'run': lambda self, args: None, 'work': work})


class Help(Command):
    """Display the list of available commands"""
    def run(self, cfg):
        result = ["Available commands:"]
        names = list(commands)
        padding = max([len(k) for k in names]) + 2
        for k in sorted(names):
            name = k.ljust(padding, ' ')
            doc = (commands[k].__doc__ or '').split('\n')[0]
            result.append("    %s%s" % (name, doc))
        result.append("\nUse '%s <command> --help' for individual command help." % sys.argv[0].split(os.path.sep)[-1])

        result = '\n'.join(result)
        sys.stdout.write(result)
        return result


def _load_cfg(cfg_file: str) -> dict:

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


def save_cfg(cfg: dict) -> None:
    cfg_file = cfg.get('config') or geektime_cfg

    p = configparser.RawConfigParser()
    p.add_section('default')
    for opt in sorted(cfg):
        if opt in ['config', 'course_id', 'course_ids']:
            continue
        p.set('default', opt, cfg[opt])

    # try to create the directories and write the file
    cfg_exist = os.path.exists(cfg_file)
    if not cfg_exist and not os.path.exists(os.path.dirname(cfg_file)):
        try:
            os.makedirs(os.path.dirname(cfg_file))
        except OSError:
            sys.stderr.write("ERROR: couldn't create the config directory\n")
    try:
        p.write(open(cfg_file, 'w'))
    except IOError:
        sys.stderr.write("ERROR: couldn't write the config file\n")


def parse_config(args: list) -> dict:
    parser = argparse.ArgumentParser(prog='{} <command>'.format(sys.argv[0]))
    parser.add_argument("--config", dest="config", type=str, default=geektime_cfg,
                      help="specify alternate config file")
    parser.add_argument("-a", "--account", dest="account", type=str,
                      help="specify the account phone number")
    parser.add_argument("-p", "--password", dest="password", type=str,
                      help="specify the account password")
    parser.add_argument("--area", dest="area", type=str, default='86',
                      help="specify the account country code")
    parser.add_argument("-o", "--output-folder", dest="output_folder", type=str, default=cwd,
                      help="specify the output folder")
    parser.add_argument("-c", "--course-id", dest="course_id", type=int,
                      help="specify the target course id")
    parser.add_argument("--force", dest="force", action='store_true', default=False,
                      help="do not use the cache data")
    parser.add_argument("--enable-comments", dest="enable_comments", action='store_true', default=False,
                      help="fetch the course comments")
    parser.add_argument("--comments-count", dest="comments_count", type=int, default=10,
                      help="the count of comments to fetch each post")
    parser.add_argument("--push", dest="push", action='store_true', default=False,
                      help="push to kindle")
    parser.add_argument("--source-only", dest="source_only", action='store_true', default=False,
                      help="download source file only")
    parser.add_argument("--url-only", dest="url_only", action='store_true', default=False,
                        help="download mp3/mp4 url only")
    parser.add_argument("--hd-only", dest="hd_only", action='store_true', default=False,
                        help="download mp4 with high quality")
    parser.add_argument("--all", dest="all", action='store_true',  default=False,
                      help="fetch all courses")
    parser.add_argument("--course-ids", dest="course_ids",  type=str,
                      help="specify the target course ids")
    parser.add_argument( "--smtp-host", dest="smtp_host", type=str,
                        help="specify the smtp host")
    parser.add_argument("--smtp-port", dest="smtp_port", type=int,
                        help="specify the a smtp port")
    parser.add_argument("--smtp-encryption", dest="smtp_encryption", type=int,
                        help="specify the a smtp encryption")
    parser.add_argument("--smtp-user", dest="smtp_user", type=str,
                        help="specify the smtp user")
    parser.add_argument("--smtp-password", dest="smtp_password", type=str,
                        help="specify the smtp password")
    parser.add_argument("--email-to", dest="email_to", type=str,
                        help="specify the kindle receiver email")
    parser.add_argument("--workers", dest="workers", type=int, default=1,
                        help="specify the workers number")

    opt = parser.parse_args(args)

    cfg_file = opt.config
    cfg = _load_cfg(cfg_file)

    keys = ['config', 'account', 'area', 'password', 'output_folder',
            'force', 'enable_comments', 'comments_count', 'push',
            'course_id', 'source_only', 'url_only', 'hd_only', 'all', 'course_ids',
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password',
            'smtp_encryption', 'email_to', 'workers']
    for name in keys:
        if getattr(opt, name, None) is not None:
            cfg[name] = getattr(opt, name)
    save_cfg(cfg)

    return cfg


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
            sys.stderr.write("ERROR: {}".format(e))
            logger.error('ERROR: {}'.format(traceback.format_exc()))
    else:
        print('Unknow command %r\n\n' % (command,))
