# 爬取代理并存储

爬取 [http://www.xicidaili.com/](http://www.xicidaili.com/) 和 [http://cn-proxy.com/](http://cn-proxy.com/) 代理并用 sqlite3 存储，其中 cn-proxy 需翻墙。

## 用法

- 安装依赖：pip install requests bs4

- 更新脚本：python proxy.py

- 从数据库中获取代理，示例：
```python
  import proxy # proxy.py 在当前执行路径下
  
  requests.get('https://www.baidu.com/', proxies=proxy.get())
```

## 特色

- 每次获取代理时，先检查代理是否可用，不可用则从数据库中删除，重新获取直至可用。
- 更新代理时，不插入已存在的代理，不重复创建表。
- 自动判断网络环境，若不能翻墙则只爬取西刺代理。
- 用 Python 自带的 sqlite3 存储，简单，方便。