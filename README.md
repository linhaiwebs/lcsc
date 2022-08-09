## 运行环境
1. Python 版本：Python3.7
2. 以 lcsc 为目录创建虚拟环境

## 获取思路
###采取生产者消费者模式
1. 生产者根据类目id同步获取元件id 
2. 集合对(元件id, 类目名称)去重检测，```{"product_id": "x", "cate_name": "x", "cate_id": x}```进入```lcsc_product_id.json```
3. 消费者在```lcsc_product_id.json```中获取元件id进行异步爬取元件数据
4. 获取数据失败的元件id进入```fail_product_id.json```

## 开始前配置

### 修改config.yaml文件
可通过修改请求并发数进行提速，最好不超过15
```
# 异步请求并发数，默认5
CONCURRENT_REQUESTS: 5
# 异步请求等待时间下区间
REQUEST_SLEEP_TIME: 5  # 偏移3s为上区间
```

####上传到服务器

```
# 上传到服务器
UPLOAD_TO_SERVER: True
```

####可支持存储在json文件
1. SAVE_PATH自定义路径
```
# 保存product_id在json文件
SAVE_PATH: './data'
```

####可支持存储在mysql
1. SAVE_TO_DATABASE取True
2. 填入数据库信息
```
# 是否保存在mysql
SAVE_TO_DATABASE: True
DATABASE_SETTING:
  DATABASE_HOST: 'localhost'
  DATABASE_PORT: 3306
  DATABASE_USER: 'root'
  DATABASE_PASSWORD: '******'
  DATABASE_DB: 'xxx'
```

####支持邮件发送报错信息
1. SENT_EMAIL取True
2. 在发送人qq邮箱设置开启SMTP: qq邮箱-->设置-->账户 开启SMTP
3. 收件人，以 , 为间隔的str
4. 可通过运行 ```python3 test_send_email.py``` 测试SMTP
```
# 是否发送报错邮件
SENT_EMAIL: False
EMAIL_SETTING:
  # 发送人qq邮箱
  FROM_ADDR: 'xxx@qq.com'
  # 发送人SMTP授权码，qq邮箱-->设置-->账户 开启SMTP
  PASSWORD: '******'
  # 邮箱服务器，写死
  SMTP_HOST: 'smtp.qq.com'
  # 收件人，以 , 为间隔的str
  RECEIVE_LIST: 'xxx@qq.com, xxx@qq.com'
```

### 安装依赖库
使用以下命令来安装依赖文件
```
pip install -r requirement.txt
```

## 运行程序

###获取元件id并存储
使用命令 ```python3 product_id_main.py``` 启动程序，启动后将看到以下内容：
```shell
类目进度:   0%|          | 0/504 [00:00<?, ?it/s]2022-07-11 22:16:26,903 | INFO | 128 | first cate --> {'cate_name': '电容/电阻/电感', 'cate_id': 1, 'parent_id': 0}
2022-07-11 22:16:26,904 | INFO | 131 | second cate --> {'cate_name': '电容', 'cate_id': 312, 'parent_id': 1}
2022-07-11 22:16:26,904 | INFO | 133 | start crawl {'cate_name': '牛角型电解电容', 'cate_id': 11182, 'parent_id': 312}
2022-07-11 22:16:28,153 | INFO | 30 | save to json success!!!
2022-07-11 22:16:28,154 | INFO | 30 | save to json success!!!
2022-07-11 22:16:28,155 | INFO | 30 | save to json success!!!
2022-07-11 22:16:28,155 | INFO | 30 | save to json success!!!
2022-07-11 22:16:28,156 | INFO | 30 | save to json success!!!
2022-07-11 22:16:28,162 | INFO | 30 | save to json success!!!
2022-07-11 22:16:28,163 | INFO | 30 | save to json success!!!
```

###获取元件数据并上传
使用命令 ```python3 product_data_main.py``` 启动程序，启动后将看到以下内容：
```shell
2022-07-11 22:39:03,427 | INFO | 153 | upload to server success!!!
2022-07-11 22:39:03,427 | INFO | 180 | success total num: 1 --> {'product_id': '238430', 'cate_name': '牛角型电解电容', 'cate_id': 11182}
2022-07-11 22:39:04,674 | INFO | 153 | upload to server success!!!
2022-07-11 22:39:04,674 | INFO | 180 | success total num: 2 --> {'product_id': '387937', 'cate_name': '牛角型电解电容', 'cate_id': 11182}
2022-07-11 22:39:05,035 | INFO | 153 | upload to server success!!!
2022-07-11 22:39:05,036 | INFO | 180 | success total num: 3 --> {'product_id': '47454', 'cate_name': '牛角型电解电容', 'cate_id': 11182}
2022-07-11 22:39:05,677 | INFO | 153 | upload to server success!!!
2022-07-11 22:39:05,677 | INFO | 180 | success total num: 4 --> {'product_id': '430166', 'cate_name': '牛角型电解电容', 'cate_id': 11182}
2022-07-11 22:39:06,667 | INFO | 153 | upload to server success!!!
2022-07-11 22:39:06,667 | INFO | 180 | success total num: 5 --> {'product_id': '107652', 'cate_name': '牛角型电解电容', 'cate_id': 11182}
```


## 日志检查
###在logs文件夹检查每天的日志记录
1. ```get_id_log``` 获取元件id的日志
2. ```get_data_log``` 获取元件数据的日志
3. ```request``` 请求日志

