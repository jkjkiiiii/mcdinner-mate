# -*- coding: utf-8 -*-
"""本地 ASR 冒烟：把一段中文语音转成文字，验证语音链路。

用法：python scripts/asr_check.py [音频路径]
默认用 docs/samples/asr_test.mp3（由 edge-tts 生成，不入库）。
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.config import settings  # noqa: E402
from server.voice import asr  # noqa: E402


def main():
    audio = sys.argv[1] if len(sys.argv) > 1 else str(
        ROOT / "docs" / "samples" / "asr_test.mp3"
    )
    if not Path(audio).exists():
        print(f"❌ 找不到音频：{audio}")
        return
    print(f"模型：{settings.asr_model}")
    print(f"设备：{settings.asr_device} / {settings.asr_compute_type}")
    print(f"音频：{audio}\n正在加载模型（首次约 10~30 秒）…")

    t0 = time.time()
    r = asr.transcribe(audio, settings)
    print(f"\n⏱  耗时 {time.time() - t0:.1f}s")
    print(f"📝 识别：{r['text']}")
    print(f"   语言={r['language']}  音频时长={r['duration']:.1f}s")


if __name__ == "__main__":
    main()
