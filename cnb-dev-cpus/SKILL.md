---
name: cnb-dev-cpus
description: >-
  修改 CNB 云原生开发环境的 CPU 核数配置，覆盖 `.cnb.yml` 中 `$:` → `vscode`
  的 `runner.cpus` 与 `.cnb/settings.yml` 的启动按钮核数。当用户说“切换/调整云开发核数”“我要 2 核云开发”“云开发环境太卡/太浪费”或要求指定 CNB 云开发规格时使用；普通 CI 任务资源调优除非用户明确要求不适用。
---

# CNB 云开发 CPU 核数切换

把用户指定的 CNB 云原生开发环境核数同步到实际运行配置和启动按钮配置，同时保护仓库已有的镜像、服务、阶段脚本与其他 YAML 设置。

## 关键规则

- 云开发实际资源由 `.cnb.yml` 的 `$:` → `vscode` → `runner.cpus` 决定。
- `.cnb/settings.yml` 的 `workspace.launch.cpus` 只控制启动按钮的默认/展示核数；如果两个值不一致，会造成按钮提示与实际环境规格不一致。
- 按当前 CNB 规则，普通节点 `cnb:arch:amd64` 的 `cpus` 合法范围是 1–64，内存按 `cpus × 2GB` 计算；`cpus` 必须写成数字，不能写成字符串。
- GPU 节点（如 `cnb:arch:amd64:gpu` 或 `cnb:arch:amd64:gpu:<型号>`）核数固定为 16。检测到 GPU tag 后，不要手写或修改 `runner.cpus`；向用户说明无法按指定核数切换，并停止修改。
- `runner.tags`、`docker`、`services`、`stages` 和业务脚本不是本技能的调整对象。除非用户另有要求，不要删除、重排或改写它们。

## 执行流程

1. 读取仓库适用的 `AGENTS.md` 和 Git 状态，确认当前分支及未提交修改；只在用户当前要求涉及的仓库内操作。
2. 从用户请求解析目标核数。支持“2 核”“4核”“切到 8”等自然表达；无法确定唯一数字时先询问，不要猜测。
3. 校验目标值为整数且在 1–64 内。越界时直接报告合法范围，不修改文件。
4. 检查 `.cnb.yml` 的 `$:` → `vscode` 段，读取现有 `runner.tags`。若为 GPU 节点，按上面的 GPU 规则停止。
5. 对普通节点做最小改动：
   - 已有 `runner`：只修改或补充 `cpus: <目标数字>`。
   - 没有 `runner`：在 `vscode` 事件中补充 `runner.cpus`；保留该事件已有的 `docker`、`services`、`stages`。只有在现有配置明确需要节点标签时才补 `tags: cnb:arch:amd64`，不要无依据覆盖原标签。
   - `.cnb.yml` 或 `vscode` 事件不存在时，不要凭空重建完整流水线；报告缺失位置并请求确认后再新增。
6. 若 `.cnb/settings.yml` 存在，检查并同步 `workspace.launch.cpus`；同时保留按钮的 `name`、`description`、`disabled`、`autoOpenWebIDE` 等其他字段。若文件不存在，不为“按钮同步”擅自创建整份设置文件，除非用户明确要求新增启动按钮配置。
7. 使用最小补丁完成修改，检查 `git diff` 与 `git diff --check`。确认 `cpus` 是 YAML 数字、两处配置一致，且没有改动业务脚本。

## 参考片段

普通 2 核云开发环境的核心结构如下；实际输出应以仓库原有字段为准：

```yaml
$:
  vscode:
    - runner:
        tags: cnb:arch:amd64
        cpus: 2
      docker:
        image: node:20
      services:
        - vscode
        - docker
      stages:
        - name: 欢迎信息
          script: echo "当前是 2 核云开发环境"
```

按钮配置的核心结构如下：

```yaml
workspace:
  launch:
    button:
      name: 启动 2 核云原生开发
      description: 轻量环境，2 核 4G，一键进入
    cpus: 2
```

不要为了套用示例而覆盖仓库原有镜像、服务、阶段或按钮字段；示例中的欢迎阶段也不应被自动添加到真实项目。

## 输出要求

用简短中文称呼用户为“资中工程师”，并报告：

- 实际修改的文件和配置路径。
- 目标核数及按当前规则对应的内存（例如 2 核约 4GB）。
- 修改后的相关完整 YAML 片段，而不是只报一个数字。
- 未修改或无法修改的部分，以及原因。
- 提醒用户重新点击“云原生开发”按钮（或重建工作区）后生效；现有工作区不会因仓库文件改变而自动换规格。

## 边界

- 本技能只负责仓库配置编辑与本地校验，不代替用户发布、部署或创建云端工作区。
- 不修改 CI 事件段，除非用户明确要求调整 CI 任务核数。
- 不把 `cpus` 写成带引号的字符串。
- 不因“看起来应该统一”而改动 GPU 节点、业务脚本或无关配置。

相关官方文档：

- [自定义开发流水线](https://docs.cnb.cool/zh/workspaces/custom-dev-pipeline.md)
- [自定义云原生开发按钮](https://docs.cnb.cool/zh/workspaces/custom-dev-button.md)
