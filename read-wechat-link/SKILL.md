---
name: read-wechat-link
description: 读取微信文章链接（mp.weixin.qq.com）。当用户给出微信链接、需要抓取微信文章正文、或摄入微信文章内容到工作流（收件箱、资料收集、引用核对）时使用。通过 iOS 微信 UA 伪装绕过"请在微信中打开"拦截，必要时降级到真实浏览器通道。
---

# Read WeChat Link

读取微信公众平台文章正文，绕过"请在微信中打开"的 UA 拦截。

## 两级降级链

一级（UA 伪装，免费快速）失败 → 二级（kimi-webbridge 真实浏览器，需确认）→ 兜底（明确报错+部分信息）。

## 一级：iOS 微信 UA 伪装

用 iOS 微信 UA 伪装直连。内置多组 UA，随机选一组，失败换下一组：

```bash
UA1="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.40(0x18002823) NetType/WIFI Language/zh_CN"
UA2="Mozilla/5.0 (iPhone; CPU iPhone OS 26_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.70(0x18004629) NetType/WIFI Language/zh_CN"
UA3="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.34(0x16082222) NetType/WIFI Language/zh_CN"
```

静默下载到文件再解析，避免终端输出污染：

```bash
curl -sL -A "$UA1" "<URL>" -o /tmp/wechat-article.html
```

从 HTML 提取正文：标题在 `.rich_media_title`，正文在 `.rich_media_content`（可用 python/bs4 或简单 grep 截取）。

### 拦截判定（一级失败标准）

满足任一 → 判定被拦，换下一组 UA 或进入二级：
- 返回页面体积过小（< 30KB，正常文章通常数百 KB）
- 页面含验证关键字：`验证`、`环境异常`、`请在微信中打开`、`频繁`、`neterror`
- 重定向到登录/二维码页

连续请求间加 1~3 秒随机延迟，避免触发微信频控。

## 二级：kimi-webbridge 真实浏览器

一级全部失败且用户确认后，用 kimi-webbridge 驱动真实浏览器（复用本机登录态，可过滑块）：

1. 先向用户确认（借用浏览器侵入性强）："UA 被拦，是否用浏览器通道重试？"
2. `navigate` 打开文章 URL
3. `snapshot` 或 `evaluate` 提取正文文本（`#js_content`），并提取标题、作者、发布时间
4. 完成后 `close_tab`，不留会话

## 最终兜底

两级都失败时，明确报错并分类原因：
- 文章已删除/不存在 → "该内容已被删除"
- 私有/付费文章（仅粉丝可见）→ "需关注/付费，无法读取"
- 风控拦截 → "触发微信风控，建议手动打开链接"

能抓到的部分（标题/作者/发布时间）也一并输出，方便判断文章是否值得手动处理。

## 边界与失败处理

- 部分链接带签名/登录墙（`__biz` + 时效参数），UA 技巧不保证全部可读
- URL 含 `&` 等特殊字符时务必整体加引号
- 只读取用户明确要求读的文章，不主动扫描
- 二级依赖 kimi-webbridge daemon（`127.0.0.1:10086`）；未运行则跳过二级直接进兜底
