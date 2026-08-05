---
name: read-wechat-link
description: 读取微信文章链接（mp.weixin.qq.com）。当用户给出微信链接、需要抓取微信文章正文、或摄入微信文章内容到工作流（收件箱、资料收集、引用核对）时使用。通过伪装 iOS 微信 UA 绕过"请在微信中打开"拦截。
---

# Read WeChat Link

读取微信公众平台文章正文，绕过"请在微信中打开"的 UA 拦截。

## 何时使用

- 用户给出 `mp.weixin.qq.com` 链接，需要读取/整理文章正文
- 工作流摄入微信文章（如 `Work/收件箱.md`、资料收集、引用核对）

## 方法

用 iOS 微信 UA 伪装直连：

```bash
curl -L -A "iOS 微信 UA(MicroMessenger/8.0.40)" "<URL>"
```

建议静默下载到文件再解析，避免终端输出污染：

```bash
curl -sL -A "iOS 微信 UA(MicroMessenger/8.0.40)" "<URL>" -o /tmp/wechat-article.html
```

从 HTML 提取正文：标题在 `.rich_media_title`，正文在 `.rich_media_content`（可用 python/bs4 或简单 grep 截取）。

## 边界与失败处理

- 部分链接带签名/登录墙（`__biz` + 时效参数），UA 技巧不保证全部可读
- 若返回登录/验证页或重定向到非正文：停止重试，改用用户手动复制正文或截图
- URL 含 `&` 等特殊字符时务必整体加引号
- 只读取用户明确要求读的文章，不主动扫描
