from __future__ import annotations

from pathlib import Path
from typing import Dict

import torch
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from voice_engine import (
    DEFAULT_CFG,
    DEFAULT_EXAGGERATION,
    DEFAULT_SPEED,
    DEFAULT_VOICE_NAME,
    PIPELINE_SINGLE,
    PIPELINE_STREAM,
    VoiceEngine,
)


def pick_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


DEVICE = pick_device()
BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Tarvis Voice Server v3", version="3.3")
engine = VoiceEngine(device=DEVICE, base_dir=BASE_DIR)


def _opus_response(path: Path, headers: Dict[str, str]) -> FileResponse:
    return FileResponse(
        str(path),
        media_type="audio/ogg",
        filename=path.name,
        headers=headers,
    )


@app.on_event("startup")
def startup_checks():
    if not engine.ffmpeg_ok:
        raise RuntimeError("ffmpeg is required for Opus-only mode but was not found in PATH")
    if not engine.bootstrap_default_voice(DEFAULT_VOICE_NAME):
        raise RuntimeError("Default voice 'juno' not found. Place sample at local-voice-reply/voice/juno_ref.wav")


@app.get("/health")
def health():
    return {
        "ok": True,
        "device": DEVICE,
        "ffmpeg_ok": engine.ffmpeg_ok,
        "outputs_dir": str(engine.outputs_dir),
        "registered_voices": list(engine.voice_registry.keys()),
        "in_memory_cache": engine.cache.keys(),
        "encode_method": engine.encode_method_name,
        "generate_with_embedding_method": engine.generate_embedding_method_name,
        "benchmark": engine.benchmark_summary(),
    }


@app.get("/benchmark")
def benchmark():
    return {"ok": True, "summary": engine.benchmark_summary()}


@app.post("/voice/register")
async def register_voice(voice_name: str = Form(...), audio: UploadFile = File(...)):
    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty audio upload")
    return JSONResponse(engine.register_voice(voice_name, audio, data))


@app.post("/voice/warm")
def warm_voice(voice_name: str = Form(...)):
    if voice_name not in engine.voice_registry:
        raise HTTPException(status_code=404, detail=f"Voice '{voice_name}' not registered")
    emb = engine._load_or_build_embedding(voice_name)
    return {"ok": True, "voice_name": voice_name, "embedding_ready": emb is not None}


@app.post("/speak")
def speak(
    text: str = Form(...),
    voice_name: str = Form(DEFAULT_VOICE_NAME),
    speed: float = Form(DEFAULT_SPEED),
    exaggeration: float = Form(DEFAULT_EXAGGERATION),
    cfg: float = Form(DEFAULT_CFG),
):
    result = engine.synthesize(
        voice_name=voice_name,
        text=text,
        exaggeration=exaggeration,
        cfg=cfg,
        speed=speed,
    )
    out_file = Path(result["path"])
    meta = result["meta"]

    return _opus_response(
        out_file,
        headers={
            "X-Pipeline": PIPELINE_SINGLE,
            "X-Voice": voice_name,
            "X-Cache-Hits": str(meta.get("cache_hits", 0)),
            "X-Total-Ms": str(meta["latency_ms"].get("total_ms", 0)),
            "X-Speed": f"{float(meta.get('speed', DEFAULT_SPEED)):.2f}",
            "X-Output-Format": out_file.suffix.lstrip("."),
        },
    )


@app.post("/speak_stream")
def speak_stream(
    text: str = Form(...),
    voice_name: str = Form(DEFAULT_VOICE_NAME),
    speed: float = Form(DEFAULT_SPEED),
    exaggeration: float = Form(DEFAULT_EXAGGERATION),
    cfg: float = Form(DEFAULT_CFG),
):
    result = engine.synthesize_stream(
        voice_name=voice_name,
        text=text,
        exaggeration=exaggeration,
        cfg=cfg,
        speed=speed,
    )
    out_file = Path(result["path"])
    meta = result["meta"]

    return _opus_response(
        out_file,
        headers={
            "X-Pipeline": PIPELINE_STREAM,
            "X-Voice": voice_name,
            "X-Chunk-Count": str(meta.get("chunk_count", 0)),
            "X-Cache-Hits": str(meta.get("cache_hits", 0)),
            "X-Total-Ms": str(meta["latency_ms"].get("total_ms", 0)),
            "X-Speed": f"{float(meta.get('speed', DEFAULT_SPEED)):.2f}",
            "X-Output-Format": out_file.suffix.lstrip("."),
        },
    )


@app.post("/output/cleanup")
def cleanup_output(path: str = Form(...)):
    return JSONResponse(engine.cleanup_output(path))
