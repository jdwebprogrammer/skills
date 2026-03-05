---
name: wodeapp-ai
description: "WodeApp AI Engine — token-efficient, unified credit pool, zero-deploy. Text, image, video (Doubao Seedance + Kling AI), structured JSON, TTS, visual workflows, no-code page building. 343+ models, MCP-native."
---

# WodeApp AI Skill Pack

> 🇺🇸 One skill pack to unlock all WodeApp AI capabilities — Text / Image / JSON / TTS / Video / Visual Workflow / Page Building / Zero-Deploy.
>
> 🇨🇳 只需接入一个 Skill 包，即可解锁 WodeApp 全部 AI 能力 — 文本 / 图片 / JSON / TTS / 视频 / 可视化工作流 / 页面构建 / 免部署发布。

## ✨ Core Capabilities | 核心能力

| Capability | Description 🇺🇸 | 说明 🇨🇳 | Models |
|------------|-----------------|---------|--------|
| 🤖 **Text** | Copywriting, summaries, translation, code | 文案、摘要、翻译、代码 | GPT-4o / Claude 3.5 / Gemini / DeepSeek / Qwen |
| 🎨 **Image** | Text-to-image, image-to-image, style transfer | 文生图、图生图、风格迁移 | Seedream 3.0 / Imagen 4 / Flux |
| 📊 **JSON** | Structured JSON output following your schema | 指定 Schema 输出精确 JSON | All models |
| 🎙️ **TTS** | Multi-language, multi-voice natural speech | 多语言多音色语音合成 | Doubao TTS / Edge TTS |
| 🎬 **Video** | Text/image to dynamic video | 文字/图片一键生成视频 | **Doubao Seedance** / **Kling AI** |
| ⚡ **Workflow** | Drag-and-drop multi-step AI pipelines | 拖拽编排 19 种步骤类型 | No code needed |
| 🌐 **Page Build** | One sentence → full interactive page | 一句话生成完整交互页面 | 60+ UI components |
| 🚀 **Zero-Deploy** | One-click publish, auto domain + SSL | 一键发布，自动域名 + SSL | `*.wodeapp.com` |

## 💰 Why WodeApp? | 为什么选 WodeApp？

| 🇺🇸 English | 🇨🇳 中文 |
|-------------|---------|
| **Token-Efficient** — Smart routing, same quality, 80% less cost | **极致省 Token** — 智能路由，同样效果成本直降 80% |
| **Unified Credit Pool** — One balance for 343+ models, no multi-platform hassle | **统一积分池** — 一份积分调 343+ 模型，告别多平台账单 |
| **Zero-Deploy, Zero-Ops** — Auto domain + SSL, no server needed | **免部署免运维** — 自动域名 + SSL，无需服务器 |
| **MCP Plug & Play** — Auto-discover all tools, zero config | **开箱即用** — MCP 直连，Agent 自动发现所有工具 |
| **Visual Workflows** — Form → AI → Review → Publish, drag-and-drop | **可视化编排** — 表单→AI→审核→发布，拖拽即成 |

## ⚙️ Setup | 准备工作

🇺🇸 Get your API Key: sign up at [wodeapp.ai](https://wodeapp.ai) → **API Skills** → **Generate API Key**

🇨🇳 获取 API Key：访问 [wodeapp.ai](https://wodeapp.ai) → 「开放能力」→ 「生成 API Key」

```bash
export WODEAPP_API_KEY="sk_live_xxxxxxxxxx"
```

## 🚀 Quick Start | 快速开始

### MCP Server (Recommended | 推荐)

🇺🇸 Add to your MCP client config (Claude Desktop `claude_desktop_config.json` or Cursor MCP settings):

🇨🇳 将以下配置添加到 MCP 客户端（Claude Desktop 的 `claude_desktop_config.json` 或 Cursor 的 MCP 设置）：

```json
{
  "mcpServers": {
    "wodeapp": {
      "type": "sse",
      "url": "https://wodeapp.ai/mainserver/mcp",
      "headers": { "X-API-Key": "${WODEAPP_API_KEY}" }
    }
  }
}
```

> ⚠️ **Security | 安全提示**: Use environment variable `$WODEAPP_API_KEY` instead of pasting the key directly. Never hardcode API keys in config files.
>
> ⚠️ 请使用环境变量 `$WODEAPP_API_KEY`，不要将密钥直接写在配置文件中。

**9 MCP Tools auto-discovered | 自动发现 9 个工具：**

| Tool | 🇺🇸 Description | 🇨🇳 说明 |
|------|-----------------|---------|
| `ai_generate_text` | AI text generation (343+ models) | AI 文本生成 |
| `ai_generate_image` | Text-to-image / image-to-image | 文生图/图生图 |
| `list_projects` | List user projects | 列出项目 |
| `create_project` | Create from template | 从模板创建 |
| `get_project` | Get project details | 获取项目详情 |
| `get_page` | Get page JSON config | 获取页面配置 |
| `list_actions` | List executable actions | 列出可执行 Action |
| `execute_action` | Execute action / workflow | 执行 Action/工作流 |
| `publish_project` | Publish to production | 发布上线 |

### REST API

🇺🇸 Standard HTTP. **Always include `X-API-Key` header.**

🇨🇳 标准 HTTP 请求，**必须携带 `X-API-Key`**。

```bash
# Text generation | 文本生成
curl -X POST https://wodeapp.ai/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $WODEAPP_API_KEY" \
  -d '{"message":"Write a brand tagline","model":"gemini-2.0-flash"}'

# Image generation | 图片生成
curl -X POST https://wodeapp.ai/api/ai/image/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $WODEAPP_API_KEY" \
  -d '{"prompt":"Coffee beans close-up","size":"16:9","model":"seedream-3.0"}'

# Video generation | 视频生成 (Doubao Seedance)
curl -X POST https://wodeapp.ai/api/ai/video \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $WODEAPP_API_KEY" \
  -d '{"prompt":"Barista latte art close-up","model":"seedance"}'

# Structured JSON | 结构化 JSON
curl -X POST https://wodeapp.ai/api/ai/json \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $WODEAPP_API_KEY" \
  -d '{"message":"Generate 3 prompts","systemPrompt":"Return {prompts:[{title,content}]}"}'
```

> Local dev | 本地开发: replace domain with `http://localhost:4100`

## 🔐 Security | 安全最佳实践

| Item | Recommendation 🇺🇸 | 建议 🇨🇳 |
|------|------------------|---------|
| **Key storage** | Always use env vars (`$WODEAPP_API_KEY`), never hardcode | 始终使用环境变量，不要硬编码 |
| **Scoped keys** | Create project-scoped keys with billing limits | 创建项目级密钥并设置额度上限 |
| **Revocation** | Revoke compromised keys instantly at wodeapp.ai | 密钥泄露时立即在 wodeapp.ai 撤销 |
| **Data policy** | Prompts are sent to AI providers for processing only, not stored for training | 提示词仅用于 AI 处理，不会用于模型训练 |
| **Rate limits** | Built-in per-user and per-project throttling protects against abuse | 内置用户/项目级限流防止滥用 |

## 📡 Endpoints | 端点

| Service | Production | Local Dev |
|---------|-----------|-----------|
| Main (Projects) | `https://wodeapp.ai/mainserver/api` | `http://localhost:3100/mainserver/api` |
| Runtime (AI) | `https://wodeapp.ai/api` | `http://localhost:4100/api` |
| MCP (SSE) | `https://wodeapp.ai/mainserver/mcp` | `http://localhost:3100/mainserver/mcp` |

## 🛡️ Rate Limits | 限流

| Layer | Mechanism | Value |
|-------|-----------|-------|
| Concurrency | Per-user / global | 5/user, 30 global |
| Guest daily | Per-guest cap | 500 credits/day |
| Project daily | Per-project cap | 2,000 credits/day |
| Billing | Token-based | Insufficient → `HTTP 402` |

## 🔧 Environment Variables | 环境变量

```bash
WODEAPP_API_KEY=sk_live_xxx          # Required | 必填
WODEAPP_MAIN_SERVER=http://...       # Optional | 选填
WODEAPP_RUNTIME_SERVER=http://...    # Optional | 选填
```

## 🏷️ Keywords

`ai` `text-generation` `image-generation` `video-generation` `tts` `mcp` `no-code` `no-deploy` `zero-deploy` `page-builder` `workflow` `visual-workflow` `agent-tools` `multi-model` `gpt-4o` `claude` `gemini` `deepseek` `doubao` `seedance` `kling` `seedream` `imagen` `flux` `qwen` `token-efficient`
