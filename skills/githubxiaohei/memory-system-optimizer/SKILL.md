---
name: memory-system-optimizer
description: OpenCLAW 记忆系统优化 - 三层架构 + 自动衰减 + CRUD验证
version: 1.2.0
author: Odin
tags: [memory, openclaw, optimization, ai]
price: 0.01
currency: USDT
payment: skillpay
---

# Memory System Optimizer

> OpenCLAW 记忆系统优化 Skill，基于 Ray Wang 30天实战经验

## 功能

### 1. 三层记忆架构
- **NOW.md** - 工作台，当前任务看板
- **memory/YYYY-MM-DD.md** - 每日日志
- **INDEX.md** - 知识导航 + 健康度仪表盘

### 2. 自动衰减机制
- Hot/Warm/Cold 温度模型
- 自动归档过期记忆
- 优先级标记

### 3. CRUD 验证
- 写入前先读原则
- 冲突检测
- 过时标记

### 4. 写入工具
- memlog.sh - 自动时间戳日志
- memory-gc.sh - 冷数据归档
- memory-decay.js - 温度分档

## 收费

- **每次调用**: 0.01 USDT
- **支付方式**: SkillPay（BNB Chain）

## 安装配置

**获取凭证：**
1. 去 [skillpay.me](https://skillpay.me) 注册账号
2. 创建 Skill，获取 **API Key** 和 **Skill ID**
3. 设定价格：0.01 USDT/次

**配置环境变量：**
```bash
export SKILLPAY_API_KEY="你的APIKey"
export SKILLPAY_SKILL_ID="你的SkillID"
```

## 收费接入（必须）

**在执行 Skill 逻辑前，必须调用收费 API：**

```javascript
const SKILLPAY_API = "https://skillpay.me/api/v1/billing";
const API_KEY = process.env.SKILLPAY_API_KEY;
const SKILL_ID = process.env.SKILLPAY_SKILL_ID;

// 自动生成 user_id（用飞书/Telegram ID 或随机标识）
const userId = context.user_id || `user_${Date.now()}`;

// 扣费调用
const response = await fetch(`${SKILLPAY_API}/charge`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
  },
  body: JSON.stringify({
    user_id: userId,
    skill_id: SKILL_ID
  })
});

const result = await response.json();

if (result.success) {
  // ✅ 扣费成功，执行 Skill 逻辑
  return await runSkill(input);
} else {
  // 💳 余额不足，返回支付链接
  return {
    error: "insufficient_balance",
    message: "余额不足，请充值后继续使用",
    payment_url: result.payment_url
  };
}
```

**重要规则：**
- ❌ 不要让用户去 skillpay.me 注册
- ❌ 不要暴露 API Key
- ✅ user_id 自动生成，不要问用户要
- ✅ 余额不足时，直接发支付链接给用户

## 使用方法

```bash
# 写入日志
memlog.sh "标题" "内容"

# 刷新记忆
node memory-decay.js

# 归档
./memory-gc.sh
```

## 技术栈

- OpenCLAW
- Markdown 文件
- Shell 脚本
- Node.js
- SkillPay 计费

## 作者

Odin（总舵主）
