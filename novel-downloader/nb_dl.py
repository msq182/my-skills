#!/usr/bin/env python3
"""
novel-downloader skill 的多站无交互包装脚本。

底层：saudadez21/novel-downloader (PyPI `novel-downloader`, MIT)
支持站点：番茄 fanqienovel、起点 qidian(需 cookie)、约 90 个笔趣阁镜像站。
子命令：
  search <关键词> [-s site] [-l limit]    多站搜索书籍
  download <site> <book_id|URL> [--format txt|epub|both] [--out DIR]
                                           下载并导出书籍
  仅导出已下载书籍：download 带 --export-only
"""

import argparse
import asyncio
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
CONFIG = BASE / "settings.toml"

sys.path.insert(0, str(BASE))


def _ensure_config():
    if CONFIG.exists():
        return
    from novel_downloader.infra.config import copy_default_config
    copy_default_config(CONFIG)
    # 启动时请求间隔降到 0.3s 提速，镜像站请求量大
    text = CONFIG.read_text(encoding="utf-8")
    text = text.replace('request_interval = 0.5', 'request_interval = 0.3')
    CONFIG.write_text(text, encoding="utf-8")


async def cmd_search(keyword, site, limit):
    from novel_downloader.plugins.search import search
    results = await search(
        keyword=keyword,
        sites=[site] if site else None,
        limit=limit,
        per_site_limit=min(3, max(1, limit)),
        timeout=8,
    )
    if not results:
        print("NO_RESULTS")
        return
    print(f"# {keyword} ({len(results)} results)")
    for r in results:
        title = r.get("title") or "(无标题)"
        author = r.get("author") or ""
        site_k = r.get("site", "")
        bid = r.get("book_id", "")
        url = r.get("book_url", "")
        print(f"[{site_k}] {title} | {author} | id={bid} | {url}")


async def cmd_download(site, target, fmt, out_dir, export_only):
    from novel_downloader.plugins import registrar
    from novel_downloader.infra.config import ConfigAdapter, load_config
    from novel_downloader.schemas import BookConfig

    config_data = load_config(CONFIG)
    adapter = ConfigAdapter(config=config_data)
    client = registrar.get_client(site, adapter.get_client_config(site))

    # URL 时自动识别站点
    if target.startswith("http"):
        from novel_downloader.infra.book_url_resolver import resolve_book_url
        resolved = await resolve_book_url(target)
        if not resolved:
            print(f"ERROR: 无法从 URL 解析出书籍: {target}")
            return 1
        site = resolved["site"]
        book_id = resolved["book_id"]
        print(f"已解析 URL: 站点 {site}, 书 ID {book_id}")
    else:
        book_id = target

    book = BookConfig(book_id=book_id)
    try:
        async with client:
            if adapter.get_login_required(site):
                login_ok = await client.login(
                    ui=None,
                    login_cfg=adapter.get_login_config(site),
                )
                if not login_ok:
                    print(f"ERROR: 站点 {site} 需要登录/cookie，登录失败")
                    return 1
            if not export_only:
                info = await client.get_book_info(book_id)
                title = info.get("title") or info.get("book_name") or book_id
                author = info.get("author") or ""
                vols = info.get("volumes") or []
                n = sum(len(v.get("chapters", [])) for v in vols)
                print(f"书籍: {title} | {author} | 共 {n} 章，开始下载...")
                await client.download_book(book)
                print("下载完成，导出中...")
            result = client.export_book(book, formats=fmt.split(","))
            for k, paths in result.items():
                for p in paths:
                    if out_dir:
                        dest = Path(out_dir) / Path(p).name
                        Path(out_dir).mkdir(parents=True, exist_ok=True)
                        Path(p).replace(dest)
                        print(f"OUTPUT {k}: {dest}")
                    else:
                        print(f"OUTPUT {k}: {Path(p).resolve()}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return 1
    return 0


def main():
    p = argparse.ArgumentParser(description="多站小说下载器")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("search", help="多站搜索")
    ps.add_argument("keyword")
    ps.add_argument("-s", "--site", default=None)
    ps.add_argument("-l", "--limit", type=int, default=15)
    ps.set_defaults(fn=cmd_search)

    pd = sub.add_parser("download", help="下载并导出")
    pd.add_argument("site", help="站点标识，或传 URL 时填 auto")
    pd.add_argument("target", help="书 ID 或书籍页 URL")
    pd.add_argument("--format", dest="fmt", default="txt", help="txt/epub/both")
    pd.add_argument("--out", dest="out_dir", default=None)
    pd.add_argument("--export-only", action="store_true", help="仅导出已下载数据")
    pd.set_defaults(fn=cmd_download)

    args = p.parse_args()
    _ensure_config()
    rc = asyncio.run(args.fn(
        **{k: v for k, v in vars(args).items() if k not in ("cmd", "fn")}
    ))
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
