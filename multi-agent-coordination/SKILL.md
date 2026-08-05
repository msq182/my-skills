---
name: multi-agent-coordination
description: Multi-agent onboarding and daily-startup coordination playbook for the user's Claude+Hermes+WorkBuddy+ZCode+Grok system. Use when the user wants to onboard a new AI agent, set up or upgrade cross-agent collaboration, fix agent-to-agent sync/coordination issues, or apply the daily-startup discipline (M1-M4). Covers the softlink onboarding pattern, the AI vault as shared memory, the M1-M4 daily-startup rules, and the two-skill-system architecture. Trigger phrases include "接入新 agent", "多 agent 协作", "升级启动流程", "agent 同步", "协调架构".
---

# 多 Agent 协作接入与每日启动纪律

本 skill 定义本用户生态下「新 agent 接入」与「每日启动纪律」的可复用流程。与具体 AI 工具无关——Claude / Hermes / WorkBuddy / ZCode / Grok 通用。

> 最后更新：2026-07-13  
> **系统总览（优先）**：`~/ObsidianVaults/AI/ops/map.md`  
> **通道细节**：`~/ObsidianVaults/AI/ops/channels.md`  
> **项目交接卡**：`~/ObsidianVaults/AI/ops/projects/`（接项目先读对应卡）

---

## 核心架构（先读这个）

- **Agent**：Claude Mac（主协调）、Claude Win（跨设备）、Hermes（云，task-broker）、WorkBuddy（vault 中继 + 协作群）、ZCode / Grok（软链或同 vault 纪律）。
- **协调中枢 = AI vault**：`~/ObsidianVaults/AI/`（Syncthing `ai-memory`）。
- **记忆 v2 分层**：`NOW.md`（Working）+ `shared-memory.md`（evergreen ≤2000）+ `ops/map.md` / `ops/channels.md` / `ops/projects/`（程序 + 项目交接）+ `decisions.md` / `session-log.md` / `relay.md`。
- **单一操作入口**：`~/.claude/CLAUDE.md`（SSOF；与 `AI/AGENTS.md` 冲突时以 CLAUDE.md 为准）。
- **黄金原则**：软链接入 + AI vault 共享记忆，**不需要第三套结构**。不另建 registry / inbox / 协议。
- **WB 不加** task-broker 第三节点；飞书**不当**权威记忆。

---

## 模块 1：新 Agent 接入（软链接入）

最快的接入方式 = 让新 agent 的启动配置直接指向 Claude 的 `CLAUDE.md`：

```bash
# ZCode 同款
ln -sf /Users/masongqi/.claude/CLAUDE.md /Users/masongqi/.zcode/AGENTS.md
# WorkBuddy 同款
ln -sf /Users/masongqi/.claude/CLAUDE.md /Users/masongqi/.workbuddy/CLAUDE.md
```

要点：
- 软链后，新 agent 读到的启动指令与 Claude **字字相同**——无需 registry/inbox。
- 共享上下文靠「软链 + AI vault 文件系统」，零新基础设施。
- 接入后：在 `ops/map.md` §2 补一行角色；需要新通道再改 `ops/channels.md`。
- WorkBuddy：无原生 boot；靠每日同步 + 会话内读软链；本地 `.workbuddy/memory` 休眠，新记忆只写 AI vault。

---

## 模块 2：每日启动纪律（M1–M4）

已落地于 `~/.claude/CLAUDE.md` 与 `AI/AGENTS.md`。

- **M1 默认轻量收尾**：会话末若有变化，追加 ≤3 行到 `session-log.md`（格式 `YYYY-MM-DD HH:MM | <参与者> | <一句话>`，append-only）。「变化」：新偏好/决策/状态 · 改了 vault 文件 · 用户要求记住。Full save 仍等触发词。
- **M2 启动扫 decisions 顶部**：顶部 ~5 条（标题+日期），避免翻案已定之事。
- **M3 NOW 锚点**：独立文件 `NOW.md`（≤10 行，整段覆盖）。谁改全局状态谁覆盖；过期即删。**不是** shared-memory 顶部小节。
- **M4 参与者适配**：Claude/ZCode 有真 boot；WorkBuddy 靠同步 + 软链；Grok 在本 workspace 跟 vault 启动 5 步；Hermes 跟 vault + broker。

启动 5 步：`NOW` → session-log 前 40 → decisions 顶 5 → relay 非终态 → 按需 shared / channels / **map**。

---

## 模块 3：技能系统架构（勿混淆）

- **共享 skill（记忆系统一等公民）**：`~/.claude/skills/`、`Novel/skills/`、`Work/skills/`（Claude Code 格式 `SKILL.md`）。
- **WB skills 孤岛**：`~/.workbuddy/skills/` 仅 WB 可见。
- **推论**：多方复用须写成 Claude 格式落到 vault / `~/.claude/skills/`，**非** WorkBuddy SkillManage。
- 索引：`AI/skills-catalog.md`。

---

## 通道速查（细节见 channels / 决策表见 map）

| 场景 | 通道 |
|------|------|
| 跨 agent 派活 | vault 中继 `relay.md` |
| WB↔Claude 实时商量 | AI 协作群（只对话） |
| Win↔Mac Claude | 跨设备群 |
| Claude↔Hermes | task-broker |
| 长期事实 | 直接写 vault |

---

## 常见错误

| 错误 | 正确做法 |
|------|---------|
| 为新 agent 另建 registry/inbox/协议 | 软链 + AI vault（黄金原则） |
| 用 WorkBuddy SkillManage 做「共享 skill」 | 写 `SKILL.md` 到共享路径 |
| 启动只信触发词收尾 | M1 默认轻量收尾 |
| 改动不更 NOW | 覆盖 `NOW.md`，不是 shared 顶部 |
| 翻案已定决策 | 启动扫 decisions 顶部 5 条 |
| 飞书当权威记忆 / 只在群里派活 | 派活走 relay；飞书只辅助对话 |
| 把 WB 加进 broker 或跨设备群 | 见 decisions + map |

---

## 当前状态（2026-07-13）

- 记忆 v2 已落地；系统总览在 `ops/map.md`。
- 主通道：vault 中继 + AI 协作群；跨设备群独立；单聊 p2p 弃用。
- task-broker 仅 Claude↔Hermes；状态以 `NOW.md` / 服务检查为准（勿写死「宕机」）。
