---
name: novel-downloader
description: 下载网络小说全文到本地 TXT/EPUB。支持番茄小说（免登录）、起点中文网（需 cookie）及约 90 个笔趣阁镜像站（覆盖七猫等平台的连载书），可跨站搜索书名定位书籍。当用户需要下载某本小说、抓取小说全文、把在线小说导出为电子书、或对小说网站内容做离线保存时使用。
---

# novel-downloader

基于 `saudadez21/novel-downloader`（PyPI `novel-downloader`，MIT）的多站下载封装，无交互命令行，支持搜索、下载、导出。

## 底层与依赖

- 后端：`novel-downloader` Python 包（需要 Python 3.11+，本机用 python3.12）
- venv：`~/tools/novel-downloader/.venv/`
- 包装脚本：本文件同目录 `nb_dl.py`
- 配置文件：本文件同目录 `settings.toml`（数据目录在 `~/tools/novel-downloader/data/`）

## 站点覆盖

| 站点 | 标识符 | 说明 |
| --- | --- | --- |
| 番茄小说 | `fanqienovel` | 免登录直接下载，支持按书 ID / 书籍页 URL |
| 起点中文网 | `qidian` | 需要登录 cookie（配置见下），支持搜索 |
| 笔趣阁镜像 | `shuhaige`/`n71ge`/`biquguo`/`quanben5`/`n23qb`/`yibige` 等约 90 个 | 覆盖七猫、起点老书等在镜像站有收录的书籍 |

> 不同镜像站覆盖面不同：老书（如《盘龙》）用 `shuhaige`、`quanben5`；七猫连载新书多用 `n71ge`、`biquguo`、`shuhaige`。单站找不到时用 `search` 跨站找，命中后直接拿书 ID 下载。

> **下载速度差异大**：`shuhaige` 快（实测约 120 章/分钟），`n71ge` 慢（约 35 章/分钟）。同一本书多个镜像站有收录时，优先选 `shuhaige`。整本千章级书 10-20 分钟，建议后台跑。

## 用法

### 1. 跨站搜索（推荐先做这步）

```bash
~/tools/novel-downloader/.venv/bin/python ~/.agents/skills/novel-downloader/nb_dl.py search "<书名>" [-l 20]
```

返回各站命中结果，格式 `[站点] 书名 | 作者 | id=xxx | 书籍页URL`。搜索过程部分镜像站会报 `Failed to fetch HTML`，属正常（那些站抓取失败），不影响其他站的命中。

### 2. 下载并导出

```bash
~/tools/novel-downloader/.venv/bin/python ~/.agents/skills/novel-downloader/nb_dl.py download <site> <book_id或URL> \
  --format txt|epub|both \
  --out <输出目录>
```

- `<site>` 传 `auto` 且 target 传书籍页 URL 时自动识别站点
- 例：`download shuhaige 67304 --format both --out ~/Downloads/小说`
- 例：`download auto https://fanqienovel.com/page/7276384138653862966 --format epub`

### 3. 仅导出已下载缓存

```bash
... download <site> <book_id> --export-only --out <输出目录>
```

已下载章节缓存在 `~/tools/novel-downloader/data/raw/<site>/<id>/`，重下同一本书秒级完成（走缓存）。

## 起点 cookie 配置

起点免费章节也需要登录。在 `settings.toml` 的 `[sites.qidian]` 下添加：

```toml
[sites.qidian]
login_required = true
cookie = "浏览器登录后复制的完整 Cookie 字符串"
```

获取方式：浏览器登录 qidian.com → F12 开发者工具 → Network → 任意请求的 Request Headers → 复制 Cookie 全文。

## 已知限制

- **付费章节（实测结论）**：主走镜像站时付费书也能拿完整全本。实测《诡秘之主》（起点付费大热书）1422章全本下载成功，《盘龙》827章全本成功。起点直连（`qidian`）才受付费限制（`fetch_inaccessible=false` 只下免费章），但日常不需要走直连。
- **已落地成品（本机 `data/downloads/`）**：《诡秘之主》1422 章 13MB、《盘龙》827 章 8.2MB，均 shuhaige 源。已按同名 raw 缓存，重导秒级完成。新书下载建议先 `search` 跨站找 shuhaige 收录，`download shuhaige <id> --format txt --out ~/tools/novel-downloader/data/downloads`。
- 镜像站有反爬，偶发请求失败会自动重试（默认 3 次）；千章级整本 10-20 分钟，建议后台运行。
- 镜像站覆盖面不一：部分冷门老书可能所有站都无收录，此时如实告知用户搜不到，不强行编造。
- 版权提示：起点/番茄为正版付费平台，下载仅限个人阅读；笔趣阁等镜像站为盗版转载，使用注意合规风险。
