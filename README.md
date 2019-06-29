# 极客时间专栏下载

这是 github 项目 [geektime_dl](https://github.com/jachinlin/geektime_dl) 的一份 fork, 我做了如下修改

- 删除 sqlite 部分，让项目依赖更少(坏处是增多了不必要的请求)
- 修复 爬取过程中 cookie 失效的问题
- 修复 极客时间专栏使用阿里云点播服务 mp4 无法下载的问题
- 修复 html 样式混乱问题(渣前端，胡乱塞点样式，能看就好……(^O^))
- 极客时间最有价值的评论循环爬取
- 增加 ffmpeg 转码 shell 脚本(渣运维，写 python 脑仁疼，直接用shell吧:-D)
- 删除过多参数(懒得写参数), 账户密码/下载路径放配置文件中
- 删除测试脚本(不要喷...)
- 删除推送到 kindle (我真的不需要)

# 使用方法


#### 安装kindlegen

- Linux:

```
wget http://kindlegen.s3.amazonaws.com/kindlegen_linux_2.6_i386_v2_9.tar.gz -O - | tar -xzf - -C ~/venv3/bin
```

- macOS:

```
brew install homebrew/cask/kindlegen
```

#### 初始化

```
virtualenv -p python3 ./venv3
cp config.ini.tmpl config.ini 

```
#### 下载

- 批量下载

```

source venv/bin/activate
python geektime.py ebookbatch --all
python geektime.py mp3batch --all
python geektime.py mp4batch --all
```

- 查询

```
source venv/bin/activate
geektime.py query
```

- 下载单独的课程

```
source venv/bin/activate
geektime.py ebook <course_id>
```

# 项目结构

- kindle_maker: 一个mobi电子书制作工具。用户只需要提供制作电子书的html文件，和一个包含目录信息的toc.md文件，kindle_maker即可制作出一本精美的kindle电子书。这部分已拎出来放在单独的项目里，具体使用方式见该项目文档[kindle_maker](https://github.com/jachinlin/kindle_maker)

- geektime_ebook: 主要将抓取到的数据转化为 kindle_maker 需要的源文件，主要是 html 文件

- utils: 提供了 mp3 和 mp4 下载器等工具

- gk_apis: `gk_apis`封装了极客时间的若干 api

- store_client: 删除了原有sqlite3 存储

- cli: 提供若干cmd命令(subcmd)，将上面这个部分连接在一起，最后使用 kindle_maker 制作电子书，或者使用下载器下载相关音视频

## 依赖

- [requests](http://www.python-requests.org/en/master/): 网络请求

- [Jinja2](http://jinja.pocoo.org/): html模板引擎

- [kindle_maker](https://github.com/jachinlin/kindle_maker): 制作kindle电子书

- [Kindlegen](https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211): kindle_maker核心依赖

## Todo list

- [ ] support mathjax
- [ ] ...

## 其他

1. 注意版权，勿传播电子书及音视频
2. pr or issue is welcome


