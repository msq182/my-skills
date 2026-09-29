---
name: fleet-ops
description: 跨机执行纪律。当任务需要跑到 Mac Mini 或 Windows 上做时使用——远端代码工作、在那两台机器上跑命令/起服务、让那边的 Agent 干活，或判断某台机器为什么连不上。工具是 `fleet` 命令：网易UU远程 管设备发现与人工兜底，SSH 管实际执行。
---

# 跨机执行（fleet-ops）

> 最后更新：2026-09-30

## 一句话

三台机器、两条通道、一个命令：

```
本机 (MacBook Air)
   └── fleet ──┬── ssh macmini  →  Mac Mini   （常驻 hub）
               └── ssh windows  →  Windows    （开发机）
```

通道底座是**网易UU远程的「端口映射」**：把被控端 22 端口映射到本机（2222 / 2223），本机再用**标准 SSH** 直连。UU远程 只当网线，不当遥控器。

## 铁律

1. **动远端之前先 `fleet doctor`**。它一次回答三件事：UU远程主程序在不在、设备在不在线、SSH 通不通。
2. **不要在脚本里硬编码 IP / 端口**。机器清单唯一来源是 `~/.config/fleet/hosts.json`，用 `fleet hosts` 查看；`uuyc_device_name` 填 UU远程列表里的准确设备名，供 `repair` 定位界面。
3. **不要绕过 `fleet` 直接 `ssh`**，会丢掉 UU远程 那层的诊断和兜底提示。
4. **远端不做重复安装**。Mac Mini 是裸机；Windows 已装 Node / Codex 桌面版。
5. **终端里 `uuyc-cli term` 不能当执行接口**——它只开窗口、不回传输出。要执行就用 `fleet run`。

## 命令

| 命令 | 用途 |
|---|---|
| `fleet list` | 机器清单 + 双状态（UU远程在线 / SSH 可达） |
| `fleet doctor` | 全链路诊断，出问题第一步 |
| `fleet repair <host>` | 本机映射端口拒绝连接时，打开对应设备映射页并等待 SSH 恢复 |
| `fleet run <host> "<命令>"` | 在远端执行 |
| `fleet open <host>` | SSH 不通时的兜底：开悠悠远程终端人工接管 |
| `fleet hosts` | 查看机器清单 |

## 选路（从省到贵）

1. 本机能做的 → **本机做**，不要为了"用上通道"而外派
2. 必须远端跑的 → `fleet run <host> "..."`
3. SSH 显示 `Connection refused` → `fleet repair <host>` 自动尝试恢复本机映射；其他 SSH 故障用 `fleet open <host>` 人工接管；**不要**去改端口映射或重装 sshd

`fleet repair <host>` 只在本机映射端口拒绝连接时操作 UU远程：它打开该设备的「端口映射」页并重试 SSH，不会切换、删除或重建规则。需要 macOS 图形会话和允许辅助功能控制 UU远程；若客户端未运行、登录/网络异常或自动化权限不足，命令会停止并要求人工处理。其他 SSH 错误不会触发 UI 操作。

## 两台机器的脾气

- **macmini** — macOS，用户 `msq`，默认 shell `zsh`。
  **裸机**：没有 node / git / brew / python3。要跑 JS/Python/git 必须先装环境。
- **windows** — Windows 11，用户 `mason`，**默认 shell 是 `cmd`**。
  - 要跑 PowerShell：`fleet run windows 'powershell -NoProfile -Command "..."'`
  - 路径用反斜杠；引号要套两层（外层 cmd、内层 PowerShell）

## 失败怎么办

| 症状 | 先查 | 处理 |
|---|---|---|
| 报「UU远程 主程序不可用」 | `fleet doctor` 第 1 行 | 打开 UU远程 客户端 / 登录 |
| UU远程 在线但 SSH 显示 `Connection refused` | 本机映射端口没有监听；映射规则可能尚未重新建立 | 运行 `fleet repair <host>`；失败时在 UU远程 设备列表选中目标设备，打开「端口映射」页，等对应 SSH 规则显示「成功」，再运行 `fleet doctor`。先不要删除或重建规则 |
| 映射页显示「成功」但 SSH 仍不通 | 远端 sshd 或映射目标异常 | 确认规则目标是 `127.0.0.1:22`，再检查远端 sshd；需要人工接管时用 `fleet open <host>` |
| 主机显示「未登记」 | deviceId 是否过期 | 更新 `hosts.json` 的 `uuyc_device_id` |
| 远端报「找不到命令」 | Windows 是不是 cmd 语法 | 显式调 `powershell` |

## 不要做的事

- 不要新建第二套派活通道；跨项目派活仍走 `AI/relay.md`
- 不要把 `fleet` 的输出当长报告贴出来——它只回结果和下一步
- 不要为协作而协作（见 `ops/agent-orchestration.md`：默认单 Agent，外派须能证明总成本更低）

## 相关

- 工具本体：`~/.local/bin/fleet`；配置：`~/.config/fleet/hosts.json`
  - 工具源码在本技能目录下的 `bin/fleet`（python3 单文件、无外部依赖）。**改工具改这里**，再 `cp bin/fleet ~/.local/bin/fleet`。
- 底层 CLI：`uuyc-cli`（配套技能 `uuyc-cli`）
- 派活纪律：`~/AI Projects/AI-memory/ops/agent-orchestration.md`
