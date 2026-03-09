---
name: local-voice-reply
description: Generate Feishu voice replies in user required voice. Generate OPUS file to match Feishu audio.
---

# Local Voice Reply

Use this skill to turn text into a cloned-voice audio reply and deliver it to Feishu reliably.

Server implementation is kept with the skill (not workspace root):
- `server/voice_server_v3.py` (FastAPI routes)
- `server/voice_engine.py` (generation and cache engine)

Voice assets are also colocated with the skill:
- `voice/`

## Use this workflow

1. Ensure local **v3.3** TTS server is running from this skill folder:
   - `python -m uvicorn --app-dir server voice_server_v3:app --host 127.0.0.1 --port 8000`
2. Call `/speak` with `text` (and optional `speed`, `exaggeration`, `cfg`).
   - `voice_name` defaults to `juno`.
3. Receive **Opus directly** from server (`audio/ogg`) in Juno voice.
4. Save final media into allowed path:
   - `C:\Users\hanli\.openclaw\media\outbound\`
5. Send with `message` tool:
   - `action=send`
   - `channel=feishu`
   - `filePath=<allowed-path>`
   - `asVoice=true`

## Defaults

- `voice_name`: `juno`
- `speed`: `1.2`
- Output format: Opus from server `/speak` (no post-conversion)

## Speed Improvements In This Version

- Caches model capability lookups once at startup.
- Uses `torch.inference_mode()` during synthesis to reduce overhead.
- Reuses phrase cache for both `/speak` and `/speak_stream`.
- Improves chunking behavior for long CJK text to avoid oversized chunks.
- Keeps latency metrics for benchmarking and tuning.

## Common failure and fix

- Error: `LocalMediaAccessError ... path-not-allowed`
- Fix: copy the file into `.openclaw/media/outbound` before sending.

## Script

Use `scripts/send_voice_reply.ps1` to generate Opus directly with defaults (`voice_name=juno`, `speed=1.2`).
It auto-selects `/speak_stream` for longer text (or when `-Stream` is passed) for better throughput.
