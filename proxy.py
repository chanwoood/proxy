import re
import requests
from bs4 import BeautifulSoup
import sqlite3
import random

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWeb"
    "Kit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
}


def crawl():
    conn = sqlite3.connect("proxy.db")
    cs = conn.cursor()
    cs.execute(
        """
		create table if not exists proxy (
			host varchar(20) primary key,
			port varchar(10),
			proto varchar (10)
		)
	"""
    )
    xici(conn, cs)
    cn(conn, cs)


def xici(conn, cs):
    try:
        rsp = requests.get("http://www.xicidaili.com/", headers=headers, timeout=15)
    except Exception:
        print("爬取西刺失败！")
        return

    soup = BeautifulSoup(rsp.text, "html.parser")
    for i in soup.find_all("tr", class_="subtitle"):
        i.decompose()

    trs = soup.find_all("tr", class_=re.compile(r"\s*"))
    for tr in trs:
        tds = tr.find_all("td")
        host = tds[1].text
        port = tds[2].text
        proto = tds[5].text
        if proto == "socks4/5":
            continue

        cs.execute(
            "insert or replace into proxy(host, port, proto) values (?, ?, ?)",
            (host, port, proto),
        )
        conn.commit()
    print("成功爬取西刺 !")


def cn(conn, cs):
    try:
        rsp = requests.get("http://cn-proxy.com/", headers=headers, timeout=15)
    except Exception:
        print("无法翻墙，爬取 cn-proxy 失败！")
        cs.close()
        conn.close()
        return

    soup = BeautifulSoup(rsp.text, "html.parser")

    for tbody in soup.find_all("tbody"):
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            host = tds[0].text
            port = tds[1].text
            cs.execute(
                "insert or replace into proxy (host, port, proto) values (?, ?, ?)",
                (host, port, "http"),
            )
            conn.commit()

    cs.close()
    conn.close()
    print("成功爬取 cn-proxy !")


def get():
    conn = sqlite3.connect("proxy.db")
    cs = conn.cursor()
    cs.execute("select * from proxy")
    record = random.choice(cs.fetchall())

    proxies = {
        proto: "{}://{}:{}".format(record[2], record[0], record[1])
        for proto in ["https", "http"]
    }

    try:
        r = requests.get("https://www.baidu.com/", proxies=proxies, timeout=15)
    except Exception:
        cs.execute("delete from proxy where host=?", (record[0],))
        conn.commit()
        return get()

    cs.close()
    conn.close()
    return proxies


if __name__ == "__main__":
    crawl()
