
# 简介

## 项目结构

这个项目主要包括下边这几个部分：

- kindle_maker: 一个 mobi 电子书制作工具。用户使用 kindle_maker 就可以轻松制作出一本精美的 kindle 电子书。这部分已拎出来放在单独的项目里，具体使用方式见该项目文档： [kindle_maker](https://github.com/jachinlin/kindle_maker)；

- utils: 提供了 mp3/mp4 下载、邮件发送、html 文件生成等功能；

- gk_apis: 封装了极客时间 api；

- store_client: 缓存极客时间专栏数据至本地 json 文件；

- cli: 提供若干cmd 命令，将上面这几个部分连接在一起，最后使用 kindle_maker 制作电子书，或者使用下载器下载相关音视频。

## 主要依赖

- [Python](https://dPocs.python.org/3.6/): 支持的 Python 版本为 3.6 及以上

- [requests](http://www.python-requests.org/en/master/): 网络请求

- [Jinja2](http://jinja.pocoo.org/): html 模板引擎

- [kindle_maker](https://github.com/jachinlin/kindle_maker): 制作 kindle 电子书

## 安装

### 安装 Python 解释器

目前仅支持 Python3.6+（包含），请在 [Python 官网](https://www.python.org/downloads/)下载并安装您熟悉的版本对应的 Python 解释器。

### 虚拟环境

```bash
mkdir geektime $$ cd geektime
python3 -m venv venv3 && source venv3/bin/activate
```

### 安装 geektime-dl

```bash
pip install -U geektime_dl
```

或者源码安装，这样可以获取最新的特性

```bash
pip install -U git+https://github.com/jachinlin/geektime_dl.git
```

### 检验是否正确安装

```bash
geektime help
```

执行上述命令，如果出现 `command not found: geektime`，则说明没有正确安装，请按照上面步骤重新按照，如果还有困难的话，可以[提 issue](https://github.com/jachinlin/geektime_dl/issues/new)获取帮助；如果 terminal 显示的是其他信息，则说明您已经正确安装该软件了，恭喜您，咱们可以进行下一步了。
## 查看帮助信息

```bash
geektime help
```

该命令会显示所有支持的命令（command），以及所支持的命令的简要说明，具体输出如下：

```bash
Available commands:
    daily  保存每日一课视频
    ebook  将专栏文章制作成电子书
    help   Display the list of available commands
    login  登录极客时间，保存账号密码至配置文件
    mp3    保存专栏音频
    mp4    保存视频课程视频
    query  查看课程列表

Use 'geektime <command> --help' for individual command help.
```

通过下边的操作可以查看具体命令（command）的帮助信息

```bash
geektime <command> --help
```

例如，

```bash
geektime ebook --help
```

这条命令就可以显示出 `ebook` 命令（制作 mobi 电子书命令）的使用说明和所有的参数说明

```bash
usage: geektime ebook
       [-h] [-a ACCOUNT] [-p PASSWORD] [--area AREA] [--config CONFIG]
       [-o OUTPUT_FOLDER] [--no-login] [--image-ratio IMAGE_RATIO]
       [--image-min-height IMAGE_MIN_HEIGHT]
       [--image-min-width IMAGE_MIN_WIDTH] [--email-to EMAIL_TO]
       [--smtp-password SMTP_PASSWORD] [--smtp-user SMTP_USER]
       [--smtp-encryption SMTP_ENCRYPTION] [--smtp-port SMTP_PORT]
       [--smtp-host SMTP_HOST] [--push] [--comments-count COMMENTS_COUNT]
       [--force]
       course_ids

将专栏文章制作成电子书

positional arguments:
  course_ids            specify the target course ids

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT, --account ACCOUNT
                        specify the account phone number (default: None)
  -p PASSWORD, --password PASSWORD
                        specify the account password (default: None)
  --area AREA           specify the account country code (default: 86)
  --config CONFIG       specify alternate config file (default:
                        /Users/linjiaxian/dev/geektime_dl/geektime.cfg)
  -o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                        specify the output folder (default:
                        /Users/linjiaxian/dev/geektime_dl)
  --no-login            no login, just for test (default: False)
  --image-ratio IMAGE_RATIO
                        image ratio (default: None)
  --image-min-height IMAGE_MIN_HEIGHT
                        image min height (default: None)
  --image-min-width IMAGE_MIN_WIDTH
                        image min width (default: None)
  --email-to EMAIL_TO   specify the kindle receiver email (default: None)
  --smtp-password SMTP_PASSWORD
                        specify the smtp password (default: None)
  --smtp-user SMTP_USER
                        specify the smtp user (default: None)
  --smtp-encryption SMTP_ENCRYPTION
                        specify the a smtp encryption (default: None)
  --smtp-port SMTP_PORT
                        specify the a smtp port (default: None)
  --smtp-host SMTP_HOST
                        specify the smtp host (default: None)
  --push                push to kindle (default: False)
  --comments-count COMMENTS_COUNT
                        the count of comments to fetch each post (default: 0)
  --force               do not use the cache data (default: False)
```

具体命令的参数说明是使用 `argparse` 生成的，如果你对于上面的参数说明感到迷惑的话，可以先阅读 [argparse 的文档](https://docs.python.org/3.8/howto/argparse.html)。

下一步，请阅读[使用说明](/guide.html)。
