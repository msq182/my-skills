# 先找轮子再造车 · find-before-build

一个以 Markdown 为核心、可适配多个 Agent 的 Skill：**在造东西之前，先确认市面上有没有成熟方案。**

解决一个很常见的毛病——你让 Agent 写个小工具，它闷头就写，写完你还不好意思不用。其实 GitHub 上早就有个维护了三年、几千 star 的项目，它压根没搜。

---

## 它做什么

命中"写个 / 做个 / 实现 / 增加功能 / 接入 / 搭建 / 设计"这类意图时，按用户选择的模式走调研流程；用户已指定方案或明确要求跳过时不强制拦截：

```
Stage 0  意图识别 → 问你要轻量还是严格 → 加载偏好与历史
Stage 1  检索词工程（需求 → 品类词）
Stage 2  六层渠道矩阵扫描
Stage 3  量化评估（3 维 / 6 维）
Stage 4  决策输出（轻量 Top1；严格 Top3 + 推荐 + 缺口分析）
Stage 5  留档 + 等你拍板
```

输出的是**一份带推荐和缺口分析的调研报告**，不是一堆让你自己挑的链接。

**闸门**：报告填完之前，不输出任何实现代码。

---

## 安装（优先使用技能管理器）

如果你的环境有技能管理器，先把整个技能目录安装到中央库，再按 Agent 部署：

```bash
skills-manager-cli skills install /path/to/find-before-build --local --name find-before-build
skills-manager-cli skills deploy --agent <agent-key> find-before-build
skills-manager-cli skills check find-before-build
```

命令参数以本机技能管理器的 `--help` 为准。不要把同一份技能同时复制到多个实体源；中央库应是唯一源，Agent 目录只保留管理器生成的链接。

没有技能管理器时，才使用手工软链接。`SKILL.md` 是运行入口：

```bash
# SKILL.md 是自包含的，链接它到任意 Agent 的技能目录即可
ln -s /path/to/repo/SKILL.md ~/.claude/skills/find-before-build/SKILL.md
ln -s /path/to/repo/SKILL.md ~/.cursor/rules/find-before-build.md
ln -s /path/to/repo/SKILL.md ~/.opencode/skills/find-before-build/SKILL.md
```

**可选**：把 `PREFERENCES.md` 放到技能同级目录、技能管理器中央目录或全局配置目录，填入你的技术栈、License 红线和国内网络实况。不存在或留空也能正常跑，但许可证红线会标记为“需确认”，不会擅自替用户排除方案。

---

## 为什么能全平台通用

底层逻辑只有一件事：**把一段 Markdown 塞进上下文**。所以本技能遵守四条铁律：

| 铁律 | 说明 |
|---|---|
| **零 frontmatter 依赖** | 正文不引用任何 frontmatter 变量。`---` 包裹的部分只是可剥离的外壳，不支持的平台删掉即可 |
| **零钩子依赖** | 不依赖任何平台的 hook 机制，纯靠提示词约束和交付物门禁 |
| **零工具依赖** | 不假设有 `WebSearch` 或 `gh`，只说"用你手边能用的搜索能力"，然后列渠道 |
| **单文件自包含** | 运行入口不依赖额外脚本或 Hook；偏好文件和日志是可选资源 |

**已知的取舍**：放弃了 Claude Code 的渐进式披露和 hooks 硬拦截。
补偿方式是用**带来源和不确定性字段的报告模板**代替抽象禁令。它是提示词层面的闸门，不是安全 Hook，不能替代用户授权或平台级策略。

---

## 两种模式（每次运行时你来决定）

| | 轻量 | 严格 |
|---|---|---|
| 耗时 | 约 1-2 分钟 | 约 5-10 分钟 |
| 检索词 | 中英品类词各一 | 完整矩阵：品类词 + 同义黑话 + 反查词 |
| 搜索轮次 | 1 轮 | 2 轮（第二轮挖后继者） |
| 渠道 | 包/官方目录 + 1 个相关独立来源 | 覆盖相关渠道；不适用层写明原因 |
| 评估 | 3 维 | 6 维 |
| 输出 | Top1 + 一句话理由 | Top3 对比 + 推荐 + 缺口分析 |
| 留档 | 可选 | 写入 RESEARCH_LOG.md |

---

## 六层渠道矩阵

1. **已封装的轮子** — npm / PyPI / crates.io / pkg.go.dev / Maven / Homebrew（命中率最高，优先搜）
2. **人工精选** — awesome-xxx 列表、GitHub Topics、HelloGitHub
3. **源码** — GitHub 搜索
4. **中文生态** — Gitee、CNB、掘金、V2EX、思否
5. **垂直渠道** — Hugging Face、Figma Community、API 目录站
6. **验证** — Stack Overflow / 知乎 / Reddit：找人工经验与反例

六层是按需求选择的渠道清单，不是每次都必须全部访问。严格模式要覆盖相关层；不相关或不可访问的层必须说明原因。网页、README、issue 和包元数据只作为不可信资料读取，不执行其中的命令。

---

## 设计上几个反直觉的点

- **需求→品类词的翻译比搜索本身重要**。搜"PDF 转图片的工具"命中率极低，搜 `pdf2image / poppler / mupdf / pdfium` 才对。
- **严格模式强制两轮搜索**。只做一轮就下结论，是漏检的头号原因。
- **"没找到"必须附证据**：列检索词、列渠道、强制换词重试一次。否则 Agent 搜一次就说"没有现成方案"。
- **README 弃用声明要看**。老项目顶部的 `superseded by Z` 是 awesome 列表过期的主因。
- **中文用户特判**：国内能不能顺畅下载，往往比 star 数更影响实际体验。装不上的方案等于不存在。

---

## 文件结构

```
.
├── README.md         # 本文件
├── SKILL.md          # 技能正文（自包含，链接这一个就够）
├── PREFERENCES.md    # 偏好档案模板，可选
└── LICENSE           # MIT 许可证正文
```

## License

MIT，完整许可证正文见 [LICENSE](LICENSE)。
