---
name: fleet-ops
description: 跨机执行纪律。当任务需要跑到 Mac Mini 或 Windows 上做时使用——远端代码工作、在那两台机器上跑命令/起服务、让那边的 Agent 干活，或判断某台机器为什么连不上。工具是 `fleet` 命令：网易UU远程 管设备发现与人工兜底，SSH 管实际执行。
---

# 跨机执行（fleet-ops）

> 最后更新：2026-10-03

## 一句话

三台机器、两条通道、一个命令：

```
本机 (MacBook Air)
   └── fleet ──┬── ssh macmini  →  Mac Mini   （常驻 hub）
               └── ssh windows  →  Windows    （开发机）
```

通道底座是**网易UU远程的「端口映射」**：把被控端 22 端口映射到本机（2222 / 2223），本机再用**标准 SSH** 直连。UU远程 只当网线，不当遥控器。

## 铁律

1. **动远端之前先 `fleet doctor`**。它分别显示 UU远程 CLI/设备状态、当前打开的映射规则、本机 TCP 监听、SSH banner 和远端命令执行；映射窗口未打开时，规则状态会标为未知，不会为了诊断主动打开或触发连接。
2. **不要在脚本里硬编码 IP / 端口**。机器清单唯一来源是 `~/.config/fleet/hosts.json`，用 `fleet hosts` 查看；`uuyc_device_name` 填 UU远程列表里的准确设备名，供 `repair` 定位界面。
3. **不要绕过 `fleet` 直接 `ssh`**，会丢掉 UU远程 那层的诊断和兜底提示。
4. **远端不做重复安装**。Mac Mini 是裸机；Windows 已装 Node / Codex 桌面版。
5. **终端里 `uuyc-cli term` 不能当执行接口**——它只开窗口、不回传输出。要执行就用 `fleet run`。

## 命令

| 命令 | 用途 |
|---|---|
| `fleet list` | 机器清单 + UU在线 / 本机入口 / SSH 状态；任一主机异常时返回非零退出码 |
| `fleet doctor` | 分层诊断 UU远程、映射规则、本机监听、SSH banner 和远端命令，出问题第一步 |
| `fleet repair <host>` | 确认为本机映射入口拒绝连接，或入口仍监听但 SSH 握手超时后，自动点击「端口映射」并验证 SSH 恢复 |
| `fleet run <host> "<命令>"` | 在远端执行 |
| `fleet open <host>` | 检查 SSH 状态后打开 UU远程人工接管窗口；CLI 会说明窗口输入边界 |
| `fleet hosts` | 查看机器清单 |

## 选路（从省到贵）

1. 本机能做的 → **本机做**，不要为了"用上通道"而外派
2. 必须远端跑的 → `fleet run <host> "..."`
3. `fleet doctor` 显示本机映射入口未监听，或入口仍监听但 SSH 握手超时 → `fleet repair <host>` 点击 UU远程设备卡片上的「端口映射」按钮建立会话，并等待 SSH 恢复；它不会修改已保存的规则。其他 SSH 故障用 `fleet open <host>` 人工接管；**不要**去改端口映射或重装 sshd

`fleet open <host>` 是明确请求打开 UU远程窗口时的人工兜底，不是命令执行通道。它会先探测 SSH，并在 SSH 可用时提示用 `fleet run` 执行远端命令，但仍会照常打开窗口。UU远程的终端/远控内容不会回传给 CLI，因此 CLI 不能判断窗口当前显示的是密码提示还是 shell，也不能代输。只有窗口明确显示 `Password:` 且说明正在验证被控端身份时，才在 UU远程窗口里输入账户密码；如果看到普通 shell 提示符（如 `%`、`$`、`PS ...>`），说明已经进入终端，不要再输入密码。拿不准时先停下确认，不要把密码输入普通命令行或发到聊天里。

`fleet doctor` 通过 `ssh -G <alias>` 解析 SSH 实际目标，不把本机端口写死。对于 loopback 目标，它分别探测本机 TCP 监听、SSH banner 和实际命令；banner 可判断流量是否到达 SSH 服务，命令探测再确认认证与远端 shell 可用。它只读取当前已打开的 UU 端口映射窗口；窗口未打开时映射规则显示未知，不会主动打开界面或建立会话。UU远程 CLI 的登录、网络和设备在线信息本身不能证明端口转发可用。

SSH 连接使用 `StrictHostKeyChecking=accept-new`：首次连接会记录主机密钥，后续密钥变化会拒绝连接并提示检查，不再跳过主机身份校验。

`fleet run` 只建立一次 SSH 命令连接，使用非交互认证和配置的 `ssh_timeout` 限制连接握手时间；远端命令本身可以按需长时间运行。

`fleet repair <host>` 只在 SSH 目标确认为本机映射且出现连接拒绝，或 SSH 握手超时并确认本机映射入口仍在监听时操作 UU远程：它会把主窗口置前、选中目标设备、真实点击设备卡片的「端口映射」按钮以建立映射会话，然后重试 SSH。超时时若本机入口本身不可连接，则不会点击。它不会切换、删除或重建已保存的规则。成功以 SSH 可达为准，不以窗口打开或端口监听为准。需要 macOS 图形会话及允许 fleet 读取和控制 UU远程界面；若客户端未运行、登录/网络异常或自动化权限不足，命令会停止并给出错误。其他 SSH 故障不会触发 UI 操作。

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
| UU远程 在线但 `fleet doctor` 显示入口未监听，或入口监听但 SSH 超时 | 设备在线/入口监听都不能证明 SSH 转发会话有效 | 运行 `fleet repair <host>` 自动点击设备卡片的「端口映射」按钮并验证 SSH；失败时查看页面是否显示「已连接」且 SSH 规则为「成功」。先不要删除或重建规则 |
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
