# -*- coding: utf-8 -*-
"""FastAPI 入口：WebSocket 收发音频/文本，串起 ASR → 对话引擎 → TTS。"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .dialog.engine import DialogEngine
from .mcp_client import MCPClient
from .memory.db import DB
from .voice import asr as asr_mod
from .voice.tts import synth

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
AUDIO_DIR = ROOT / "data" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="McDinnerMate", version="0.1.0")
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")
app.mount("/static", StaticFiles(directory=str(WEB)), name="static")

# 全局单例（MCP 无状态、引擎带会话状态）
mcp = MCPClient(settings)
db = DB(settings.db_path)
engine = DialogEngine(settings, mcp, db)


@app.on_event("startup")
async def _startup():
    await mcp.list_tools()          # 启动时把工具清单抓好


@app.get("/")
async def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/health")
async def health():
    return {"ok": True, "tools": len(mcp.tools),
            "store": settings.default_store_id, "persona": settings.portrait_mode}


@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())[:8]

    async def send(payload: dict):
        await ws.send_text(json.dumps(payload, ensure_ascii=False))

    await send({"type": "ready", "session_id": session_id})

    try:
        while True:
            msg = await ws.receive()

            if msg.get("type") == "websocket.disconnect":
                break

            # ---- 二进制：音频帧
            if msg.get("bytes"):
                raw = msg["bytes"]
                wav = AUDIO_DIR / f"{uuid.uuid4().hex}.webm"
                wav.write_bytes(raw)
                try:
                    r = asr_mod.transcribe(str(wav), settings)
                    text = r["text"]
                except Exception as e:                      # noqa: BLE001
                    await send({"type": "error", "message": f"语音识别失败：{e}"})
                    continue
                if not text:
                    await send({"type": "asr", "text": "", "empty": True})
                    continue
                await send({"type": "asr", "text": text})
                await _respond(ws, send, session_id, text)
                continue

            # ---- 文本控制消息
            if msg.get("text"):
                try:
                    data = json.loads(msg["text"])
                except json.JSONDecodeError:
                    continue
                t = data.get("type")
                if t == "text":
                    await _respond(ws, send, session_id, data.get("text", ""))
                elif t == "stop":
                    await send({"type": "stopped"})
                elif t == "reset":
                    db.clear_messages(session_id)
                    await send({"type": "reset", "ok": True})

    except WebSocketDisconnect:
        return


async def _respond(ws, send, session_id: str, text: str):
    await send({"type": "thinking"})
    try:
        r = await engine.chat(session_id, text)
    except Exception as e:                                  # noqa: BLE001
        await send({"type": "error", "message": str(e)[:200]})
        return

    audio_url = None
    if r["reply"]:
        p = await synth(r["reply"], str(AUDIO_DIR), settings.tts_voice)
        if p:
            audio_url = f"/audio/{Path(p).name}"

    await send({
        "type": "reply",
        "text": r["reply"],
        "audio": audio_url,
        "cards": r["cards"],
        "stage": r["stage"],
    })
