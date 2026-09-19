---
name: cnb-github-publish
description: "Publish a local app or project to a CNB primary repository and a GitHub mirror, configure one-way CNB-to-GitHub synchronization, and verify that both repositories are aligned. Use when the user asks to upload, publish, mirror, or connect a project between CNB and GitHub."
---

# CNB 主仓库 + GitHub 镜像发布

把本地项目发布到两个代码托管平台，并建立清晰的单向维护关系：

- CNB 是主仓库和日常开发来源。
- GitHub 是用户自己的镜像仓库，用于备份、展示或云端协作。
- 原作者仓库、上游仓库只能作为 `upstream` 参考，未经用户明确授权绝不推送。

> **本技能 2026-09-12 经 FusionDay 实战校准。** 实操细节（CLI 语法、Secret 仓库边界、流水线验证）来自真实发布过程，与官方文档可能有出入时以本文件为准。

## 执行边界

这是一个需要实际写入远程仓库的发布技能。只有在用户明确要求发布、推送、同步或创建仓库时才执行远程写操作。普通检查只读完成，不因为"看起来应该同步"就自动创建仓库或推送。

目标信息必须来自用户当前请求、已确认的项目配置或当前登录会话：

- 本地项目绝对路径。
- CNB 目标仓库（命名空间/仓库名）。
- GitHub 目标仓库（账号/仓库名）及可见性。
- 主分支名称，默认 `main`，但必须以仓库实际分支为准。

如果目标仓库不明确，先问一个简短问题；不要猜测或沿用原作者仓库。

## 首次运行强制安全门

这是本技能最优先的规则，用来防止把代码误推到原作者仓库：

1. **第一次在一个项目上运行本技能时，必须先创建一个新的、属于用户自己的仓库。** 在 CNB 或 GitHub 创建一个即可；默认优先 CNB，但未明确平台时先问用户选择 CNB 还是 GitHub。不能把现有远端、当前 `upstream`、原作者仓库或任何来源不明的仓库当作“新仓库”。
2. 新仓库必须先通过平台查询复核：命名空间/账号属于用户、仓库名正确、可见性符合用户要求、仓库不是原作者仓库。复核完成前，不得添加该远端，也不得执行任何 `git push`。
3. 只有在新仓库创建并复核成功后，才能把它设为 `cnb` 或 `github` 发布目标；原作者或公共仓库一律命名为 `upstream`，并设置为不可推送。
4. 如果项目已经存在 `cnb`/`github` 远端，但无法证明它就是本次首次运行时创建的用户仓库，必须停下并报告远端，不得“顺手复用”。用户明确确认它是自己的仓库后，仍应先完成所有者和 URL 复核，再继续。
5. CNB 主仓库与 GitHub 镜像的单向同步只能在上述安全门通过后配置。同步目标只能是用户刚创建并复核过的 GitHub 仓库，绝不能从 `upstream` 推导目标。

**不可接受的捷径：** 看到已有 `origin`、看到仓库名相似、看到当前目录来自某个 GitHub clone，均不等于目标已确认；不得因此直接推送。

## 发布前检查

1. 读取项目的 `AGENTS.md`/`CLAUDE.md`、项目说明和 Git 状态；确认当前分支、未提交修改、已有远程和待发布内容。
2. **未 git 化的项目先 git 化**：`git init -b main` → 检查 `.gitignore` → `git add .` → 检查暂存清单无密钥 → 首次提交。四步缺一不可，`.gitignore` 必须在 `git add` 之前就位。
3. 保护用户现有修改。不要 reset、checkout 丢弃修改，也不要为了“整理干净”删除文件。
4. 检查待提交文件，排除 `.env`、API Key、Token、证书、数据库、个人配置、构建缓存和私密日志。若发现疑似密钥，停止发布并先处理泄露风险。
5. 执行“首次运行强制安全门”。若尚未创建并复核用户自己的新仓库，先完成创建和复核，再继续后面的远端配置。
6. 检查 `cnb`、`github`、`upstream` 的 URL；确认发布目标是用户自己的新仓库，原作者仓库只能是只读 `upstream`。
7. 若工作区有用户未提交修改，先说明将要提交的范围和提交信息；不要把无关改动混入发布。

## 本机 CNB CLI 环境（发布前先探测）

CNB CLI（`cnb`）是主要操作通道，token 存在 macOS Keychain，shell 里这样取：

```bash
export CNB_TOKEN="$(security find-generic-password -a "$(id -un)" -s 'CNB_TOKEN' -w)"
```

- **确认 `command -v cnb` 存在**。若 zshrc 里有 `cnb()` 包装函数，直接调用会失败（非交互 shell 不加载），必须用上面的 `security` 取 token 后 `export CNB_TOKEN=...` 调 `command cnb`。
- CLI 是 OpenAPI 风格：`cnb <module> <tool> [options]`，`cnb repositories --help` 列工具，`cnb <module> <tool> --help` 列参数。常用：

| 操作 | 命令 |
|---|---|
| 列我的仓库 | `cnb repositories get-repos --page-size 50`（过滤 `--filter-type secret` 只列密钥库） |
| 查仓库 | `cnb repositories get-by-id --repo <ns>/<name>` |
| 建仓库 | `cnb repositories create-repo --slug <ns> --data '{"name":"...","visibility":"private"}'` |
| 读远端文件 | `cnb git get-content --repo <ns>/<name> --file-path .cnb.yml --ref main` |
| 触发构建 | `cnb build start-build --repo <ns>/<name> --branch main --event api_trigger` |

**已知坑（实测踩过）：**

- `create-repo` 的 `--slug` 是**组织路径**（如 `msq-2026`），不是 `组织/仓库名`；仓库名放 `--data` 的 `name` 字段。混合使用 `--slug <ns>/<name>` 会返回误导性的 404。成功时返回 `status: 201` 且 body 为空（CLI 会报一个无害的 `Unexpected end of JSON input` 解析错误——**看到 201 就是成功**，用 `get-by-id` 复核）。
- 仓库名保持小写短横线（`fusionday`），与 FreeLLMAPI 既有模式一致。
- CLI token 的 scope 不覆盖构建日志读取（`repo-cnb-history:r`），`get-build-logs` 可能 403——改用网页端看流水线。

## 远程关系

推荐统一使用以下 remote 名称，降低误推风险：

```text
cnb      -> CNB 主仓库
github   -> 用户自己的 GitHub 镜像
upstream -> 原作者或公共上游，仅用于拉取参考（push 置 DISABLED://）
```

不要把原作者仓库继续放在 `origin` 这种容易误用的名称下。修改 remote 前先记录现有 URL，并用 `git remote -v` 验证结果。任何涉及强制推送、覆盖 GitHub 现有历史或删除远程内容的操作，都必须得到用户明确确认。

CNB 推送认证用 cnb CLI 的 git credential helper（仓库级配置，参照 FreeLLMAPI）：

```bash
git config credential.helper '!f() { /bin/zsh -lc '"'"'cnb git-credential "$1"'"'"' -- "$1"; }; f'
```

## 首次发布流程

1. 在本地提交经过检查的项目版本，提交信息要说明实际变更。
2. 将同一个提交推送到 CNB 主分支。
3. 创建或确认 GitHub 镜像仓库的可见性符合用户要求；默认选择私有，除非用户明确要求公开。
4. 在 CNB 上配置从主分支到 GitHub 镜像的单向同步（见下节）。同步目标必须是用户自己的 GitHub 仓库，不得是上游仓库。
5. 若 GitHub 为空，使用普通推送建立镜像；若 GitHub 已有不同历史，先停下报告差异，不擅自 force push。

## CNB 到 GitHub 同步

### .cnb.yml 模板（已验证可用）

```yaml
main:
  push:
    # CNB 是主仓库；GitHub 仅作为个人私有镜像。令牌含 workflow 写权限。
    - imports:
        - https://cnb.cool/<ns>/<repo>-secrets/-/blob/main/env.yml
      stages:
        - name: sync to github mirror
          image: tencentcom/git-sync
          settings:
            target_url: https://github.com/<owner>/<repo>.git
            auth_type: https
            username: ${GIT_USERNAME}
            password: ${GIT_ACCESS_TOKEN}
            branch: main
            push_tags: true
```

### 密钥仓库（<repo>-secrets）

密钥放在 CNB **Secret 可见性**的专门仓库（如 `msq-2026/fusionday-secrets`），格式两行：

```yaml
GIT_USERNAME: <github 用户名>
GIT_ACCESS_TOKEN: <github_pat_ / ghp_ / gho_ 开头的令牌>
```

**铁律与边界（全部实测）：**

- **Secret 仓库拒绝一切 token 访问**——API 和 git push 都返回 `403 "Secret repos do not support token access"`。这是平台安全设计，**不要试图绕过**。密钥写入只能走网页：用 kimi-webbridge 驱动用户已登录的浏览器代操作，或请用户手动操作（2 分钟）。每个项目一次性成本。
- 创建密钥仓库：`cnb repositories create-repo --slug <ns> --data '{"name":"<repo>-secrets","visibility":"secret"}'`。建好后网页打开 `https://cnb.cool/<ns>/<repo>-secrets/-/new/main?file_name=env.yml`。
- **令牌要求**：GitHub Fine-grained PAT（限制到目标镜像仓库，`Contents: Read and write`；镜像含 `.github/workflows` 时加 `Workflows: Read and write`），或本机 `gh auth token`（scope 含 repo + workflow，更宽但可用）。粘贴的令牌先用 `curl -s -o /dev/null -w "%{http_code}" -H "Authorization: token <t>" https://api.github.com/user` 静默验证——`rc-` 等非 `gh`/`github_pat_`/`ghp_` 前缀的令牌无效。
- 令牌绝不能写入代码、技能文件、终端输出、提交信息或最终回复。展示状态时只说"已配置/未配置"，验证时只打印前缀（`ghp_***`）。
- **网页代操作 Monaco 编辑器的坑**：往 `/-/new/main?file_name=env.yml` 页面填内容时，① URL 的 `file_name` 参数**不会**自动填进文件名输入框——必须先 `fill` `input[placeholder=输入文件名称]`，否则提交按钮永远 disabled；② webbridge `fill` 到 Monaco 的 `textarea.inputarea` 后**必须回读验证内容真的写入了**（提交前用 DOM 查询确认 `GIT_USERNAME` 存在）——第一次可能显示成功但实际为空，导致提交出空文件；③ 提交是两段式：点「提交」→ 弹出确认面板（默认"直接提交到 main 分支"）→ 再点一次「提交」；④ 全部完成后导航到 `/-/blob/main/env.yml` 回读页面文本，确认内容非空。

### 首次触发与验证

1. 推送（或推送一个空提交 `git commit --allow-empty`）触发流水线。
2. 流水线跑完约 45-60 秒后，验证 GitHub 镜像（见验证清单）。

## 验证清单（发布后必须核对实际结果）

**不要相信流水线的"通过"状态。** git-sync stage 的失败退出码可能不传导到流水线整体状态——流水线显示绿色但镜像推送实际失败（FusionDay 实战：日志里 `fatal: could not read Username for 'https://github.com'`，即密钥没注入，状态却是"通过"）。唯一可信的是镜像端实际提交。

1. `git remote -v` 指向正确的 CNB、GitHub 和可选上游。
2. CNB 主分支包含本次发布提交（`cnb git get-content` 或网页）。
3. **GitHub 镜像头部提交 == 本地头部提交**（决定性验证）：
   ```bash
   gh api repos/<owner>/<repo>/commits --jq '.[0].sha[:7]'   # 与 git log --oneline -1 对比
   ```
   镜像为空返回 409 "Git Repository is empty"。不一致 → 排查：本地推送成功？流水线是否跑过（网页 `/-/build/logs`）？日志里 git-sync 阶段的实际 stderr？密钥文件非空且变量名匹配？
4. 本地工作区状态符合预期，未产生意外改动。
5. 没有密钥进入提交、流水线日志或技能文件。流水线日志会回显 runner 环境但不含密钥值；网页截图/回读时一律先遮蔽令牌前缀再输出。

若 GitHub 只显示旧提交，不要立即重试或强推：先检查 CNB 流水线状态、目标分支、令牌权限和网络错误。将"CNB 发布成功"和"GitHub 镜像成功"分别报告。

## 输出格式

完成后用简短中文报告：目标仓库、主分支、最新提交短哈希、CNB 推送结果、GitHub 镜像结果、同步验证结果，以及仍需用户处理的事项（如需用户网页操作密钥库时明确列出步骤和 URL）。不要输出任何密钥、完整 URL 中的敏感查询参数或私密仓库内容。
