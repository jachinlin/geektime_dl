<p align="center" style="padding:10%">
    <img src="https://raw.githubusercontent.com/jachinlin/jachinlin.github.io/master/img/gk-mp4.gif" alt="左耳听风">
</p>


# 把极客时间专栏装进Kindle

[![travis](https://travis-ci.org/jachinlin/geektime_dl.svg?branch=master)](https://travis-ci.org/jachinlin/geektime_dl)
[![codecov](https://codecov.io/gh/jachinlin/geektime_dl/branch/master/graph/badge.svg)](https://codecov.io/gh/jachinlin/geektime_dl)

极客时间专栏文章的质量都是非常高的，比如耗子哥的《左耳听风》、朱赟的《朱赟的技术管理课》和王天一的《人工智能基础课》，都是我非常喜欢的专栏。这些专栏深入浅出，将知识和经验传授于读者，都是值得多次阅读的。

然而，每当空闲时间时，都需要掏出手机才能阅读专栏文章，这在某种情况下是很不便的，尤其坐地铁且没有网络时。作为一个kindle党，最好的解决方案就是kindle电子书。于是有了这个项目

>[把极客时间装进Kindle](https://github.com/jachinlin/geektime_ebook_maker)

现在，这个工具除了将专栏制作成`kindle`电子书，还提供了下载`mp3`和`mp4`等功能，具体见下使用方法。


## 一、项目结构

<p align="center">
    <img src="https://github.com/jachinlin/jachinlin.github.io/blob/master/img/gk-chart.png?raw=true" alt="流程图">
</p>


这个项目主要包括下边这几个部分

- kindle_maker: 一个mobi电子书制作工具。用户只需要提供制作电子书的html文件，和一个包含目录信息的toc.md文件，kindle_maker即可制作出一本精美的kindle电子书。这部分已拎出来放在单独的项目里，具体使用方式见该项目文档[kindle_maker](https://github.com/jachinlin/kindle_maker)
- geektime_ebook: 主要将抓取到的数据转化为 kindle_maker 需要的源文件
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
cd ~ && virtualenv -p python3 venv3 && source venv3/bin/activate
```

#### 代码

```
pip install -U git+https://github.com/jachinlin/geektime_dl.git
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
coming soon ~~
or pr is welcome
```


### 运行

#### 查看帮助信息

1、查看 cli subcmd

```
geektime help
```

![gk-help](https://github.com/jachinlin/jachinlin.github.io/blob/master/img/gk-help.png?raw=true)


2、查看具体 cli subcmd 帮助信息

```
geektime ebook --help
```

![gk-ebook-help](https://github.com/jachinlin/jachinlin.github.io/blob/master/img/gk-ebook-help.png?raw=true)


#### 登录保存登录token

```
geektime login
```

按照相关提示输入账号、密码即可


#### 查看极客时间课程列表

```
geektime query
```

![gk-query](https://github.com/jachinlin/jachinlin.github.io/blob/master/img/gk-query.png?raw=true)


#### 制作电子书

![gk-ebook](https://github.com/jachinlin/jachinlin.github.io/blob/master/img/gk-ebook.png?raw=true)


#### 下载mp3

![gk-mp3](https://github.com/jachinlin/jachinlin.github.io/blob/master/img/gk-mp3.png?raw=true)


#### 下载mp4

![gk-mp4](https://github.com/jachinlin/jachinlin.github.io/blob/master/img/gk-mp4.png?raw=true)



## 四、Docker

see [Dockerfile for 把极客时间专栏装进Kindle](https://hub.docker.com/r/jostyee/docker_geektime_ebook_maker/)


## 五、效果




### Todo list

- [ ] support mathjax
- [X] MP3 and MP4
- [ ] support windows
- [ ] ...


