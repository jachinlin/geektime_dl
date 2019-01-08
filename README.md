# 把极客时间专栏装进Kindle

[![travis](https://travis-ci.org/jachinlin/geektime_dl.svg?branch=master)](https://travis-ci.org/jachinlin/geektime_dl)
[![codecov](https://codecov.io/gh/jachinlin/geektime_dl/branch/master/graph/badge.svg)](https://codecov.io/gh/jachinlin/geektime_dl)
[![Python versions](https://img.shields.io/pypi/pyversions/geektime-dl.svg)](https://pypi.org/project/geektime-dl/)
[![PyPI - Downloads](https://img.shields.io/pypi/dd/geektime-dl.svg)](https://pypi.org/project/geektime-dl/)
[![PyPI](https://img.shields.io/pypi/v/geektime-dl.svg)](https://pypi.org/project/geektime-dl/)


<p align="center" style="margin:70px">
    <img src="https://raw.githubusercontent.com/jachinlin/jachinlin.github.io/master/img/gk-mp4.gif" alt="左耳听风">
</p>

极客时间专栏文章的质量都是非常高的，比如耗子哥的《左耳听风》、朱赟的《朱赟的技术管理课》和王天一的《人工智能基础课》，都是我非常喜欢的专栏。这些专栏深入浅出，将知识和经验传授于读者，都是值得多次阅读的。

然而，每当空闲时间时，都需要掏出手机才能阅读专栏文章，这在某种情况下是很不便的，尤其坐地铁且没有网络时。作为一个kindle党，最好的解决方案就是kindle电子书。于是有了这个项目

>[把极客时间装进Kindle](https://github.com/jachinlin/geektime_ebook_maker)

现在，这个项目除了将专栏制作成`kindle`电子书，还提供了下载`mp3`和`mp4`等功能，具体见下使用方法。


## 一、项目结构

<p align="center" style="margin:70px">
    <img src="https://github.com/jachinlin/jachinlin.github.io/blob/master/img/gk-chart.png?raw=true" alt="流程图">
</p>


这个项目主要包括下边这几个部分

- kindle_maker: 一个mobi电子书制作工具。用户只需要提供制作电子书的html文件，和一个包含目录信息的toc.md文件，kindle_maker即可制作出一本精美的kindle电子书。这部分已拎出来放在单独的项目里，具体使用方式见该项目文档[kindle_maker](https://github.com/jachinlin/kindle_maker)

- geektime_ebook: 主要将抓取到的数据转化为 kindle_maker 需要的源文件，主要是 html 文件

- utils: 提供了mp3和mp4下载器等工具

- gk_apis: `gk_apis`封装了极客时间的若干api

- store_client: 存储相关数据至sqlite3

- cli: 提供若干cmd命令(subcmd)，将上面这个部分连接在一起，最后使用 kindle_maker 制作电子书，或者使用下载器下载相关音视频



## 二、依赖

- [requests](http://www.python-requests.org/en/master/): 网络请求

- [Jinja2](http://jinja.pocoo.org/): html模板引擎

- [kindle_maker](https://github.com/jachinlin/kindle_maker): 制作kindle电子书

- [Kindlegen](https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211): kindle_maker核心依赖



## 三、使用

### 安装

#### 虚拟环境 virtualenv
```
virtualenv -p python3 ~/venv3 && source ~/venv3/bin/activate
```

#### 代码

```
pip install -U geektime_dl
```

#### 安装kindlegen

1. Linux:

```
wget http://kindlegen.s3.amazonaws.com/kindlegen_linux_2.6_i386_v2_9.tar.gz -O - | tar -xzf - -C ~/venv3/bin
```

2. macOS:

```
brew install homebrew/cask/kindlegen
```

3. Windows:

```
not test now!

use docker, see below
```


### 运行

#### 查看帮助信息

1、查看 cli subcmd

```
geektime help
```

2、查看具体 cli subcmd 帮助信息

```
geektime <subcmd> --help
```

`<subcmd>` 为具体的子命令名，可以从 help 子命令查看。


#### 登录保存登录token

```
geektime login  [--account=<account>] [--password=<password>] [--area=<area>]
```

`[]`表示可选，`<>`表示相应变量值，下同

- --account: 手机账号，不提供可稍后手动输入
- --password: 账号密码，不提供可稍后手动输入
- --area: 注册手机号所属地区，默认86


#### 查看极客时间课程列表

```
geektime query
```

执行该命令后，我们可以看到专栏、视频、微课等课程的课程标题、订阅情况、更新频率还有课程ID，这个**课程ID**很重要，咱们下边的操作就是基于这个ID进行的。

```
专栏
        课程ID        已订阅       课程标题             更新频率/课时·时长
        49             否         朱赟的技术管理课      (全集)
        48             是         左耳听风      (全集)
        ......
微课
        课程ID        已订阅       课程标题             更新频率/课时·时长
        75             是         深入浅出gRPC  (全集)
        73             否         Service Mesh实践指南  (全集)
        ......
视频
        课程ID        已订阅       课程标题             更新频率/课时·时长
        138            是         Nginx核心知识100讲    (100课时，约600分钟)
        130            否         算法面试通关40讲      (40课时·约500分钟)
        ......
其他
        课程ID        已订阅       课程标题             更新频率/课时·时长
        69             否         零基础入门 Python 机器学习    (None)
        70             否         零基础入门 TensorFlow (None)
```

#### 制作电子书

```
geektime ebook <course_id> [--out-dir=<out_dir>] [--enable-comments] [--comment-count=<comment_count>]
```

- course_id: 课程ID，可以从 query subcmd 查看
- --out_dir: 电子书存放目录，默认`./ebook/`
- --enable-comments: 启动评论下载，默认不下载评论
- --comment-count: 在启动评论下载时，设置评论条数，默认10条

notice: 此 subcmd 需要先执行 login subcmd

*批量下载所有已订阅专栏的方法`geektime query | grep '是' | cut -d ' ' -f 1 | xargs -I {} geektime ebook {}`*

#### 下载mp3

```
geektime mp3 <course_id> [--url-only] [--out-dir=<out_dir>]
```
- course_id: 课程ID，可以从 query subcmd 查看
- --url-only: 只保存音频url，不下载音频
- --out_dir: 音频存放目录，默认`./mp3/`


notice: 此 subcmd 需要先执行 login subcmd

#### 下载mp4

```
geektime mp4 <course_id> [--url-only] [--hd-only] [--out-dir=xxx]
```

- course_id: 课程ID，可以从 query subcmd 查看
- --url-only: 只保存视频url
- --hd-only：下载高清视频，默认下载标清视频
- --out_dir: 视频存放目录，默认`./mp4/`

notice: 此 subcmd 需要先执行 login subcmd

#### 推送到kindle

如果你想把制作完成的电子书推送到kindle的话，需要在工作目录(当前目录)下添加 `smtp.conf` smtp配置文件，文件格式如下（以qq邮箱为例），

```
{
    "host": "smtp.qq.com",
    "port": "465",
    "user": "1234@qq.com",
    "password": "psd",
    "encryption": "ssl",
    "email_to": "xxx@kindle.cn"
}
```

然后在[制作电子书](https://github.com/jachinlin/geektime_dl#%E5%88%B6%E4%BD%9C%E7%94%B5%E5%AD%90%E4%B9%A6) ebook subcmd后添加 `--push` 参数即可，例如，

```
geektime ebook 42 --push
```

至于邮箱smtp配置和kindle邮箱配置就自行google吧。

## 四、Docker

如果你对 Python 不是很了解，对上面的安装过程还是很迷惑的话，
我们还提供了 docker 版本，只要安装好 docker ，依次复制下边指令并执行，
就能下载全部已购买专栏文章、mp3、mp4，如果专栏更新完毕的话，我们还会把该专栏做成kindle电子书。

```
# 构建
docker build https://github.com/jachinlin/geektime_dl.git -t geektime

# 登录
docker run -v `pwd`:/output -it --rm geektime login

# 下载
docker run -v `pwd`:/output -it --rm geektime ebookbatch --all --enable-comments
docker run -v `pwd`:/output --rm geektime mp4batch --all
docker run -v `pwd`:/output --rm geektime mp3batch --all
```


## 五、效果

我把免费试读的课程章节的电子书、音频、视频都下载下来，并上传到网盘，你可以把资源下载下来查看效果

- [百度网盘mp4](https://pan.baidu.com/s/13Vu8N94wK4gWP86bJI9wAA ) 密码:j9yx
- [百度网盘mp3](https://pan.baidu.com/s/1_l5iBZxcBZi0pGszM1oE9A)  密码:byng
- [百度网盘ebook](https://pan.baidu.com/s/19lNyWE2FxXBHPwsAlTg4EQ) 密码:phng

## 六、Todo list

- [X] MP3 and MP4
- [X] comments
- [X] batch download
- [X] docker
- [X] push to kindle
- [ ] support mathjax
- [ ] ...


## 七、其他

1. 注意版权，勿传播电子书及音视频
2. pr or issue is welcome


