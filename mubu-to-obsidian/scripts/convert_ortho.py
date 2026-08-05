#!/usr/bin/env python3
"""
将幕布导出的 HTML 转换为 Obsidian Markdown 格式（骨科疾病专用）
"""
import os
import re
import sys
import urllib.request
from bs4 import BeautifulSoup, NavigableString, Tag

# ========== 配置 ==========
html_path = "/Users/masongqi/Documents/📑骨科疾病-执业医.html"
output_dir = "/Users/masongqi/Library/Mobile Documents/iCloud~md~obsidian/Documents/医学"
base_name = "骨科疾病"
image_dir_name = base_name
image_dir = os.path.join(output_dir, image_dir_name)

os.makedirs(image_dir, exist_ok=True)

# ========== 读取 HTML ==========
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

title_div = soup.find('div', class_='title')
title = title_div.get_text(strip=True) if title_div else base_name

# ========== 图片下载 ==========
image_urls = set()
for img in soup.find_all('img'):
    src = img.get('src', '')
    if src and 'mubu.com' in src:
        image_urls.add(src)

print(f"找到 {len(image_urls)} 个唯一图片链接")

url_to_filename = {}
for idx, url in enumerate(sorted(image_urls)):
    # 从 URL 中提取文件名，或者用序号命名
    match = re.search(r'(\d+_[a-f0-9-]+\.png)', url)
    if match:
        filename = match.group(1)
    else:
        filename = url.split('/')[-1].split('?')[0]
        if not filename.endswith('.png'):
            # 用序号命名
            filename = f"image_{idx+1:03d}.png"

    local_path = os.path.join(image_dir, filename)
    url_to_filename[url] = filename

    if os.path.exists(local_path):
        print(f"  跳过已存在: {filename}")
        continue

    try:
        print(f"  下载: {filename} ...", end=' ', flush=True)
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(local_path, 'wb') as f:
                f.write(resp.read())
        print("OK")
    except Exception as e:
        print(f"失败: {e}")

print(f"图片准备完成")

# ========== 解析内容 ==========
def extract_text_with_formatting(content_div):
    """
    提取文本，保留格式。关键修复：嵌套的 bold/underline 不再产生双重 **
    """
    result = []

    def get_inline_text(node):
        """提取节点的纯文本（用于判断内容是否为空）"""
        if isinstance(node, NavigableString):
            return str(node).strip()
        if isinstance(node, Tag):
            return ''.join(get_inline_text(c) for c in node.children)
        return ''

    def walk(node, inherited_bold=False, inherited_highlight=False):
        """
        递归提取文本
        inherited_bold: 父级已经加了 **，子级不再重复添加
        inherited_highlight: 父级已经加了 ==，子级不再重复添加
        """
        if isinstance(node, NavigableString):
            result.append(str(node))
            return

        if not isinstance(node, Tag):
            return

        classes = node.get('class', [])

        if node.name == 'span':
            is_bold = 'bold' in classes or 'Bold' in classes
            is_underline = 'underline' in classes
            is_red = 'text-color-red' in classes
            is_highlight = 'highlight-yellow' in classes or 'highlight' in classes

            # 红色和黄色高亮 → ==文字==（Obsidian 高亮）
            should_highlight = (is_red or is_highlight) and not inherited_highlight
            # 粗体和下划线 → **文字**
            should_bold = (is_bold or is_underline) and not inherited_bold

            if should_highlight:
                result.append('==')
            if should_bold:
                result.append('**')

            for child in node.children:
                walk(child,
                     inherited_bold or is_bold or is_underline,
                     inherited_highlight or is_red or is_highlight)

            if should_bold:
                result.append('**')
            if should_highlight:
                result.append('==')
        elif node.name == 'br':
            result.append('\n')
        else:
            for child in node.children:
                walk(child, inherited_bold, inherited_highlight)

    walk(content_div, False, False)
    # 清理
    text = ''.join(result).strip()
    # 修复 &#x20; 等 HTML 实体
    text = text.replace('&#x20;', ' ')
    # 清理多余空白
    text = re.sub(r' {2,}', ' ', text)
    # 合并相邻的同类型标记：**A****B** -> **AB**；==A====B== -> ==AB==
    while True:
        new_text = re.sub(r'\*\*([^*]+)\*\*\*\*([^*]+)\*\*', r'**\1\2**', text)
        if new_text != text:
            text = new_text
            continue
        new_text = re.sub(r'==([^=]+)====([^=]+)==', r'==\1\2==', text)
        if new_text == text:
            break
        text = new_text
    return text


def parse_node_list(ul_element):
    """解析 ul.node-list"""
    if ul_element is None:
        return []

    lines = []
    for li in ul_element.find_all('li', class_='node', recursive=False):
        # 提取内容文本
        content_div = li.find('div', class_='content')
        text = ''
        if content_div:
            text = extract_text_with_formatting(content_div)

        # 提取图片 - 只取直接子级的 image-list（recursive=False 关键修复）
        image_ul = li.find('ul', class_='image-list', recursive=False)
        images = []
        if image_ul:
            for img in image_ul.find_all('img'):
                src = img.get('src', '')
                if src in url_to_filename:
                    images.append(url_to_filename[src])

        # 递归提取子节点
        children_div = li.find('div', class_='children')
        children = []
        if children_div:
            child_ul = children_div.find('ul', class_='node-list')
            if child_ul:
                children = parse_node_list(child_ul)

        lines.append({
            'text': text,
            'images': images,
            'children': children
        })

    return lines


def render_markdown(node_list, depth=0):
    """渲染为 markdown（用 tab 缩进）"""
    indent = '\t' * depth
    result = []

    for node in node_list:
        text = node['text']
        images = node['images']
        children = node['children']

        # 写文本行
        if text:
            result.append(f"{indent}- {text}")

        # 写图片
        for img_file in images:
            if text:
                # 如果有文本，图片比文本多缩进一级
                result.append(f"{indent}\t- ![[{image_dir_name}/{img_file}]]")
            else:
                # 如果没有文本，图片在当前层级
                result.append(f"{indent}- ![[{image_dir_name}/{img_file}]]")

        # 写子节点（递归）
        if children:
            child_lines = render_markdown(children, depth + 1)
            result.extend(child_lines)

    return result


# ========== 解析 ==========
root_ul = soup.find('ul', class_='node-list')
if root_ul is None:
    print("错误: 未找到 node-list")
    sys.exit(1)

parsed = parse_node_list(root_ul)
md_lines = render_markdown(parsed, depth=0)

output_path = os.path.join(output_dir, f"{base_name}.md")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines) + '\n')

print(f"\nMarkdown 已保存到: {output_path}")
print(f"共 {len(md_lines)} 行")
print(f"图片文件夹: {image_dir}")
