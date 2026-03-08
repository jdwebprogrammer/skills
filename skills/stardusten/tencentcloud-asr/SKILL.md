---
name: asr-sentence-recognition
description: >
  Skill for Tencent Cloud ASR (Automatic Speech Recognition). Provides three recognition modes:
  (1) SentenceRecognition for short audio ≤60s, (2) Flash ASR for fast synchronous recognition
  of audio ≤2h/100MB, (3) CreateRecTask for async recognition of long audio ≤5h.
  Use when: recognizing/transcribing speech from audio files, converting voice to text, speech
  recognition, generating subtitles, meeting transcription, or any audio-to-text tasks.
  Supports Chinese, English, Cantonese, Japanese, and 20+ other languages.
---

# 腾讯云语音识别 Skill

## 功能描述

本 Skill 提供**三种语音识别**能力，覆盖从短音频到超长录音的全场景需求：

| 场景 | API | 脚本 | 音频限制 | 返回方式 |
|------|-----|------|----------|----------|
| 短音频 | SentenceRecognition | `main.py` | ≤60s, ≤3MB | 同步 |
| 长音频极速 | Flash ASR | `flash_recognize.py` | ≤2h, ≤100MB | 同步 |
| 超长音频 | CreateRecTask | `file_recognize.py` | ≤5h (URL) / ≤5MB (上传) | 异步轮询 |

### 🎯 选择规则

```
音频 ≤60s  →  main.py（一句话识别，最简单）
60s < 音频 ≤2h  →  flash_recognize.py（极速版，同步快速返回）
音频 >2h 或需要高级功能  →  file_recognize.py（异步轮询，支持情绪识别/说话人分离等）
```

> 如果用户未指定使用哪种模式，Agent 应根据音频时长或文件大小自动选择合适的脚本。若无法判断时长，优先使用 `flash_recognize.py`。

### 支持特性

- **多语种**：中文普通话、英语、粤语、日语、韩语、法语、德语等 20+ 语种
- **多方言**：上海话、四川话、武汉话、南京话等 23 种方言
- **多格式**：wav、pcm、ogg-opus、speex、silk、mp3、m4a、aac、amr、flv、mp4、wma、3gp、flac
- **自动安装依赖**：首次运行时自动安装所需 SDK
- **智能凭证检测**：优先从环境变量获取密钥，仅在未配置时提示用户开通
- **自动格式检测**：根据文件扩展名自动推断音频格式

## 环境配置指引

### 密钥配置

本 Skill 需要腾讯云 API 密钥才能正常工作。

> ⚠️ **注意**：使用极速版（`flash_recognize.py`）**额外需要** `TENCENTCLOUD_APPID` 环境变量。

#### Step 1: 开通语音识别服务

🔗 **[腾讯云语音识别控制台](https://console.cloud.tencent.com/asr)**

#### Step 2: 获取 API 密钥

🔗 **[腾讯云 API 密钥管理](https://console.cloud.tencent.com/cam/capi)**

#### Step 3: 设置环境变量

**Linux / macOS：**
```bash
export TENCENTCLOUD_SECRET_ID="你的SecretId"
export TENCENTCLOUD_SECRET_KEY="你的SecretKey"
export TENCENTCLOUD_APPID="你的AppId"    # 仅极速版需要
```

如需持久化：
```bash
echo 'export TENCENTCLOUD_SECRET_ID="你的SecretId"' >> ~/.zshrc
echo 'export TENCENTCLOUD_SECRET_KEY="你的SecretKey"' >> ~/.zshrc
echo 'export TENCENTCLOUD_APPID="你的AppId"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell)：**
```powershell
$env:TENCENTCLOUD_SECRET_ID = "你的SecretId"
$env:TENCENTCLOUD_SECRET_KEY = "你的SecretKey"
$env:TENCENTCLOUD_APPID = "你的AppId"
```

> ⚠️ **安全提示**：切勿将密钥硬编码在代码中。

## Agent 执行指令（必读）

> ⚠️ **本节是 Agent（AI 模型）的核心执行规范。当用户提供音频并请求语音识别时，Agent 必须严格按照以下步骤自主执行，无需询问用户确认。**

### 🔑 通用执行规则

1. **触发条件**：用户提供了音频文件或音频 URL，且用户意图为语音转文本。
2. **零交互原则**：Agent 应直接执行脚本，不要向用户询问任何确认。
3. **自动选择脚本**：根据上方「选择规则」自动选择合适的脚本。
4. **⛔ 禁止使用大模型自身能力替代语音识别（最高优先级规则）**：
   - ASR 脚本调用失败时，**Agent 严禁自行猜测或编造识别内容**。
   - 如果调用失败，Agent **必须**向用户返回清晰的错误说明。

---

### 📌 脚本一：一句话识别 `main.py`

**适用场景**：≤60 秒短音频

```bash
python3 <SKILL_DIR>/scripts/main.py "<AUDIO_INPUT>"
```

**可选参数**：
- `--engine <TYPE>`：引擎类型，默认 `16k_zh`。常用：`16k_en`（英语）、`16k_yue`（粤语）、`16k_ja`（日语）
- `--format <FMT>`：音频格式，默认自动检测
- `--word-info <0|1|2>`：词级时间戳，0=关闭，1=开启，2=含标点

**输出示例**：
```json
{
  "result": "腾讯云语音识别欢迎您。",
  "audio_duration": 2430
}
```

---

### 📌 脚本二：极速版 `flash_recognize.py`

**适用场景**：60s ~ 2h 音频，需要快速同步返回结果

> ⚠️ 需要额外设置 `TENCENTCLOUD_APPID` 环境变量。

```bash
python3 <SKILL_DIR>/scripts/flash_recognize.py "<AUDIO_INPUT>"
```

**可选参数**：
- `--engine <TYPE>`：引擎类型，默认 `16k_zh`。支持大模型版：`16k_zh_large`、`16k_zh_en`、`16k_multi_lang`
- `--format <FMT>`：音频格式，默认自动检测
- `--word-info <0|1|2|3>`：词级时间戳，3=字幕模式
- `--speaker-diarization <0|1>`：说话人分离
- `--first-channel-only <0|1>`：仅识别首声道（默认 1）

**输出示例**：
```json
{
  "result": "腾讯云语音识别欢迎您。",
  "audio_duration": 2386,
  "request_id": "6098aecab9c686fbfd35adb0",
  "channels": [
    {
      "channel_id": 0,
      "text": "腾讯云语音识别欢迎您。"
    }
  ]
}
```

---

### 📌 脚本三：录音文件识别 `file_recognize.py`

**适用场景**：>2h 超长音频，或需要情绪识别、口语转书面语等高级功能

```bash
python3 <SKILL_DIR>/scripts/file_recognize.py "<AUDIO_URL_OR_FILE>"
```

**可选参数**：
- `--engine <TYPE>`：引擎类型，默认 `16k_zh`。支持大模型版：`16k_zh_large`、`8k_zh_large`
- `--channel-num <1|2>`：声道数，1=单声道，2=双声道（仅 8k）
- `--res-text-format <0-5>`：结果格式，0=基础，1-3=详细词级，4=语义分段，5=口语转书面
- `--speaker-diarization <0|1>`：说话人分离
- `--speaker-number <0-10>`：说话人数量，0=自动
- `--poll-interval <N>`：轮询间隔秒数，默认 5
- `--no-poll`：仅提交任务不轮询（返回 TaskId）

**输出示例**：
```json
{
  "task_id": 9266418,
  "status": "success",
  "result": "[0:0.020,0:2.380]  腾讯云语音识别欢迎您。\n",
  "audio_duration": 2.38
}
```

> **注意**：此接口为异步接口，脚本会自动轮询直到任务完成。长音频可能需要较长等待时间（1h 音频通常 1-3 分钟出结果）。

---

### 📋 完整调用示例

```bash
# 一句话识别（短音频）
python3 /path/to/scripts/main.py "https://example.com/short.wav"

# 极速版（长音频快速识别）
python3 /path/to/scripts/flash_recognize.py /path/to/meeting.mp3

# 极速版 + 说话人分离 + 字幕模式
python3 /path/to/scripts/flash_recognize.py --speaker-diarization 1 --word-info 3 /path/to/audio.wav

# 录音文件识别（超长音频）
python3 /path/to/scripts/file_recognize.py "https://cos.example.com/long-meeting.wav"

# 录音文件识别 + 详细结果 + 说话人分离
python3 /path/to/scripts/file_recognize.py --res-text-format 2 --speaker-diarization 1 "https://example.com/audio.wav"

# 仅提交任务不等待结果
python3 /path/to/scripts/file_recognize.py --no-poll "https://example.com/audio.wav"
```

### ❌ Agent 须避免的行为

- 只打印脚本路径而不执行
- 向用户询问"是否要执行语音识别"——应直接执行
- 手动安装依赖——脚本内部自动处理
- 忘记读取输出结果并返回给用户
- ASR 服务调用失败时，自行编造识别内容
- 未根据音频时长选择合适的脚本

## API 参考文档

详细的引擎类型、参数说明、错误码等信息请参阅 `references/` 目录下的文档：

- [一句话识别 API](references/sentence_recognition_api.md)（[原始文档](https://cloud.tencent.com/document/product/1093/35646)）
- [录音文件识别 API](references/file_recognition_api.md)（[创建任务](https://cloud.tencent.com/document/product/1093/37823) / [查询结果](https://cloud.tencent.com/document/product/1093/37822)）
- [录音文件识别极速版 API](references/flash_recognition_api.md)（[原始文档](https://cloud.tencent.com/document/product/1093/52097)）

## 核心脚本

- `scripts/main.py` — 一句话识别，≤60s 短音频同步识别
- `scripts/flash_recognize.py` — 极速版，≤2h 音频同步快速识别
- `scripts/file_recognize.py` — 录音文件识别，≤5h 音频异步轮询

## 依赖

- Python 3.7+
- `tencentcloud-sdk-python`（腾讯云 SDK，`main.py` 和 `file_recognize.py` 使用）
- `requests`（HTTP 库，`flash_recognize.py` 使用）

安装依赖（可选 - 脚本会自动安装）：
```bash
pip install tencentcloud-sdk-python requests
```
