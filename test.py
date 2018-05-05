import requests
import proxy


try:
    rsp = requests.get("https://www.baidu.com/", proxies=proxy.get(), timeout=15)
except Exception:
    pass
else:
    print(rsp.status_code)
