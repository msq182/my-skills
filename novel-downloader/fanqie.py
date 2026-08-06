#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""无交互包装 fanqienovel-downloader，供 skill 调用。

修复了上游两个问题：
1. _init_cookie 的暴力猜 cookie 循环（首次无 cookie.json 时会卡死）——
   改为用 Session 先访问目录页建立会话，跳过 cookie 猜测。
2. 旧 Chrome/93 UA 与 curl_cffi impersonate 指纹冲突会被风控拦截——
   改用 Mozilla/5.0 让 curl_cffi 自己管理指纹。

用法：
  fanqie.py search "<关键词>"                          # 搜索，打印 id/书名/作者/字数
  fanqie.py download "<id 或目录页链接>" --out <目录> [--format txt|epub|both] [--split] [--threads N]
"""
import argparse
import json
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "../../../tools/fanqienovel-downloader/src")
sys.path.insert(0, BASE)

import main
from main import Config, NovelDownloader, SaveMode


def build_downloader(threads: int, out_dir: str, save_mode: SaveMode) -> NovelDownloader:
    cfg = Config()
    cfg.xc = threads
    cfg.save_path = out_dir
    cfg.save_mode = save_mode
    os.makedirs(out_dir, exist_ok=True)

    session = __import__("curl_cffi.requests", fromlist=["Session"]).Session(impersonate="chrome")
    session.get("https://fanqienovel.com/page/7143038691944959011", timeout=15)
    main.req = session

    d = NovelDownloader.__new__(NovelDownloader)
    d.config = cfg
    d.headers_lib = [{"User-Agent": "Mozilla/5.0"}]
    d.headers = d.headers_lib[0].copy()
    d.script_dir = BASE
    d.data_dir = os.path.join(BASE, "data")
    d.bookstore_dir = os.path.join(BASE, "data", "bookstore")
    d.record_path = os.path.join(BASE, "data", "record.json")
    d.config_path = os.path.join(BASE, "data", "config.json")
    d.cookie_path = os.path.join(BASE, "data", "cookie.json")
    with open(os.path.join(BASE, "charset.json"), encoding="utf-8") as f:
        d.charset = json.load(f)
    os.makedirs(d.bookstore_dir, exist_ok=True)
    d.cookie = ""
    d.log_callback = lambda *a, **k: None
    d.progress_callback = lambda *a, **k: None
    d.verbose = bool(os.environ.get("FANQIE_VERBOSE"))
    d.zj = {}
    d.cs = 0
    d.tcs = 0
    d.tzj = None
    d.book_json_path = None
    d.CODE = [[58344, 58715], [58345, 58716]]
    return d


def cleanup_metadata_txt(path: str) -> None:
    """去掉 _save_single_txt 误写入的 _metadata 段首行与 metadata dict 行。"""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip() == "_metadata":
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("{'"):
                lines = lines[:i] + lines[i + 2:]
            else:
                lines = lines[:i] + lines[i + 1:]
            break
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def do_search(keyword: str) -> int:
    d = build_downloader(4, os.getcwd(), SaveMode.SINGLE_TXT)
    d.log_callback = lambda *a, **k: None if not d.verbose else print(*a)
    results = d.search_novel(keyword)
    if not results:
        print("NO_RESULT")
        return 0
    for i, book in enumerate(results):
        b = book["book_data"][0]
        print(f"{i + 1}. {b['book_name']} | 作者: {b['author']} | 字数: {b['word_number']} | ID: {b['book_id']}")
    return 0


def do_download(novel_id: str, out_dir: str, fmt: str, split: bool, threads: int) -> int:
    rc = 0
    if fmt in ("txt", "both"):
        st = _download_with_retry(novel_id, out_dir, threads,
                                  SaveMode.SPLIT_TXT if split else SaveMode.SINGLE_TXT,
                                  "_download_txt")
        print(f"TXT_RESULT:{st}")
        if st != "err":
            cleanup_metadata_txt(_find_output(out_dir, ".txt"))
        else:
            rc = 1
    if fmt in ("epub", "both"):
        st = _download_with_retry(novel_id, out_dir, threads, SaveMode.SINGLE_TXT, "_download_epub")
        print(f"EPUB_RESULT:{st}")
        if st == "err":
            rc = 1
    return rc


def _download_with_retry(novel_id: str, out_dir: str, threads: int, mode: SaveMode, method: str) -> str:
    """风控会导致目录页偶发解析失败（'err'），重试最多 3 次。已有缓存章节会自动复用。"""
    import time
    for attempt in range(1, 4):
        d = build_downloader(threads, out_dir, mode)
        st = getattr(d, method)(novel_id)
        if st != "err":
            return st
        print(f"[retry] {method} attempt {attempt} failed (wind-control), retrying...")
        time.sleep(3)
    return "err"


def _find_output(out_dir: str, ext: str) -> str:
    for name in os.listdir(out_dir):
        if name.endswith(ext):
            return os.path.join(out_dir, name)
    raise FileNotFoundError(f"no {ext} file in {out_dir}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search")
    p_search.add_argument("keyword")

    p_dl = sub.add_parser("download")
    p_dl.add_argument("novel_id")
    p_dl.add_argument("--out", default=os.path.expanduser("~/Downloads/novels"))
    p_dl.add_argument("--format", choices=["txt", "epub", "both"], default="both")
    p_dl.add_argument("--split", action="store_true")
    p_dl.add_argument("--threads", type=int, default=16)

    args = parser.parse_args()
    if args.cmd == "search":
        sys.exit(do_search(args.keyword))
    sys.exit(do_download(args.novel_id, args.out, args.format, args.split, args.threads))


if __name__ == "__main__":
    main()
