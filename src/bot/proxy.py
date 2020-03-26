import json
import os
import random
import string
import requests
from bot.proxylist import ProxyList
from bs4 import BeautifulSoup
import base64

IFCONFIG_CANDIDATES = (
    "https://api.ipify.org/?format=text", "https://myexternalip.com/raw", "https://wtfismyip.com/text",
    "https://icanhazip.com/", "https://ipv4bot.whatismyipaddress.com/", "https://ip4.seeip.org")
TIMEOUT = 10
USER_AGENT = "curl/7.{curl_minor}.{curl_revision} (x86_64-pc-linux-gnu) libcurl/7.{curl_minor}.{curl_revision} OpenSSL/0.9.8{openssl_revision} zlib/1.2.{zlib_revision}".format(
    curl_minor=random.randint(8, 22), curl_revision=random.randint(1, 9),
    openssl_revision=random.choice(string.ascii_lowercase), zlib_revision=random.randint(2, 6))


def get_proxy():
    result = return_proxy(max_count=0)
    if not result["port"] is None:
        return result


    funs = [
        lambda: fetch_proxies_getproxylist(),
        lambda: fetch_proxies_pubproxy(),
        lambda: fetch_proxies_free_proxy_cz()
    ]
    random.shuffle(funs)

    funs += [lambda: fetch_proxies_github()]

    for fun in funs:
        proxies = filter_valid(filter_duplicates(fun()))
        if len(proxies) <= 0:
            continue

        ProxyList.proxy_list = proxies + ProxyList.proxy_list

        result = return_proxy()
        if not result["port"] is None:
            return result

    return {'ip': None, 'port': None}

def return_proxy(max_count=-1):
    result = {'ip': None, 'port': None}
    for i in range(len(ProxyList.proxy_list)):
        proxy = ProxyList.proxy_list.pop(0)
        if is_proxy_valid(proxy) and (max_count < 0 or proxy['count'] <= max_count):
            proxy['count'] += 1
            ProxyList.proxy_list += [proxy]
            ProxyList.proxy_list.sort(key=lambda p: p['count'])

            print("ProxyList.proxy_list: %s" % ProxyList.proxy_list)
            result = proxy
            break
    return result


def is_proxy_valid(proxy):
    try:
        ifconfig = random_ifconfig()
        response = requests.get(ifconfig)
        if os.environ.get('DEBUG', 'False') == 'True':
            print("we are online on: %s" % ifconfig)
        candidate = "https://%s:%s" % (proxy["ip"], proxy["port"])
        response = requests.get(ifconfig, proxies={"https": candidate}, timeout=10)
    except Exception as e:
        print("Proxy not valid: %s" % proxy)
        print(e)
        return False

    return True


def get_unused_proxies():
    try:
        contents = requests.get("http://pubproxy.com/api/proxy?country=DE&https=true&type=http&limit=5", timeout=10)
        j = json.loads(contents.text)
        proxies = j['data']

        if os.environ.get('DEBUG', 'False') == 'True':
            print("fetch_proxies_pubproxy: %s" % proxies)
        results = list(map(lambda proxy: {"ip": proxy["ip"], "port": int(proxy["port"]), "count": 0}, proxies))
        return results
    except Exception as e:
        print(e)
        return list()

def fetch_proxies_pubproxy():
    try:
        contents = requests.get("http://pubproxy.com/api/proxy?country=DE&https=true&type=http&limit=5", timeout=10)
        j = json.loads(contents.text)
        proxies = j['data']

        if os.environ.get('DEBUG', 'False') == 'True':
            print("fetch_proxies_pubproxy: %s" % proxies)
        results = list(map(lambda proxy: {"ip": proxy["ip"], "port": int(proxy["port"]), "count": 0}, proxies))
        return results
    except Exception as e:
        print(e)
        return list()

def fetch_proxies_getproxylist():
    try:
        contents = requests.get("https://api.getproxylist.com/proxy?country[]=DE&protocol[]=http&allowsHttps=1", timeout=10)
        j = json.loads(contents.text)
        proxies = [j]

        if os.environ.get('DEBUG', 'False') == 'True':
            print("fetch_proxies_getproxylist: %s" % proxies)
        results = list(map(lambda proxy: {"ip": proxy["ip"], "port": int(proxy["port"]), "count": 0}, proxies))
        return results
    except Exception as e:
        print(e)
        return list()


def fetch_proxies_github():
    try:
        contents = requests.get("https://raw.githubusercontent.com/stamparm/aux/master/fetch-some-list.txt", timeout=10)
        j = json.loads(contents.text)
        proxies = list(filter(lambda p: p['country'] == 'Germany' and p['proto'] == 'http', j))

        if os.environ.get('DEBUG', 'False') == 'True':
            print("fetch_proxies_github: %s" % proxies)
        results = list(map(lambda proxy: {"ip": proxy["ip"], "port": int(proxy["port"]), "count": 0}, proxies))
        random.shuffle(results)
        return results
    except Exception as e:
        print(e)
        return list()


def fetch_proxies_free_proxy_cz():
    try:
        contents = requests.get("http://free-proxy.cz/en/proxylist/country/DE/https/ping/all", timeout=10)
        soup = BeautifulSoup(contents.text, "html.parser")

        soup_ips = soup.select("#proxy_list > tbody:nth-child(2) > tr > td:nth-child(1)")
        ips = list(map(lambda s: decode_soup(s), soup_ips))
        ips_filtered = list(filter(lambda s: not s == "", ips))

        soup_ports = soup.select("#proxy_list > tbody:nth-child(2) > tr > td:nth-child(2)")
        ports = list(map(lambda s: s.text, soup_ports))

        results = []
        for i in range(len(ips_filtered)):
            results += [{"ip": ips_filtered[i], "port": int(ports[i]), "count": 0}]

        print("fetch_proxies_free_proxy_cz: %s" % results)

        random.shuffle(results)
        return results
    except Exception as e:
        print(e)
        return list()


def decode_soup(s):
    try:
        text = s.text
        encoded_str = text.split('"')[1]
        decoded_bytes = base64.b64decode(encoded_str)
        decoded_str = str(decoded_bytes, "utf-8")

        return decoded_str
    except:
        return ""


def filter_duplicates(proxies):
    filtered = list(filter(lambda r: not in_proxy_list(r), proxies))
    return filtered


def filter_valid(proxies):
    filtered = list(filter(lambda p: is_proxy_valid(p), proxies))
    return filtered


def in_proxy_list(r={'ip': None}):
    return list(filter(lambda p: r["ip"] == p["ip"], ProxyList.proxy_list))


def random_ifconfig():
    retval = random.sample(IFCONFIG_CANDIDATES, 1)[0]
    return retval
