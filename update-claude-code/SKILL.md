---
name: update-claude-code
description: 更新 Claude 两个独立产物到最新版本：① Claude Code CLI（claude update，自动配置代理 127.0.0.1:7897）；② Claude Desktop App（/Applications/Claude.app，开启自动更新 + 重启触发下载安装）。两者升级互不联动。触发词："更新 claude"、"升级 claude"、"update claude"、"更新 claude desktop"、"升级 claude 桌面版"。
---

# 更新 Claude Skill

Claude 有两个**独立产物**，升级互不联动：

| 产物 | 形态 | 位置 | 更新方式 |
|---|---|---|---|
| Claude Code | CLI | `~/.local/bin/claude` | `claude update` |
| Claude Desktop | App | `/Applications/Claude.app` | 自动更新（defaults + 重启触发） |

CC Switch"本地环境检查"检测的是 **CLI** 版本，与 Desktop 无关。

## 用法

直接说"更新 claude"、"升级 claude"（指 CLI），或"更新 claude desktop"（指桌面版）。

## 一、Claude Code CLI

1. 设置代理并更新：

```bash
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
export ALL_PROXY=http://127.0.0.1:7897
claude update
claude --version
```

2. 清理旧版本目录（可保留最新，删旧版本号目录）：

```bash
ls ~/.local/share/claude/versions/
rm -rf ~/.local/share/claude/versions/<旧版本号>
```

## 二、Claude Desktop（/Applications/Claude.app）

### 1. 开启自动更新（若被关闭）

```bash
defaults write com.anthropic.claudefordesktop SUAutomaticallyUpdate -bool true
defaults write com.anthropic.claudefordesktop SUEnableAutomaticChecks -bool true
defaults read com.anthropic.claudefordesktop | grep SU
```

### 2. 前置条件：确认 CC Switch 本地路由在跑

**关键坑**：如果 Desktop 被 CC Switch 配置成走第三方供应商（如 DeepSeek，`claudeDesktopMode: proxy`），它依赖 CC Switch 本地路由 `127.0.0.1:15721`。路由停了会报 "Can't reach 127.0.0.1:15721"，且更新下载永远卡在 "Downloading update..."。

- 检查：`lsof -iTCP:15721 -sTCP:LISTEN`
- 修复：CC Switch → 设置 → 路由 → 勾选"开启 Claude Desktop 本地路由"（对应 DB `proxy_config` 的 claude 行，端口 15721）
- 路由与 Clash TUN 不冲突：CC Switch 管"Desktop→第三方"这一跳，Clash TUN 管 CC Switch 出站那跳，127.0.0.1 回环不进 TUN
- 更新下载出站走 Clash 代理（7897）

### 3. 触发下载 + 安装

```bash
# 重启 Desktop 触发启动时检查更新
kill <Claude PID> 2>/dev/null; sleep 3; open -a "Claude"
```

- 侧边栏底部出现 "Downloading update..." 即为下载中
- 更新包落在 `~/Library/Caches/com.anthropic.claudefordesktop.ShipIt/update.*/Claude.app`（可读 Info.plist 确认新版本号）
- 下载完成后退出 App（ShipIt 在退出时安装）：`kill <PID>` 或 `osascript -e 'quit app "Claude"'`
- 安装完成后重新 `open -a "Claude"`

### 4. 验证

```bash
plutil -p "/Applications/Claude.app/Contents/Info.plist" | grep CFBundleShortVersionString
```

## 边界与注意

- 官方更新源（api.anthropic.com / claude.ai）被 Cloudflare 风控，命令行 curl 探测拿不到版本号，不要浪费时间探测
- Desktop 的 Help 菜单**没有**"检查更新"选项（只有 Claude Help / Troubleshooting / Get Support）
- 版本号格式：Desktop 与 CLI 完全不同（如 Desktop `1.26832.0` vs CLI `2.1.227`），不要混淆
- 升级 Desktop 前确保 CC Switch 本地路由已启动，否则下载会一直卡住
