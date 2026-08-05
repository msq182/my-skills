---
name: mubu-to-obsidian
description: Convert 幕布 (Mubu) exported HTML files to Obsidian-compatible Markdown format. Use this skill whenever the user mentions 幕布, Mubu, converting HTML to Markdown for Obsidian, importing notes from 幕布 to Obsidian, or needs to process a Mubu HTML export file. The skill downloads all images, saves them to a local folder, and generates properly formatted Markdown matching the user's Obsidian note style.
---

# 幕布 HTML → Obsidian Markdown 转换

将幕布导出的 HTML 文件转换为 Obsidian 可完美阅读的 Markdown 文件。

## 输出格式规范

格式参考用户 Obsidian 笔记风格（`妇科.md`）：

### 核心规则
- **不使用任何 `#` 标题**，全部使用 `- ` 缩进层级结构
- 每级缩进 = **4 个空格**
- 顶级节点：`- 文本`
- 子节点：`    - 文本`（4 空格）
- 孙节点：`        - 文本`（8 空格）
- 以此类推

### 文本格式映射
- 幕布 `bold`（粗体）→ `**文字**`
- 幕布 `underline`（下划线）→ `**文字**`（Obsidian 不支持下划线，用粗体替代）
- 幕布 `text-color-red`（红色文字）→ `==文字==`（Obsidian 高亮格式）
- 幕布 `highlight-yellow`（黄色高亮）→ `==文字==`（Obsidian 高亮格式）
- 红色/高亮 + 粗体同时存在 → `==**文字**==`（高亮内嵌粗体）

### 图片处理
- 所有图片下载到**与 md 文件同名的文件夹**中
- 图片引用格式：`![[文件夹名/图片文件名.png]]`（Obsidian wiki-link）
- 图片不加尺寸限制（不要 `|400` 等后缀）
- 图片的缩进层级：比所属文本多一级缩进

### 文件命名
- md 文件放在用户指定的文件夹中（如 `医学/`）
- md 文件名与幕布文档标题一致
- 图片文件夹与 md 文件同名
- **不要**在 md 文件内容中重复文件标题

## 使用流程

### 步骤 1：确认输入
- 用户提供幕布导出的 `.html` 文件路径
- 确认输出目录（默认 `医学/` 文件夹）

### 步骤 2：运行转换脚本
```bash
python3 ~/.claude/skills/mubu-to-obsidian/scripts/mubu_to_md.py
```

脚本会自动：
1. 解析 HTML 的嵌套 `<ul class="node-list">` / `<li class="node">` 结构
2. 下载所有图片（来自 `api2.mubu.com`）到同名文件夹
3. 生成 Obsidian 格式的 Markdown 文件

### 步骤 3：检查结果
- 用 `head -60` 查看文件前几行，确认格式正确
- 检查是否有残留的 `****`（双重粗体）或 HTML 标签
- 统计图片引用数量是否与下载数量一致

### 步骤 4：修复问题（常见）
1. **图片嵌套到错误层级** → 检查 `recursive=False` 是否正确
2. **`****text****` 双重粗体** → 合并相邻同类型标记的循环是否生效
3. **`====` 双重高亮** → 与粗体类似的合并逻辑
4. **`&#x20;` HTML 实体残留** → 确保做了 `.replace('&#x20;', ' ')`

### 步骤 5：收尾清理
- 删除原始 html 文件（用户确认后）
- 告知用户在 Obsidian 中打开查看效果

## 常见问题与解决方案

### 图片出现在错误层级
**原因**：BeautifulSoup 的 `find()` 默认递归搜索后代节点，祖先节点会错误地继承子孙的图片。
**解决**：使用 `li.find('ul', class_='image-list', recursive=False)` 只搜索直接子元素。

### `****` 双重粗体标记
**原因**：多个相邻的 span 都有 `bold` 类，各自独立包裹 `**` 造成 `**A****B****C**`。
**解决**：循环应用正则 `\*\*([^*]+)\*\*\*\*([^*]+)\*\*` → `**\1\2**` 直到不再变化。高亮的 `====` 同理。

### 图片下载失败
**原因**：幕布图片服务器可能需要 User-Agent header。
**解决**：脚本已包含标准浏览器 User-Agent。

### 文件权限问题（iCloud 目录）
**原因**：iCloud 文件有时被锁定，Write 工具返回 EPERM。
**解决**：改用 `cat > "path" << 'EOF'` 的 bash heredoc 方式写入。

## 脚本位置

转换脚本：`~/.claude/skills/mubu-to-obsidian/scripts/mubu_to_md.py`

直接运行即可，无需传参（路径硬编码在脚本中，根据实际情况修改顶部的 `html_path` 和 `output_dir`）。
