# Voice Server v3 (Chatterbox, Optimized)

## Layout

- `voice_server_v3.py`: API routes and startup checks.
- `voice_engine.py`: synthesis engine, caching, and output handling.

## Install

```bash
python -m venv .venv
# mac/linux
source .venv/bin/activate
# windows powershell
# .\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install fastapi uvicorn chatterbox-tts torchaudio python-multipart
```

## Run

```bash
uvicorn voice_server_v3:app --host 127.0.0.1 --port 8000
```

Open Swagger docs at:
- http://127.0.0.1:8000/docs

## Endpoints

- `GET /health`
- `GET /benchmark`
- `POST /voice/register` (`voice_name`, `audio`)
- `POST /voice/warm` (`voice_name`)
- `POST /speak` (`text`, optional `voice_name`, `speed`, `exaggeration`, `cfg`) - returns `audio/ogg` (Opus)
- `POST /speak_stream` (same params as `/speak`) - chunked synthesis + Opus
- `POST /output/cleanup` (`path`) - delete staged opus and sidecar json

## Performance Notes

- Method lookup for optional Chatterbox APIs is cached once on startup.
- `torch.inference_mode()` is used during generation.
- Phrase cache is shared by `/speak` and `/speak_stream`.
- Improved chunking handles CJK text without whitespace more efficiently.
- Stage latency metrics are tracked for tuning via `/benchmark`.
