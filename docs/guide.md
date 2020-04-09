

# 使用说明

阅读下文前，请先确保已[安装](/intro.html#安装) geektime-dl。

## 登录

```bash
geektime login  [--account=<account>] [--password=<password>] [--area=<area>]
```

`[]` 表示可选，`<>` 表示相应变量值。

> 下边其他命令中的 `[]` 和 `<>` 也表示这个意思，就不一一说明了。

这个命令有三个参数，

- account: 手机账号，不提供可稍后手动输入
- password: 账号密码，不提供可稍后手动输入
- area: 注册手机号所属地区，默认 `86`。当您是美国手机号注册时，area 需要设置为 `1`。

您也可以通过以下命令获取详细帮助信息。

```bash
geektime login --help
```

登录成功后，您的账号密码将会保存在 `$(pwd)/geektime.cfg`。执行其他操作时，geektime 将从这个配置文件读取账号密码。

## 查看课程列表

> 执行该命令前，请确保账号密码已经保存在 `$(pwd)/geektime.cfg`。
>
> 如果没有，请执行 `geektime login` 进行账号密码验证和保存。

```bash
geektime query
```

执行该命令后，我们可以看到专栏、视频、微课等课程的课程标题、订阅情况、更新频率还有课程ID，这个 **课程ID** 很重要，我们下边的操作就是基于这个ID进行的。

这里，我截取部分输出结果：

```bash
(venv3) ➜ geektime query
专栏
	课程ID        已订阅	已完结	课程标题
	301            否	否	数据中台实战课
	298            否	否	检索技术核心20讲
	297            否	否	SRE实战手册
	296            否	否	图解 Google V8
```


## 制作电子书

> 执行该命令前，请确保账号密码已经保存在 `$(pwd)/geektime.cfg`。
>
> 如果没有，请执行 `geektime login` 进行账号密码验证和保存。


```bash
geektime ebook <course_id>  [--comments-count=<comments_count>]
```

参数 `course_id` 表示课程ID，可以从 `geektime query` 查看获取到；
`comments_count` 表示评论条数，不设置的话则默认为 0条，您可以根据专栏评论的含金量来调整该参数大小。

示例：
```bash
geektime ebook 49 --comments-count=10
```

### 推送到 Kindle 设备


如果您想把制作完成的电子书自动推送到心爱的 Kindle 设备的话，需要提供以下 smtp 配置和 Kindle 推送邮箱：


- --smtp-encryption
- --smtp-host
- --smtp-port
- --smtp-user
- --smtp-password
- --email-to：Kindle 推送邮箱：


然后在[制作电子书基础命令](/guide.html#制作电子书)后添加 `--push` 以及上面参数即可。

例如，

```bash
geektime ebook 49 --push --smtp-host=smtp.qq.com --smtp-port=465 --smtp-encryption=ssl --smtp-user=your_qq_number@qq.com --smtp-password=your_password --email-to=your_kindle_email@kindle.cn
```

执行该命令后，smtp 配置和 Kindle 推送邮箱就会保存在 `$(pwd)/geektime.cfg`，下次推送电子书时就不用添加这些参数了，只要 `geektime ebook 49 --push` 即可。打开 `$(pwd)/geektime.cfg` 验证一下吧。

至于邮箱 smtp 配置和 Kindle邮箱配置就自行 google 吧。

### 压缩电子书大小

直接使用 `geektime ebook <course_id>` 生成的电子书大于 50M（因为含有大量图片），超过邮箱附件的大小限制，所以我们需要对图片进行压缩，这时候参数 `--image-ratio` 就发挥作用了。

试试这么操作吧

```bash
geektime ebook 49 --image-ratio=0.2
```

### 批量制作电子书

```bash
geektime ebook <course_ids>
```
上述命令可以批量制作电子书，参数 `course_ids` 表示课程ID 集合，课程ID 集合使用半角逗号 `,` 和 `-` 进行拼接，`all` 则表示全部已购买课程ID 集合
。例如：

- 制作48、49号课程电子书，可以执行 `geektime ebook 48,49`
- 制作48到50号课程电子书，可以执行 `geektime ebook 48-50`
- 制作所有已购买课程电子书，可以执行 `geektime ebook all`


### 更多用法

您也可以通过下边命令发现更多用法

```bash
geektime ebook --help
```



## 下载音频

`geektime-dl` 除了可以制作 Kindle 电子书，把极客时间装进 Kindle，还提供了课程音频下载、视频下载等附加功能，先来看下怎么保存课程视频吧。


> 执行该命令前，请确保账号密码已经保存在 `$(pwd)/geektime.cfg`。
>
> 如果没有，请执行 `geektime login` 进行账号密码验证和保存。

```bash
geektime mp3 <course_id> [--url-only]
```

这条命令会下载课程音频到 `$(pwd)/mp3/<课程名称>/` 中。
如果开启 `--url-only`，则只会保存音频链接到 `$(pwd)/mp3/<课程名称>/<课程名称>.mp3.txt`，不会下载音频文件。

您也可以通过以下命令获取更多帮助信息。

```bash
geektime mp3 --help
```

## 下载视频

> 执行该命令前，请确保账号密码已经保存在 `$(pwd)/geektime.cfg`。
>
> 如果没有，请执行 `geektime login` 进行账号密码验证和保存。

```bash
geektime mp4 <course_id> [--url-only] [--hd-only]
```

`geektime mp4` 会下载课程视频到 `$(pwd)/mp4/<课程名称>/` 中，开启 `--hd-only` 则会下载高清视频。开启 `--url-only`，则只会保存视频链接到 `$(pwd)/mp4/<课程名称>/<课程名称>.mp4.txt`，不会下载视频文件。

您也可以通过以下命令获取更多帮助信息。

```bash
geektime mp4 --help
```
