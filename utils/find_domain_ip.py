import logging

import dns.resolver
import requests
from bs4 import BeautifulSoup

# 你想要使用的 DNS 服务器列表
dns_servers = None


def resolve_with_multiple_dns(domain, dns_servers=None, http="http"):
    if dns_servers is None:
        dns_servers = ['101.101.101.101', '1.1.1.1']
        dns_dict = {"taiwan": "101.101.101.101", "cloudflare":"1.1.1.1", "ali": "223.6.6.6", "onedns": "52.80.66.66",
                    "tencent": "119.29.29.29", "baidu": "180.76.76.76", "360": "101.226.4.6","cnnic": "1.2.4.8",
                    "google": "8.8.8.8",  "dns.sb":"185.222.222.222", "adguard": "94.140.14.14", "opendns": "208.67.222.222","ibm_quad9": "9.9.9.11"}
        dns_servers = dns_dict.values()
    print(f"DNS: {dns_servers}")
    ip_addresses = []
    for dns_server in dns_servers:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]  # 只使用当前 DNS 服务器
        resolver.lifetime = 5  # 设置超时时间
        try:
            # 尝试解析域名
            answers = resolver.resolve(domain, "A")
            for rdata in answers:
                ip_addresses.append(rdata.address)
                print(f"'{rdata.address}'", end=',')
            # ip_addresses.append("104.20.19.168")
        except Exception as e:
            logging.error(f"Failed to resolve {domain} using DNS {dns_server}: {e}")
    print()

    ip_addresses = list(set(ip_addresses))  # 转为集合去重，然后再转回列表
    # 测试解析到的 IP 地址是否可以访问
    for ip in ip_addresses:
        try:
            response = requests.get(f'{http}://{ip}/', headers={'Host': f'{domain}'}, verify=False, timeout=10)
            if response.status_code == 200:
                print(f"Successfully accessed {domain} via IP {ip}")

                # 解析 HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                print(f"\033[34m标题：{soup.find('title')}\033[0m")
            else:
                logging.error(f"Failed to access {domain} via IP {ip}, Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error accessing {domain} via IP {ip}: {e}")


# 查询 github.com
resolve_with_multiple_dns("github.com", dns_servers)
# resolve_with_multiple_dns("e-hentai.org", dns_servers, http="https")

# response = requests.get(f'https://104.20.19.168/', headers={'Host': f'e-hentai.org'}, verify=False, timeout=10)
