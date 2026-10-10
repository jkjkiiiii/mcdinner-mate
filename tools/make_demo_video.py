# -*- coding: utf-8 -*-
"""把 demo_raw/ 的真实界面截图合成为 1920×1080 的 Demo MP4。

- 旁白用 edge-tts（与产品同一套语音引擎，音色 zh-CN-XiaoxiaoNeural）
- 每幕时长由**旁白实际长度**驱动，字幕即旁白原文（静音观看也看得懂）
- 对真实推理耗时不加掩饰：字幕注明「真实本地推理 xx.xs，视频已加速」

前置：先跑 tools/record_demo.py 生成 demo_raw/
用法：
    ./.venv/Scripts/python.exe tools/make_demo_video.py
产出：
    assets/demo-video.mp4
    demo_raw/frames/*.png   最终画布帧（可单独复用为封面/截图）
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "demo_raw"
FRAMES = RAW / "frames"
TMP = RAW / "tmp"
ASSETS = ROOT / "assets"
OUT_MP4 = ASSETS / "demo-video.mp4"

W, H = 1920, 1080
BG = (18, 20, 26)
BG2 = (12, 13, 18)
LINE = (43, 47, 58)
TX = (230, 232, 238)
TX2 = (150, 158, 176)
AMBER = (255, 206, 122)
TERRA = (232, 146, 92)

F_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
F_REG = "C:/Windows/Fonts/msyh.ttc"
VOICE = "zh-CN-XiaoxiaoNeural"
FPS = 30


def f(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(F_BOLD if bold else F_REG, size)
    except OSError:
        return ImageFont.load_default()


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"命令失败: {' '.join(cmd[:6])}…\n{p.stderr[-800:]}")


def probe_duration(path: Path) -> float:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 3.0


# ---------------------------------------------------------------- 剧本

def load_scenes() -> list[dict]:
    turns = json.loads((RAW / "script.json").read_text(encoding="utf-8"))
    secs = {t["i"]: t["seconds"] for t in turns}

    def note(i: int) -> str:
        return f"真实本地推理 {secs.get(i, 0):.1f}s · 视频已加速"

    scenes = [
        dict(id="00_title", img=None, kind="title", hold=5.0,
             title="", caption="一个人吃饭，但不孤单。",
             note="2026 麦当劳程序员创意开发大赛",
             narr="一个人吃饭，但不孤单。这是麦麦陪餐搭子。"),
        dict(id="01_ready", img="01_ready.png", hold=7.5,
             title="打开就位",
             caption="全部跑在本地：本地大模型对话、本地语音识别，"
                     "只有点餐数据走麦当劳官方 MCP。",
             note="本地 Qwen3 27B + faster-whisper，对话与语音不出本机",
             narr="全部跑在本地：本地大模型负责对话，本地语音识别，"
                  "只有点餐数据走麦当劳官方 MCP。"),
        dict(id="02_recall", img="01c_reply.png", hold=9.0,
             title="它记得你",
             caption="你说加班到九点，它开口就提起你上次点的那份 —— "
                     "来自真实订单历史，不是人设扮演。",
             note=note(1), narr="你说加班到九点，它开口就提起你上次点的那份。"
                                "这不是人设扮演，是读了真实的订单历史。"),
        dict(id="03_price", img="02c_reply.png", hold=8.5,
             title="价格是真的",
             caption="价格来自官方菜单与算价接口：三十三块五，一个数字都不编。",
             note=note(2), narr="问多少钱，价格来自官方菜单与算价接口，"
                                "三十三块五，一个数字都不编。"),
        dict(id="04_order", img="03c_reply.png", hold=8.0,
             title="下单只到待支付",
             caption="说「店里吃」，订单直接建好 —— 只到待支付为止，"
                     "付款仍然在麦当劳官方 App 完成。",
             note=note(3), narr="说店里吃，订单就建好了，只到待支付为止。"
                                "付款仍然在麦当劳官方 App 完成。"),
        dict(id="05_order_card", img="03d_card.png", hold=9.0,
             title="订单确认卡片",
             caption="门店、取餐方式、金额、支付时限，全部来自官方订单详情接口，"
                     "不做任何占位。",
             note="本工具不代付、不保存任何支付信息",
             narr="门店、取餐方式、金额和支付时限，全部来自官方订单详情接口。"
                  "我们不代付，也不保存任何支付信息。"),
        dict(id="06_report", img="@report", hold=10.0,
             title="吃完有张卡",
             caption="热量取自官方营养接口，查不到就留空 —— 绝不填一个假数字。",
             note="饭后说一声即生成 1080×1080 分享卡",
             narr="吃完说一声，它生成一张饭后报告卡。热量取自官方营养接口，"
                  "查不到就留空，绝不填一个假数字。"),
        dict(id="07_outro", img=None, kind="outro", hold=8.0,
             title="",
             caption="代码全部开源，五个参赛交付文件齐备。"
                     "麦麦陪餐搭子，欢迎到 GitHub 点个 Star。",
             note="github.com/jkjkiiiii/mcdinner-mate",
             narr="代码全部开源，欢迎到 GitHub 点个 Star。"
                  "一个人吃饭，但不孤单。"),
    ]

    # 有真实仓库页截图就用真的（网络原因没截到则用生成的片尾卡）
    if (RAW / "07_repo.png").exists():
        scenes[-1]["img"] = "07_repo.png"
    return scenes


# ---------------------------------------------------------------- 画布

def rounded(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1],
                                           radius=radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if draw.textlength(cur + ch, font=font) > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def draw_title_card(sc: dict) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 2):                       # 纵向渐变
        t = y / H
        d.line([(0, y), (W, y)], fill=(
            int(BG[0] * (1 - t) + BG2[0] * t),
            int(BG[1] * (1 - t) + BG2[1] * t),
            int(BG[2] * (1 - t) + BG2[2] * t)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 6], fill=AMBER)

    # 吉祥物占位：同心圆
    cx, cy = W // 2, 400
    for r, col in ((132, (48, 44, 40)), (104, (72, 62, 52)), (76, TERRA)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    d.ellipse([cx - 20, cy - 30, cx + 20, cy + 10], fill=(255, 236, 210))

    t1 = f(72, True)
    d.text((W // 2, cy + 190), "麦麦陪餐搭子", font=t1, fill=TX, anchor="mm")
    d.text((W // 2, cy + 268), "一个人吃饭，但不孤单", font=f(36), fill=AMBER,
           anchor="mm")
    d.line([W // 2 - 150, cy + 320, W // 2 + 150, cy + 320], fill=LINE, width=2)
    d.text((W // 2, cy + 366), "McDinnerMate · 基于麦当劳 MCP 的语音陪餐搭子",
           font=f(26), fill=TX2, anchor="mm")
    d.text((W // 2, H - 92), "2026 麦当劳程序员创意开发大赛参赛作品",
           font=f(24), fill=TX2, anchor="mm")
    return img


def draw_outro_card(sc: dict) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 2):
        t = y / H
        d.line([(0, y), (W, y)], fill=(
            int(BG[0] * (1 - t) + BG2[0] * t),
            int(BG[1] * (1 - t) + BG2[1] * t),
            int(BG[2] * (1 - t) + BG2[2] * t)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 6], fill=AMBER)

    d.text((W // 2, 330), "麦麦陪餐搭子", font=f(66, True), fill=TX, anchor="mm")
    d.text((W // 2, 408), "McDinnerMate", font=f(30), fill=TX2, anchor="mm")
    d.line([W // 2 - 170, 456, W // 2 + 170, 456], fill=LINE, width=2)

    # 五项参赛交付物
    items = ["README.md", "CONTEST_DECLARATION.md", "MCP_INTEGRATION.md",
             "mcp-config.example.json", "workbuddy.md"]
    d.text((W // 2, 512), "参赛交付文件", font=f(24), fill=AMBER, anchor="mm")
    x0 = W // 2 - 560
    for i, it in enumerate(items):
        d.rounded_rectangle([x0 + i * 228, 552, x0 + i * 228 + 208, 600],
                            radius=10, outline=LINE, width=2, fill=(23, 25, 35))
        d.text((x0 + i * 228 + 104, 576), it, font=f(17), fill=TX2, anchor="mm")

    d.text((W // 2, 700), "github.com/jkjkiiiii/mcdinner-mate",
           font=f(34, True), fill=AMBER, anchor="mm")
    d.text((W // 2, 756), "⭐ 如果它让你觉得没那么孤单，欢迎点个 Star",
           font=f(26), fill=TX, anchor="mm")
    d.text((W // 2, H - 96), "一个人吃饭，但不孤单",
           font=f(28, True), fill=TX2, anchor="mm")
    return img


def resolve_src(sc: dict) -> Path | None:
    """`@report` 表示用真实产出的报告卡 PNG，而不是浏览器截图。"""
    if sc["img"] is None:
        return None
    if sc["img"] == "@report":
        cands = sorted((ROOT / "data").glob("report_*.png"),
                       key=lambda p: p.stat().st_mtime)
        return cands[-1] if cands else None
    p = RAW / sc["img"]
    return p if p.exists() else None


def draw_scene(sc: dict) -> Image.Image:
    if sc.get("kind") == "title":
        return draw_title_card(sc)
    if sc.get("kind") == "outro":
        return draw_outro_card(sc)

    src_path = resolve_src(sc)
    if src_path is None:
        return draw_title_card(sc)
    src = Image.open(src_path).convert("RGB")
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)

    # 截图区
    max_w, max_h = 1560, 878
    s = min(max_w / src.width, max_h / src.height)
    sw, sh = int(src.width * s), int(src.height * s)
    cap = rounded(src.resize((sw, sh), Image.LANCZOS), 14)
    cx, cy = (W - sw) // 2, 92
    d.rectangle([cx - 1, cy - 1, cx + sw, cy + sh], fill=LINE)   # 外描边
    canvas.paste(cap, (cx, cy), cap)

    # 顶栏
    d.text((60, 34), "麦麦陪餐搭子", font=f(30, True), fill=TX)
    d.text((60 + d.textlength("麦麦陪餐搭子", font=f(30, True)) + 16, 42),
           "McDinnerMate", font=f(20), fill=TX2)
    if sc.get("title"):
        d.text((W - 60, 44), sc["title"], font=f(24), fill=AMBER, anchor="rm")
    d.line([0, 78, W, 78], fill=LINE, width=2)

    # 字幕区
    cap_font, note_font = f(30), f(21)
    lines = wrap(d, sc["caption"], cap_font, W - 160)
    y = 1002
    for ln in lines[:2]:
        d.text((W // 2, y), ln, font=cap_font, fill=TX, anchor="mm")
        y += 42
    if sc.get("note"):
        d.text((W // 2, y + 4), sc["note"], font=note_font, fill=TX2, anchor="mm")

    d.rectangle([0, H - 6, W, H], fill=AMBER)
    return canvas


# ---------------------------------------------------------------- 主流程

def main() -> int:
    if not (RAW / "script.json").exists():
        print("❌ 缺少 demo_raw/script.json，请先跑 tools/record_demo.py")
        return 1
    FRAMES.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    for p in FRAMES.glob("*.png"):
        p.unlink()
    for p in TMP.glob("*"):
        p.unlink()

    sys.path.insert(0, str(ROOT))
    import asyncio

    import edge_tts

    scenes = load_scenes()

    async def gen_voice(text: str, out: Path) -> None:
        await edge_tts.Communicate(text, VOICE).save(str(out))

    segments: list[Path] = []
    for sc in scenes:
        frame = draw_scene(sc)
        fp = FRAMES / f"{sc['id']}.png"
        frame.save(fp)

        mp3 = TMP / f"{sc['id']}.mp3"
        try:
            asyncio.run(gen_voice(sc["narr"], mp3))
            nd = probe_duration(mp3)
        except Exception as e:                              # noqa: BLE001
            print(f"    ⚠️ 旁白合成失败（{sc['id']}）：{e}")
            nd = 0.0
        dur = max(nd + 1.0, sc["hold"])
        seg = TMP / f"{sc['id']}.mp4"

        if nd > 0:
            run(["ffmpeg", "-y", "-loop", "1", "-i", str(fp), "-i", str(mp3),
                 "-filter_complex",
                 f"[0:v]scale={W}:{H},format=yuv420p[v];"
                 f"[1:a]apad,atrim=0:{dur:.3f},asetpts=N/SR/TB[a]",
                 "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
                 "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
                 "-crf", "20", "-c:a", "aac", "-b:a", "160k",
                 "-ar", "44100", "-ac", "1", str(seg)])
        else:
            run(["ffmpeg", "-y", "-loop", "1", "-i", str(fp),
                 "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                 "-t", f"{dur:.3f}", "-r", str(FPS),
                 "-vf", f"scale={W}:{H},format=yuv420p",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                 "-c:a", "aac", "-b:a", "160k", "-shortest", str(seg)])
        print(f"    ✓ {sc['id']:<14} 旁白 {nd:4.1f}s → 镜头 {dur:4.1f}s")
        segments.append(seg)

    lst = TMP / "concat.txt"
    lst.write_text("".join(f"file '{s.as_posix()}'\n" for s in segments),
                   encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", "-movflags", "+faststart", str(OUT_MP4)])

    total = probe_duration(OUT_MP4)
    size = OUT_MP4.stat().st_size / 1024 / 1024
    print(f"\n✅ {OUT_MP4.relative_to(ROOT)}  {total:.1f}s  {size:.1f} MB  "
          f"{W}×{H}@{FPS}fps")
    shutil.rmtree(TMP, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
