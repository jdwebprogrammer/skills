---
name: xiaohongshu-generator
description: Generate Xiaohongshu (RedNote) infographic images. 7.2K Stars! 9 styles × 6 layouts. Each call charges 0.001 USDT via SkillPay.
version: 1.0.0
author: moson
tags:
  - xiaohongshu
  - infographic
  - image
  - social-media
  - design
  - rednote
homepage: https://github.com/jimliu/baoyu-skills
metadata:
  clawdbot:
    requires:
      env:
        - SKILLPAY_API_KEY
triggers:
  - "xiaohongshu image"
  - "rednote image"
  - "infographic"
  - "小红书配图"
  - "小红书图片"
  - "生成图片"
  - "ins图片"
  - "ins风"
  - "social media image"
config:
  SKILLPAY_API_KEY:
    type: string
    required: true
    secret: true
---

# Xiaohongshu Image Generator

## 功能

Generate beautiful Xiaohongshu (RedNote) infographic images. From baoyu-skills with 7.2K Stars!

### 风格 (9 styles)

- cute (可爱)
- fresh (清新)
- warm (温暖)
- bold (大胆)
- minimal (简约)
- retro (复古)
- pop (波普)
- notion (笔记风)
- chalkboard (粉笔风)

### 布局 (6 layouts)

- sparse (稀疏) - 1-2点, 封面/引用
- balanced (均衡) - 3-4点, 常规内容
- dense (密集) - 5-8点, 知识卡片
- list (列表) - 4-7点, 清单/排行
- comparison (对比) - 2边, 前后/优缺点
- flow (流程) - 3-6步, 过程/时间线

## 使用方法

```json
{
  "action": "generate",
  "content": "今日星座运势",
  "style": "cute",
  "layout": "balanced"
}
```

## 价格

每次调用: 0.001 USDT

## Stars

7.2K Stars on GitHub!
