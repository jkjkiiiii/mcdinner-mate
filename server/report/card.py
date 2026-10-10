"""饭后分享报告卡：1080×1080 PNG。

内容：吃了什么 / 热量 / 今日心情关键词 / 一句麦门金句。
⚠️ 不使用任何品牌 Logo 或商标图形。
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1080
BG_TOP = (23, 25, 43)
BG_BOT = (15, 16, 28)
CREAM = (255, 246, 226)
AMBER = (255, 206, 122)
TERRA = (232, 146, 92)
MUTED = (150, 158, 176)
WHITE = (255, 252, 245)

# ⚠️ 金句只谈陪伴与情绪，不评价品牌与餐品，不鼓吹多吃
QUOTES = [
    "一个人吃饭，但不孤单。",
    "今天的饭有我陪着吃完了。",
    "吃饱了，才有力气跟生活过招。",
    "这顿饭的热量表我记下了，明天见。",
    "加班很晚，但饭是热的。",
    "你已经很努力了，慢慢吃。",
]

_FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
_FONT_REG = "C:/Windows/Fonts/msyh.ttc"


def _f(size: int, bold: bool = False):
    try:
        return ImageFont.truetype(_FONT_BOLD if bold else _FONT_REG, size)
    except OSError:
        return ImageFont.load_default()


def render_card(
    items: list[str],
    kcal: int | None = None,
    mood: str | None = None,
    quote: str | None = None,
    date: str | None = None,
    out_path: str | Path = "report_card.png",
) -> Path:
    img = Image.new("RGB", (W, H), BG_TOP)
    d = ImageDraw.Draw(img)

    # 竖向渐变背景
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)],
               fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))

    # 顶部暖光晕（呼应吉祥物）
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W // 2 - 260, -200, W // 2 + 260, 320], fill=(255, 201, 107, 42))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    x = 96
    y = 140

    d.text((x, y), "今日陪餐报告", font=_f(46, True), fill=AMBER)
    y += 84
    if date:
        d.text((x, y), date, font=_f(28), fill=MUTED)
        y += 72

    # 分隔线
    d.line([(x, y), (W - x, y)], fill=(60, 64, 84), width=2)
    y += 56

    d.text((x, y), "吃了什么", font=_f(30), fill=MUTED)
    y += 56
    if items:
        for it in items[:5]:
            d.text((x + 8, y), f"· {it}", font=_f(38), fill=WHITE)
            y += 62
    else:
        d.text((x + 8, y), "· 今天没记录到餐品", font=_f(38), fill=MUTED)
        y += 62

    y += 40
    if kcal is not None:
        d.text((x, y), "热量", font=_f(30), fill=MUTED)
        y += 56
        d.text((x, y), f"{kcal}", font=_f(88, True), fill=AMBER)
        d.text((x + 262, y + 40), "kcal", font=_f(36), fill=MUTED)
        y += 140

    if mood:
        d.text((x, y), "今日心情", font=_f(30), fill=MUTED)
        y += 56
        d.text((x, y), mood, font=_f(44, True), fill=TERRA)
        y += 96

    # 底部金句
    q = quote or random.choice(QUOTES)
    d.line([(x, H - 210), (W - x, H - 210)], fill=(60, 64, 84), width=2)
    d.text((x, H - 168), q, font=_f(40, True), fill=CREAM)
    d.text((x, H - 104), "麦麦陪餐搭子 · McDinnerMate", font=_f(26), fill=MUTED)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out
