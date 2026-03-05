---
name: Zeelin深度研究
description: "Zeelin深度研究是一款 AI 驱动的深度研究辅助平台，支持普通模式、深度模式与专家模式三大研究路径，覆盖从快速理解到系统分析、再到超万字级专家报告生成的全过程。用户可根据任务需求选择不同研究深度，通过多轮推理与多源数据整合，高效完成企业分析、市场洞察、招商研究等复杂研究任务"
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["curl"] } } }
---

# Zeelin 深度研究

> AI 驱动的深度研究辅助平台，支持普通模式、深度模式、专家模式

## 没有 API Key 怎么办？

如果用户没有提供 api_key，提示用户前往 https://desearch.zeelin.cn/ 进行免费注册，获取点数及 api_key

**获取 API Key 步骤：**
1. 访问 https://desearch.zeelin.cn
2. 登录账号后点击立即体验
3. 页面左下角进入"我的会员"
4. 点击"MCP / API Key"
5. 复制对应的 Key

## API 基础信息

- **Base URL**: `https://desearch.zeelin.cn`
- **认证方式**: Header `x-api-key`
- **接口**: `POST /api/conversation/anew`

## thinking 参数

- `deep` - 深度思考模式（最强推理）
- `major` - 专家模式
- `smart` - 普通模式（最常用）

## 使用示例

### 普通模式搜索

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "smart",
    "workflow": "",
    "moreSettings": {}
  }'
```

### 深度思考模式

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "deep",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }'
```

### 专家模式

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "major",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }'
```

## 多轮对话

第一轮返回的 `sessionId` 可以用于后续对话：

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "上一轮的sessionId",
    "content": "追问内容",
    "thinking": "smart",
    "workflow": "",
    "moreSettings": {}
  }'
```

## 快速调用

用户 API key 从环境变量 `DESEARCH_API_KEY` 读取。

**设置方式：**
```bash
export DESEARCH_API_KEY="你的API Key"
```

### 普通模式调用示例

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "合肥地理位置怎么样",
    "thinking": "smart",
    "workflow": "",
    "moreSettings": {}
  }'
```

## 注意事项

- `sessionId` 为空时创建新对话
- `thinking` 参数决定推理深度
- API 返回 JSON，包含回答内容

---

## 查询任务状态

任务提交后，需要轮询查询状态：

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X GET "https://desearch.zeelin.cn/api/conversation/status?sessionId={sessionId}" \
  -H "x-api-key: ${API_KEY}"
```

**返回示例:**
```json
{
  "code": 200,
  "data": {
    "sessionId": "b9162dfdefa74461a764aebe51366d87",
    "status": 2,
    "statusText": "正常结束",
    "question": "合肥地理位置怎么样",
    "modelMode": "smart"
  }
}
```

**状态码说明:**
- `1` = 进行中
- `2` = 正常结束 ✅
- `3` = 用户主动结束
- `4` = 失败
- `5` = 排队中

---

## 查询历史内容

任务完成后，获取完整回答：

```bash
API_KEY="${DESEARCH_API_KEY}"
curl -s -X GET "https://desearch.zeelin.cn/api/conversation/history?sessionId={sessionId}&pageSize=10&pageNo=1" \
  -H "x-api-key: ${API_KEY}"
```

**返回字段:**
- `answers[].content` - AI 回答内容
- `answers[].createTime` - 创建时间
- `content` - 用户问题
- `others.search_range` - 搜索范围 (web/knowledge)
- `others.call_module` - 调用模块

---

## 完整任务流程

1. **创建任务** → POST `/api/conversation/anew` 获取 `sessionId`
2. **轮询状态** → 每隔一段时间调用 `/api/conversation/status?sessionId={id}` 检查状态
3. **状态 = 2** → 任务完成
4. **获取内容** → 调用 `/api/conversation/history` 获取完整回答
5. **保存文件** → 将回答内容保存为 `.md` 文件
6. **发送消息** → 使用 `message` 工具发送文件到用户

### 完整流程示例

```bash
# 1. 创建任务
API_KEY="${DESEARCH_API_KEY}"
RESULT=$(curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "smart",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }')

SESSION_ID=$(echo $RESULT | jq -r '.data.sessionId')
QUESTION_ID=$(echo $RESULT | jq -r '.data.id')

echo "Session ID: $SESSION_ID, Question ID: $QUESTION_ID"

# 2. 轮询状态直到完成
while true; do
  STATUS=$(curl -s -X GET "https://desearch.zeelin.cn/api/conversation/status?sessionId=${SESSION_ID}" \
    -H "x-api-key: ${API_KEY}" | jq -r '.data.status')
  
  if [ "$STATUS" = "2" ]; then
    echo "任务完成"
    break
  fi
  echo "状态: $STATUS, 等待中..."
  sleep 60  # 每分钟检查一次
done

# 3. 获取完整回答
curl -s -X GET "https://desearch.zeelin.cn/api/conversation/history?sessionId=${SESSION_ID}&pageSize=10&pageNo=1" \
  -H "x-api-key: ${API_KEY}" | jq -r '.data[0].answers[0].content' > result.md

# 4. 发送文件给用户
message action=send target={用户ID} filePath=result.md
```

### 实际调用命令（执行时替换对应变量）

```bash
# 1. 创建任务
API_KEY="${DESEARCH_API_KEY}"
curl -s -X POST "https://desearch.zeelin.cn/api/conversation/anew" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "sessionId": "",
    "content": "你的问题",
    "thinking": "smart",
    "workflow": "",
    "needEditChapter": 0,
    "moreSettings": {}
  }'
```

### 轮询状态脚本

```bash
# 轮询直到任务完成 (status = 2)
API_KEY="${DESEARCH_API_KEY}"
SESSION_ID="替换为实际的sessionId"

while true; do
  STATUS_RESPONSE=$(curl -s -X GET "https://desearch.zeelin.cn/api/conversation/status?sessionId=${SESSION_ID}" \
    -H "x-api-key: ${API_KEY}")
  
  STATUS=$(echo $STATUS_RESPONSE | jq -r '.data.status')
  echo "当前状态: $STATUS"
  
  if [ "$STATUS" = "2" ]; then
    echo "任务完成！"
    break
  fi
  
  sleep 60  # 每分钟检查一次
done

# 获取完整回答并保存为md文件
curl -s -X GET "https://desearch.zeelin.cn/api/conversation/history?sessionId=${SESSION_ID}&pageSize=10&pageNo=1" \
  -H "x-api-key: ${API_KEY}" | jq -r '.data[0].answers[0].content' > result.md

# 发送文件给用户
message action=send target=用户ID filePath=result.md
```

---


