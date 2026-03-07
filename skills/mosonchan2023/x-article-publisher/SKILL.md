---
name: x-article-publisher
description: Publish Markdown to X (Twitter) Articles with persistent auth. 56 Stars! Auto-convert Markdown format. Each call charges 0.001 USDT via SkillPay.
version: 1.0.0
author: moson
tags:
  - twitter
  - x
  - article
  - publisher
  - markdown
  - social-media
homepage: https://github.com/joeseesun/qiaomu-x-article-publisher
metadata:
  clawdbot:
    requires:
      env:
        - SKILLPAY_API_KEY
triggers:
  - "publish to x"
  - "x article"
  - "twitter article"
  - "post article"
  - "publish markdown"
  - "发布到X"
  - "Twitter文章"
  - "X发布"
config:
  SKILLPAY_API_KEY:
    type: string
    required: true
    secret: true
---

# X Article Publisher

## 功能

Publish Markdown articles to X (Twitter) Articles with persistent authentication. 56 Stars!

### 核心功能

- **Persistent Auth**: 7-day login persistence
- **Markdown Support**: Full Markdown → X Articles conversion
- **Auto Images**: Smart cover and content image handling
- **Draft Only**: Saves as draft (safe)

### 支持的格式

- 标题 (H1-H6)
- 粗体、斜体
- 列表 (有序/无序)
- 引用块
- 代码块
- 超链接
- 图片

## 使用方法

```json
{
  "action": "publish",
  "file": "/path/to/article.md",
  "title": "My Article"
}
```

## 价格

每次调用: 0.001 USDT

## 前置需求

- macOS
- Python 3.9+
- X Premium Plus 订阅
