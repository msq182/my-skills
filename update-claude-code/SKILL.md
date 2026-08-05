---
name: update-claude-code
description: 更新 Claude Code CLI 到最新版本（自动配置网络代理 127.0.0.1:7897）。触发词："更新 claude"、"升级 claude"、"update claude"。
---

# 更新 Claude Code Skill

更新 Claude Code CLI 到最新版本。

## 用法

用命令：`/update-claude-code`，或者直接说"更新 claude"、"升级 claude"。

## 功能

- 自动设置网络代理（127.0.0.1:7897）
- 运行 `claude update` 命令
- 验证更新后的版本

## 手动执行步骤

如果需要手动执行：

```bash
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
export ALL_PROXY=http://127.0.0.1:7897
claude update
claude --version
```
