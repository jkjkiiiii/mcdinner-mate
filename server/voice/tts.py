"""TTS：edge-tts 为主，浏览器 speechSynthesis 为前端兜底。

edge-tts 免费无需申请 Key；若出现 403/限流，前端会自动切到浏览器合成。
"""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path


async def synth(text: str, out_dir: str, voice: str = "zh-CN-XiaoxiaoNeural") -> str | None:
    """把文本合成成 mp3，返回文件路径；失败返回 None（由前端兜底）。"""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out = Path(out_dir) / f"{uuid.uuid4().hex}.mp3"
    try:
        import edge_tts

        comm = edge_tts.Communicate(text, voice)
        await comm.save(str(out))
        return str(out)
    except Exception:                                       # noqa: BLE001
        return None


def synth_sync(text: str, out_dir: str, voice: str) -> str | None:
    return asyncio.run(synth(text, out_dir, voice))
