---
name: skill-finder
description: 按能力需求在技能体系中找现成方案。当用户描述一个"想实现某个能力/功能"的需求并期待从技能库找到解决方案时使用，例如"能不能读微信文章""有没有发邮件的技能""有没有技能能转 PDF"。会按三层排查：本地技能库 → 公开技能市场 → 建议自研。适用于了解已有技能是否覆盖某需求、找可安装的技能、判断是否需要新建技能。
---

# Skill Finder

按用户描述的能力需求，在技能体系中找到最合适的现成方案。三层排查，从快到慢。

## 触发条件

用户说"有没有技能能…"、"帮我在技能里找…"、"我想实现…，有没有现成的"、"skills 里有没有…"等表述。

## 执行步骤

### 第 1 层：本地技能库排查（最快，必做）

**1a. canonical 全局技能（46 个实体，`~/.agents/skills/`）**

```bash
cd ~/.agents/skills && grep -l "SKILL.md" */SKILL.md 2>/dev/null | xargs grep -i "关键词1\|关键词2\|同义词" --include="SKILL.md" -l 2>/dev/null
```

- 更可靠的做法：遍历所有 `SKILL.md` 的 `description` frontmatter 匹配关键词：

```bash
for f in ~/.agents/skills/*/SKILL.md; do
  desc=$(sed -n '/^description:/,/^[a-z]/p' "$f" 2>/dev/null | tr '\n' ' ')
  echo "$(basename $(dirname $f)): $desc"
done | grep -i "关键词"
```

- 用能力相关的多个同义词搜（中文+英文，如"邮件"/"email"/"mail"）。
- 命中后**直接读该 SKILL.md 确认能力匹配**，不要只看名字。
- **注意区分实体 vs 软链**：canonical 里 `cua-driver` 是软链（→ `~/.cua-driver/skills/`，官方托管，不走 npx skills 管理/update）。匹配到它时如实告知用户这是外部托管技能，能力以 `cua-driver` 二进制为准。

**1b. 项目级技能（月付清单 `.agents/skills/`）**

```bash
ls ~/AI\ Projects/月付清单/.agents/skills/ 2>/dev/null
```

- 如果需求与某项目强相关，也查对应项目的 `.agents/skills/`。

**1c. 隔离层技能（快速扫一眼）**

```bash
# Codex 官方
ls ~/.codex/skills/.system/ 2>/dev/null
# Hermes 专属
for d in ~/.hermes/skills/*/; do [ -L "${d%/}" ] || echo "${d%/}"; done 2>/dev/null | xargs -I{} basename {}
```

- 隔离层技能只归单 agent，但若需求高度匹配且只在该 agent 用，也可直接指出。

### 第 2 层：公开技能市场排查（本地无命中时）

```bash
npx -y skills find <关键词>
```

- 交互式或关键字搜索 skills.sh 市场。
- 找到合适的 source（`owner/repo` 或 GitHub 直链）后，**先展示给用户**，询问是否安装，不要直接装。
- 若用户确认安装：
  - 判断该技能能否跨 agent 用（纯指令/调外部工具 → 可入 canonical；绑特定 agent → 隔离层）
  - 通用技能：`npx -y skills add <source> --skill '*' -g -a claude-code -a codex -a opencode -a grok -a qoder -a trae-cn -a reasonix -a zcode -a hermes-agent -a kimi-code-cli -a codebuddy`
  - 若 `ls -g` 计数与 canonical 不一致，以 `ls -d ~/.agents/skills/*/` 为准（lock 路径跟 `$XDG_STATE_HOME`）
  - **特殊形态：自带二进制/官方安装器的技能**（如 cua-driver 走 `cua-driver skills install`）通常自带分发机制，优先走官方安装而非 npx skills，装完在 catalog 标注"官方托管"。

### 第 3 层：建议自研（本地和市场都没有时）

- 明确告诉用户"无现成技能，建议自研"。
- 给出自研流程：写 `SKILL.md` → 放进 `msq182/my-skills` 仓库 → push → `npx skills update` 全 agent 生效。
- 可引用 `create-skill` 技能辅助搭建。
- 先和用户确认需求细节，再动手。

## 输出格式

```
## 排查结果：<需求>
### 命中（本地）
- <技能名>：<为什么匹配>（<位置>）
### 可选安装（市场）
- <source>：<描述>（<是否推荐>）
### 无现成 → 建议自研
<简要建议>
```

- 命中多个时按匹配度排序，标注推荐项。
- 没有命中也要明确说"没有"，不要强行凑。
- 全程只读排查，除非用户明确要求安装。

## 注意事项

- 关键词搜索要覆盖同义词，避免漏命中（如"截图"和"screenshot"）。
- description 匹配 ≠ 能力匹配，命中后必须读 SKILL.md 正文确认。
- 不要为了"有用"而推荐明显不相关的技能。
- 装新技能遵循共享层准入原则：能否跨 agent 跑；不能则进隔离层。
