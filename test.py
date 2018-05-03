import requests
import proxy

rsp = requests.get('https://www.baidu.com/', proxies=proxy.get())
print(rsp.status_code)