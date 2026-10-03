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

1. **动远端之前先 `fleet doctor`**。它检查 UU远程 CLI/设备状态、映射规则、本机 TCP 监听、SSH banner 和远端命令；在 macOS 上，如果 UU 已登录且网络正常、目标设备在线，并确认 SSH 本机映射入口拒绝连接，或入口仍监听但 SSH 握手超时，它会自动点击「端口映射」并验证 SSH。`fleet doctor --check` 只诊断，不操作 UU远程界面。
2. **不要在脚本里硬编码 IP / 端口**。机器清单唯一来源是 `~/.config/fleet/hosts.json`，用 `fleet hosts` 查看；`uuyc_device_name` 填 UU远程列表里的准确设备名，供 `repair` 定位界面。
3. **不要绕过 `fleet` 直接 `ssh`**，会丢掉 UU远程 那层的诊断和兜底提示。
4. **远端不做重复安装**。Mac Mini 是裸机；Windows 已装 Node / Codex 桌面版。
5. **终端里 `uuyc-cli term` 不能当执行接口**——它只开窗口、不回传输出。要执行就用 `fleet run`。

## 命令

| 命令 | 用途 |
|---|---|
| `fleet list` | 机器清单 + UU在线 / 本机入口 / SSH 状态；任一主机异常时返回非零退出码 |
| `fleet doctor` | 分层诊断；确认本机映射故障时自动恢复并验证 SSH |
| `fleet doctor --check` | 只诊断，不操作 UU远程界面 |
| `fleet repair <host>` | 确认为本机映射入口拒绝连接，或入口仍监听但 SSH 握手超时后，自动点击「端口映射」并验证 SSH 恢复 |
| `fleet run <host> "<命令>"` | 在远端执行 |
| `fleet agent submit windows --dir <路径> [--auto] <任务>` | 把任务交给 Windows 上已安装的 OpenCode，后台执行并返回任务 ID |
| `fleet agent status windows <任务ID>` | 查询任务状态；完成后取回 Agent 回复 |
| `fleet agent wait windows <任务ID> [--timeout 秒] [--interval 秒]` | 定时轮询，完成后取回 Agent 回复 |
| `fleet open <host>` | 检查 SSH 状态后打开 UU远程人工接管窗口；CLI 会说明窗口输入边界 |
| `fleet hosts` | 查看机器清单 |

## 选路（从省到贵）

1. 本机能做的 → **本机做**，不要为了"用上通道"而外派
2. 必须远端跑的 → `fleet run <host> "..."`
3. 需要远端 Agent 自主处理并回报 → `fleet agent submit windows --dir <Windows项目绝对路径> "<任务>"`，拿到任务 ID 后用 `fleet agent wait` 等待并取回回复
4. `fleet doctor` 会在确认本机映射拒绝连接，或入口仍监听但 SSH 握手超时时，自动点击 UU远程设备卡片上的「端口映射」按钮并验证 SSH；它不会修改已保存规则。只有使用 `fleet doctor --check` 后想手动恢复时才需要 `fleet repair <host>`。其他 SSH 故障用 `fleet open <host>` 人工接管；**不要**去改端口映射或重装 sshd

## 远端 Agent 派活（当前支持 Windows + OpenCode）

```sh
fleet agent submit windows --dir 'C:\Users\mason\项目目录' '检查这个项目的启动错误并修复'
fleet agent status windows <任务ID>
fleet agent wait windows <任务ID> --timeout 1800 --interval 5
```

任务经现有 SSH 通道送到 Windows，由已安装的 `opencode run` 在后台执行；fleet 不安装 Agent、不新增模型服务，也不选择免费模型，OpenCode 使用 Windows 上现有的 provider 配置，费用取决于该配置的账户与模型。必须给出绝对项目目录，避免 Agent 在错误目录工作。任务状态、请求和回复保存在 Windows `%LOCALAPPDATA%\fleet\agent-tasks\<任务ID>`；任务 ID 可用于后续查询。当前只实现 Windows/OpenCode，Mac Mini 通道与 Agent CLI 尚未验证。

默认保留 OpenCode 的权限策略。只有明确同意 Agent 自动批准工具操作时，才追加 `--auto`；该选项会把 OpenCode 的 `--auto` 传给远端 Agent。非交互运行遇到需要人工确认的操作时可能失败，使用 `fleet agent status` 查看错误。不要把密码、API key 或其他秘密写进任务内容；请求与回复会留存在远端任务目录。

`fleet open <host>` 是明确请求打开 UU远程窗口时的人工兜底，不是命令执行通道。它会先探测 SSH，并在 SSH 可用时提示用 `fleet run` 执行远端命令，但仍会照常打开窗口。UU远程的终端/远控内容不会回传给 CLI，因此 CLI 不能判断窗口当前显示的是密码提示还是 shell，也不能代输。只有窗口明确显示 `Password:` 且说明正在验证被控端身份时，才在 UU远程窗口里输入账户密码；如果看到普通 shell 提示符（如 `%`、`$`、`PS ...>`），说明已经进入终端，不要再输入密码。拿不准时先停下确认，不要把密码输入普通命令行或发到聊天里。

`fleet doctor` 通过 `ssh -G <alias>` 解析 SSH 实际目标，不把本机端口写死。对于 loopback 目标，它分别探测本机 TCP 监听、SSH banner 和实际命令；banner 可判断流量是否到达 SSH 服务，命令探测再确认认证与远端 shell 可用。映射规则状态检查本身只读取当前已打开的 UU 窗口；只有满足上述安全条件时，doctor 才会额外操作 UI 建立映射会话。UU远程 CLI 的登录、网络和设备在线信息本身不能证明端口转发可用。若 UU 状态不正常、设备离线、SSH 目标不是本机映射，或故障类型不是拒绝连接/符合条件的握手超时，doctor 不会点击界面。

SSH 连接使用 `StrictHostKeyChecking=accept-new`：首次连接会记录主机密钥，后续密钥变化会拒绝连接并提示检查，不再跳过主机身份校验。

`fleet run` 只建立一次 SSH 命令连接，使用非交互认证和配置的 `ssh_timeout` 限制连接握手时间；远端命令本身可以按需长时间运行。

`fleet repair <host>` 只在 SSH 目标确认为本机映射且出现连接拒绝，或 SSH 握手超时并确认本机映射入口仍在监听时操作 UU远程：如果客户端停在远控屏幕标签，它会先通过「窗口 → 网易UU远程」回到设备卡片，再选中目标设备并真实点击卡片上的「端口映射」按钮，最后重试 SSH。超时时若本机入口本身不可连接，则不会点击。它不会切换、删除或重建已保存的规则。成功以 SSH 可达为准，不以窗口打开或端口监听为准。需要 macOS 图形会话及允许 fleet 读取和控制 UU远程界面；若客户端未运行、登录/网络异常或自动化权限不足，命令会停止并给出错误。其他 SSH 故障不会触发 UI 操作。

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
| UU远程 在线但映射入口未监听，或入口监听但 SSH 超时 | 设备在线/入口监听都不能证明 SSH 转发会话有效 | 运行 `fleet doctor` 自动点击设备卡片的「端口映射」按钮并验证 SSH；若本轮已点击仍失败，不要立刻重复，按输出检查远端 SSH 服务与映射目标。先不要删除或重建规则 |
| 映射页显示「成功」但 SSH 仍不通 | 远端 sshd 或映射目标异常 | 确认规则目标是 `127.0.0.1:22`，再检查远端 sshd；需要人工接管时用 `fleet open <host>` |
| 主机显示「未登记」 | deviceId 是否过期 | 更新 `hosts.json` 的 `uuyc_device_id` |
| 远端报「找不到命令」 | Windows 是不是 cmd 语法 | 显式调 `powershell` |

## 不要做的事

- 不要新建第二套跨项目派活/跟踪总线；项目级交接仍走 `AI/relay.md`。`fleet agent` 只负责一次性远端执行、状态轮询和回复取回
- 不要把 `fleet` 的输出当长报告贴出来——它只回结果和下一步
- 不要为协作而协作（见 `ops/agent-orchestration.md`：默认单 Agent，外派须能证明总成本更低）

## 相关

- 工具本体：`~/.local/bin/fleet`；配置：`~/.config/fleet/hosts.json`
  - 工具源码在本技能目录下的 `bin/fleet`（python3 单文件、无外部依赖）。**改工具改这里**，再 `cp bin/fleet ~/.local/bin/fleet`。
- 底层 CLI：`uuyc-cli`（配套技能 `uuyc-cli`）
- 派活纪律：`~/AI Projects/AI-memory/ops/agent-orchestration.md`
