"""本地 ASR（faster-whisper）。

为什么不用浏览器 Web Speech API：它走 Google 服务，中国大陆基本不可用。
本机有 RTX 5090 D，跑本地 Whisper 更快、更准、零网络依赖，
且 faster-whisper 自带 VAD，顺带解决「打断」需要的语音检测。
"""
from __future__ import annotations

import os

# 国内走镜像，避免 HF 下载失败
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from ..config import Settings  # noqa: E402

_MODEL = None
_MODEL_KEY: str | None = None


def load_model(settings: Settings):
    """懒加载模型（首次约需下载 1~3GB，之后走本地缓存）。"""
    global _MODEL, _MODEL_KEY
    key = f"{settings.asr_model}|{settings.asr_device}|{settings.asr_compute_type}"
    if _MODEL is not None and _MODEL_KEY == key:
        return _MODEL
    from faster_whisper import WhisperModel

    _MODEL = WhisperModel(
        settings.asr_model,
        device=settings.asr_device,
        compute_type=settings.asr_compute_type,
    )
    _MODEL_KEY = key
    return _MODEL


def transcribe(audio_path: str, settings: Settings, language: str = "zh") -> dict:
    """转写音频文件，返回 {text, language, duration}。

    vad_filter=True 会自动裁掉静音，同时给出语音段（可用于打断检测）。
    """
    model = load_model(settings)
    segments, info = model.transcribe(
        audio_path, language=language, vad_filter=True, beam_size=5
    )
    text = "".join(s.text for s in segments).strip()
    return {
        "text": text,
        "language": getattr(info, "language", language),
        "duration": getattr(info, "duration", 0.0),
    }


def warmup(settings: Settings) -> str:
    """预热：提前把模型加载好，避免第一次对话卡住。"""
    load_model(settings)
    return f"ASR 模型已加载：{settings.asr_model} @ {settings.asr_device}"
