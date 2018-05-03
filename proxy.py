import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import sqlite3
import random

import socket 
socket.setdefaulttimeout(15)

def crawl():
	conn = sqlite3.connect('proxy.db')
	cs = conn.cursor()
	cs.execute('''
		create table if not exists proxy (
			host varchar(20),
			port varchar(10),
			proto varchar (10),
			unique(host, port, proto)
		)
	''')
	xici(conn, cs)
	cn(conn, cs)

def xici(conn, cs):
	
	ua = UserAgent().random
	headers = {'user-agent': ua}
	rsp = requests.get('http://www.xicidaili.com/', headers=headers)
	if rsp.status_code == 200:
		print("成功爬取西刺 !")
	
	soup = BeautifulSoup(rsp.text, 'html.parser')
	for i in soup.find_all('tr', class_="subtitle"):
		i.decompose()
		
	trs = soup.find_all('tr', class_=re.compile(r'\s*'))
	for tr in trs:
		tds = tr.find_all('td')
		host = tds[1].text
		port = tds[2].text
		proto = tds[5].text
		if proto == 'socks4/5':
			continue
		cs.execute('insert or ignore into proxy(host, port, proto) values (?, ?, ?)',
			(host, port, proto))
		conn.commit()
	
	
def cn(conn, cs):
	ua = UserAgent().random
	headers = {"user-agent": ua}
	try:
		r = requests.get("http://cn-proxy.com/", headers=headers, timeout=15)
	except Exception:
		print('无法翻墙，爬取 cn-proxy 失败！')
		cs.close()
		conn.close()
		return

	if r.status_code == 200:
		print("成功爬取 cn-proxy !")

	soup = BeautifulSoup(r.text, "html.parser")

	for tbody in soup.find_all("tbody"):
		for tr in tbody.find_all("tr"):
			tds = tr.find_all("td")
			host = tds[0].text
			port = tds[1].text
			cs.execute(
				"insert or ignore into proxy (host, port, proto) values (?, ?, ?)", (host, port, 'http')
			)
			conn.commit()

	cs.close()
	conn.close()

	
def get():
	conn = sqlite3.connect("proxy.db")
	cs = conn.cursor()
	cs.execute("select * from proxy")
	record = random.choice(cs.fetchall())

	proxies = {
		"http": "{}://{}:{}".format(record[2], record[0], record[1]),
		"https": "{}://{}:{}".format(record[2], record[0], record[1]),
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
	
if __name__ == '__main__':
	crawl()