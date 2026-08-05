#!/usr/bin/env python3
"""
重试下载超时的图片
"""
import os
import re
import urllib.request

html_path = "/Users/masongqi/Documents/📑骨科疾病-执业医.html"
output_dir = "/Users/masongqi/Library/Mobile Documents/iCloud~md~obsidian/Documents/医学"
image_dir = os.path.join(output_dir, "骨科疾病")

# 要重试的图片 URL（从输出中看到的那个超时的）
# 先读取 HTML 找到对应的 URL
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 找所有图片
pattern = r'src="(https?://[^"]*18715592_1320b0ff-2cfe-448b-f497-a15b5fae1487\.png[^"]*)"'
match = re.search(pattern, html)
if match:
    url = match.group(1)
    filename = "18715592_1320b0ff-2cfe-448b-f497-a15b5fae1487.png"
    local_path = os.path.join(image_dir, filename)

    if os.path.exists(local_path):
        print(f"{filename} 已存在，跳过")
    else:
        print(f"重试下载: {filename}")
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(local_path, 'wb') as f:
                    f.write(resp.read())
            print("OK")
        except Exception as e:
            print(f"还是失败: {e}")
else:
    print("未在 HTML 中找到该图片 URL")

# 再检查所有图片，看看有没有其他缺失的
print("\n检查图片完整性...")
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

missing = []
for img in soup.find_all('img'):
    src = img.get('src', '')
    if src and 'mubu.com' in src:
        match = re.search(r'(\d+_[a-f0-9-]+\.png)', src)
        if match:
            filename = match.group(1)
        else:
            filename = src.split('/')[-1].split('?')[0]
            if not filename.endswith('.png'):
                continue
        local_path = os.path.join(image_dir, filename)
        if not os.path.exists(local_path):
            missing.append((filename, src))

if missing:
    print(f"还有 {len(missing)} 个图片缺失:")
    for fn, url in missing:
        print(f"  - {fn}")
        # 尝试下载
        local_path = os.path.join(image_dir, fn)
        try:
            print(f"    下载中...", end=' ', flush=True)
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(local_path, 'wb') as f:
                    f.write(resp.read())
            print("OK")
        except Exception as e:
            print(f"失败: {e}")
else:
    print("所有图片都已下载！")
