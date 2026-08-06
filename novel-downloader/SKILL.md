---
name: novel-downloader
description: 下载网络小说全文（支持番茄小说等站点）到本地 TXT/EPUB。当用户需要下载某本小说、抓取小说全文、把在线小说导出为电子书、或者对小说网站内容做离线保存时使用。
---

# novel-downloader

基于 `ying-ck/fanqienovel-downloader`（AGPL-3.0）的本地封装，修复了上游两个会导致失败的问题后，用无交互命令行方式下载网络小说全文。

## 底层位置

- 工具源码：`~/tools/fanqienovel-downloader/`（git clone 的上游仓库）
- venv：`~/tools/fanqienovel-downloader/.venv/`
- 包装脚本：本文件同目录 `fanqie.py`

## 修复记录（重要，勿回退）

上游 `main.py` 在当前环境下有两个问题，`fanqie.py` 已规避：

1. **`_init_cookie` 暴力猜 cookie 循环会卡死**：`_get_new_cookie()` 在 `range(6e18, 9e18)` 里随机尝试 `novel_web_id`，首次无 `data/cookie.json` 时会长时间空转。修复：`build_downloader()` 里用 `curl_cffi.Session` 先访问一次目录页建立会话，然后 `main.req = session`，cookie 置空，跳过整个 cookie 猜测流程。
2. **旧 Chrome/93 UA 被风控**：上游 `headers_lib` 用的 UA 与 curl_cffi 的 `impersonate="chrome"` 指纹不一致会被拦截（返回空正文）。修复：把 `headers_lib` 改为 `Mozilla/5.0`，让 curl_cffi 自己管理 TLS 指纹。

注意：构建 downloader 用了 `NovelDownloader.__new__` + 手动补属性，绕过 `__init__`（因为它会触发 `_init_cookie`）。**属性清单必须补全**（`CODE`、`charset`、`headers_lib`、`config`、`data_dir` 系列、`zj/cs/tcs/tzj/book_json_path`），否则运行时报 AttributeError。

## 用法

### 搜索书籍

```bash
~/tools/fanqienovel-downloader/.venv/bin/python ~/.agents/skills/novel-downloader/fanqie.py search "<关键词>"
```

> ⚠️ 搜索 API（`api5-normal-lf.fqnovel.com/reading/bookapi/search`）当前返回 `PARAM_INVALID`，**搜索功能基本不可用**。核心下载不受影响：直接用书籍 ID 或目录页链接即可。

### 下载整本小说

```bash
~/tools/fanqienovel-downloader/.venv/bin/python ~/.agents/skills/novel-downloader/fanqie.py download "<书籍ID 或 目录页完整链接>" \
  --out <输出目录> \
  --format txt|epub|both   # 默认 both
  --split                  # 分章保存为多文件（默认整本一个 txt）
  --threads 16             # 并发线程数
```

- 默认输出目录：`~/Downloads/novels/`
- 书籍 ID 可从番茄小说网页版目录页 URL 提取：`https://fanqienovel.com/page/<ID>`，也可直接传完整链接。

### 输出产物

- `--format txt`：整本 `《书名》.txt`（`--split` 则按章存目录）
- `--format epub`：`《书名》.epub`，含作者、封面、目录导航
- 中途缓存：`~/tools/fanqienovel-downloader/src/data/bookstore/<书名>.json`（章节级断点续传数据）

## 注意事项

- **风控随机失败**：请求偶发返回空正文导致某章失败或 EPUB/TXT 整本 `err`。wrapper 已对整本下载加 3 次自动重试（`_download_with_retry`），已有缓存章节会自动复用；重试仍失败时再手动重跑。下载超大书籍（千章级）耗时可达 20-30 分钟，**应后台运行并轮询**，不要同步等待。
- 输出 TXT 时 `fanqie.py` 会自动清理上游 `_save_single_txt` 误写入正文头部的 `_metadata` 段。
- 首次运行会自动创建 `~/tools/fanqienovel-downloader/src/data/`。
- 免责：仅供个人学习与阅读使用，抓取付费/VIP 内容有版权风险，请自行斟酌。
