---
name: skills-report
description: 一键盘点全机器技能：canonical 全局技能（~/.agents/skills）、agent 隔离层（zcode codex 官方 / hermes 专属）与各项目项目级技能（.agents/skills）。当用户说"看下我的技能""列出所有技能""技能报告""全局和项目技能"或想了解当前机器装了哪些 skills 时使用。读取路由卡 ops/projects/*.md 自动发现项目根，无需手动指定。
---

# Skills Report

一键汇总全机器技能，按三层输出：**canonical 全局技能**（npx skills canonical `~/.agents/skills/`）+ **agent 隔离层**（codex 官方 / hermes 专属，不共享）+ **各项目项目级技能**（`<项目>/.agents/skills/`）。对话内以 Markdown 输出，不写文件、不推送外部。

## 执行步骤

### 1. canonical 全局技能

```bash
npx -y skills ls -g --json 2>/dev/null
```

- 若失败（无 npx / 网络），退化为直接扫描：`ls -la ~/.agents/skills/`，逐个读 `SKILL.md` frontmatter 的 `name`/`description`。
- 输出要点：技能名、来源（source，`owner/repo` 或 `local`）、挂载的 agents 数量。
- **注意**：`ls -g` 总数 > canonical 实体数是正常的（多出 agent 隔离层实体）。以 `ls -d ~/.agents/skills/*/` 的实体数为 canonical 权威计数。

### 2. agent 隔离层（不共享，只读盘点）

这些技能不在 canonical，属于特定 agent 独占，只列不评：

```bash
# ZCode 的 Codex 官方技能（OpenAI 系统技能，实体在 ~/.codex/skills/.system/）
ls ~/.codex/skills/.system/ 2>/dev/null

# Hermes 专属技能（canonical 软链之外的独立实体）
for d in ~/.hermes/skills/*/; do
  b="${d%/}"; [ "${b##*/}" = ".system" ] && continue
  [ -L "${d%/}" ] || echo "${d%/}"
done
```

- 隔离层判定：**canonical 实体（`ls -d ~/.agents/skills/*/`）之外的 agent 独立技能**。
- ZCode 下 imagegen/openai-docs/plugin-creator/review-agent/skill-creator/skill-installer 是 Codex 官方 system 技能（实体 `~/.codex/skills/.system/`，zcode 软链引用），**不要动**。
- Hermes 下 hermes-desktop-plugins/hermes-themes 及 apple/email/creative 等是其专属实体（`~/.hermes/skills/`），不纳入 canonical。
- 这类技能只归本 agent 用，输出时标注"隔离层，非共享"。

### 3. 项目级技能

**项目根列表来自共享记忆路由卡**（联动，无需手工维护）：

```bash
grep -rhoE '`~/[^`]+|`/[^`]+' ~/ObsidianVaults/AI/ops/projects/*.md 2>/dev/null \
  | tr -d '`' | sort -u | while read p; do
      p="${p/#\~/$HOME}"
      [ -d "$p/.agents/skills" ] && echo "$p"
    done
```

- 提取所有路由卡中反引号包裹的路径 → 展开 `~` → 只保留含 `.agents/skills/` 的目录。
- 对每个命中项目，读其项目级技能清单：

```bash
ls "<项目>/.agents/skills/" 2>/dev/null
```

- 如有 `skills-lock.json`，优先读它（权威清单，含 source/sourceUrl）：

```bash
python3 -c "import json;d=json.load(open('<项目>/.agents/skills/skills-lock.json'));print(list(d.get('skills',{}).keys()))"
```

- 项目名用路由卡文件名（如 `novel`、`monthly-list`）或路径最后一段标注。

### 4. 汇总输出

对话内输出，结构：

```
## canonical 全局技能（~/.agents/skills，N 个）
| 技能 | 来源 | 挂载 agents |

## agent 隔离层（不共享）
### ZCode（Codex 官方）
- <技能名>...
### Hermes（专属）
- <技能名>...

## 项目级技能（M 个项目）
### <项目名>（<路径>）
- <技能名>（来源）
...
```

- 只列有项目级技能的项目；无项目级技能的项目不出现。
- 全局与项目同名的技能照常并列（不同 scope，不冲突）。

## 注意事项

- 路由卡是唯一项目根来源；新项目建卡后自动纳入，无需改本技能。
- 不要修改任何技能文件或 lock——只读盘点。
- 输出保持简洁，长清单可折叠（按 agent 归组或按项目归组）。
- lock 文件位置随 `$XDG_STATE_HOME` 变化（本机 opencode 注入 → `$XDG_STATE_HOME/skills/.skill-lock.json`），查记录先看环境变量。
