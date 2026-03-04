---
name: somark-document-parser
description: 使用 SoMark 文档智能 API 将 PDF、图片及 Office 文件同步解析为 Markdown 或 JSON，需提供 SoMark API Key。
metadata: {"openclaw": {"emoji": "📄", "requires": {"env": ["SOMARK_API_KEY"]}, "primaryEnv": "SOMARK_API_KEY"}}
---

# SoMark 文档智能解析

## 概述

使用 [SoMark](https://somark.tech) 文档智能 API 将 PDF、Word、PPT 及常见图片格式解析为 Markdown 或 JSON，一次调用同步返回结果。

---

## 配置 API Key（首次使用必读）

在使用本 skill 之前，需要先配置 SoMark API Key：

1. 前往 [https://somark.tech](https://somark.tech) 注册并获取 API Key（格式：`sk-...`）。
2. 在 `~/.openclaw/openclaw.json` 中添加以下配置（如文件不存在请新建）：

```json
{
  "skills": {
    "entries": {
      "somark-document-parser": {
        "enabled": true,
        "apiKey": "sk-YOUR_API_KEY_HERE"
      }
    }
  }
}
```

3. 重新开启一个新的 OpenClaw 会话，配置即生效。

> **提示**：也可直接设置环境变量 `SOMARK_API_KEY=sk-...`，OpenClaw 将自动读取。

---

## 触发时机

当用户请求解析、提取、转换以下类型的文件时激活本 skill：
- PDF 文件（`.pdf`）
- 图片（`.png` / `.jpg` / `.jpeg` / `.bmp` / `.tiff` / `.webp` / `.heic` / `.heif` 等）
- Office 文档（`.doc` / `.docx` / `.ppt` / `.pptx`）

用户说法示例：
- "帮我解析这个 PDF"
- "把这个文档转成 Markdown"
- "用 SoMark 解析 /path/to/file.pdf"
- "提取这个文件的内容"
- "parse this PDF"
- "extract content from this file"
- "convert this document to markdown"

---

## 调用方式

### 使用 `curl` 调用同步解析接口

**默认（仅 Markdown）：**

```bash
curl -s -X POST "https://somark.tech/api/v1/extract/acc_sync" \
  -F "file=@/path/to/your/file.pdf" \
  -F "output_formats=markdown" \
  -F "api_key=${SOMARK_API_KEY}"
```

**同时获取 Markdown 和 JSON（仅在用户明确需要 JSON 时使用）：**

```bash
curl -s -X POST "https://somark.tech/api/v1/extract/acc_sync" \
  -F "file=@/path/to/your/file.pdf" \
  -F "output_formats=markdown" \
  -F "output_formats=json" \
  -F "api_key=${SOMARK_API_KEY}"
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | binary | ✅ | 待解析文件，支持 PDF、图片、Office 格式 |
| `output_formats` | array | ✅ | 输出格式，可选 `markdown` 和/或 `json`，至少选一个 |
| `api_key` | string | ✅ | SoMark API Key（`sk-...`） |

**限制：**
- 单文件最大 200MB
- 单文件最多 300 页
- 每账号 QPS 为 1

---

## 返回结果处理

成功响应结构：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "...",
    "result": {
      "file_name": "example.pdf",
      "imgs": ["https://..."],
      "outputs": {
        "markdown": "# 文档标题\n\n...",
        "json": { "pages": [...] }
      }
    },
    "error": null,
    "metadata": {
      "page_num": 5,
      "file_type": "pdf"
    }
  }
}
```

- 若用户要求 Markdown，提取 `data.result.outputs.markdown` 并直接展示。
- 若用户要求 JSON，提取 `data.result.outputs.json` 并格式化展示。
- 默认只请求 `markdown`（节省带宽），除非用户明确需要 JSON。
- `data.result.imgs` 为文档页面的图片 URL 列表，通常无需展示，除非用户明确要求查看原始页面图片。
- 若 `code` 不为 200，向用户展示 `message` 字段的错误信息，常见错误码：
  - `1107`：API Key 无效，引导用户重新检查配置
  - `2000`：请求参数校验失败（如缺少文件）
  - 文件超出大小（200MB）或页数（300页）限制时，告知用户限制并建议拆分文件
  - 不支持的文件格式时，告知用户支持的格式列表

---

## API Key 缺失处理

若 `SOMARK_API_KEY` 未配置（空或未设置），**不要**直接调用接口，而是：

1. 告知用户需要先配置 API Key。
2. 给出如下引导：

```
需要先配置 SoMark API Key 才能使用本功能。

请按以下步骤操作：
1. 访问 https://somark.tech 注册并获取 API Key（格式：sk-...）
2. 在 ~/.openclaw/openclaw.json 中添加：
   {
     "skills": {
       "entries": {
         "somark-document-parser": {
           "enabled": true,
           "apiKey": "sk-YOUR_API_KEY_HERE"
         }
       }
     }
   }
3. 重启 OpenClaw 会话后即可使用。
```

---

## 注意事项

- 不要对 API 返回的 Markdown 内容进行二次总结或改写，直接呈现原始解析结果。
- `file` 参数必须是本地文件的绝对路径，curl 中以 `@` 前缀传入（如 `-F "file=@/Users/xxx/doc.pdf"`），不支持传入 URL。
- 若用户提供的文件路径不存在，直接告知用户路径有误，不要尝试调用接口。
