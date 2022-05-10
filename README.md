
:sparkles: 重要 :sparkles:

**查看 [使用文档](https://jachinlin.github.io/geektime_dl/) 获取最新使用信息。**

<br/><br/>

本 README.md 不再更新！:point_down:

<p align="center">
    <img  width="80%" src="https://raw.githubusercontent.com/jachinlin/geektime_dl/master/docs/.vuepress/public/geektime.gif" alt="左耳听风">
</p>

# 把极客时间装进 Kindle

[![PyPI](https://img.shields.io/pypi/v/geektime-dl.svg)](https://pypi.org/project/geektime-dl/)
[![CI & CD](https://github.com/jachinlin/geektime_dl/workflows/CI%20&%20CD/badge.svg)](https://github.com/jachinlin/geektime_dl/actions)

极客时间专栏文章的质量都是非常高的，比如耗子哥的《左耳听风》、朱赟的《朱赟的技术管理课》和王天一的《人工智能基础课》，都是我非常喜欢的专栏。这些专栏深入浅出，将知识和经验传授于读者，都是值得多次阅读的。

然而，每当空闲时间时，都需要掏出手机才能阅读专栏文章，这在某种情况下是很不便的，尤其坐地铁且没有网络时。作为一个 kindle 党，最好的解决方案就是 kindle 电子书。于是有了这个项目

>[把极客时间装进Kindle](https://github.com/jachinlin/geektime_dl)



## 安装

```bash
pip install -U geektime_dl

# 或者安装最新代码
pip install -U git+https://github.com/jachinlin/geektime_dl.git
```

## 使用


**查看帮助信息**


1、查看 cli subcmd

```bash
geektime help
```

2、查看具体 cli subcmd 帮助信息

```bash
geektime <subcmd> --help
```

`<subcmd>` 为具体的子命令名，可以从 help 子命令查看。


**登录**

```bash
geektime login  [--account=<account>] [--password=<password>] [--area=<area>]
```

`[]`表示可选，`<>`表示相应变量值，下同

- account: 手机账号，不提供可稍后手动输入
- password: 账号密码，不提供可稍后手动输入
- area: 注册手机号所属地区，默认86


**查看课程列表**


```bash
geektime query
```


执行该命令后，我们可以看到专栏、视频、微课等课程的课程标题、订阅情况、更新频率还有课程ID，这个**课程ID**很重要，咱们下边的操作就是基于这个ID进行的。
```
专栏
        课程ID        已订阅       课程标题             更新频率/课时·时长
        49             否         朱赟的技术管理课      (全集)
        48             是         左耳听风      (全集)
        ......
```


**制作电子书**

```bash
geektime ebook <course_id> [--output-folder=<output_folder>]
```

- course_id: 课程ID，可以从 query subcmd 查看
- output_folder: 电子书存放目录，默认`cwd`

notice: 此 subcmd 需要先执行 login subcmd


## Todo list

- [X] 评论
- [X] 批量下载
- [X] docker
- [ ] 支持 mathjax 数学公式
- [ ] ...


## 其他

1. 注意版权，勿传播电子书
2. pr or issue is welcome


