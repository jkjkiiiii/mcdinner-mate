# -*- coding: utf-8 -*-
"""生成 README 用的演示素材。

产物：
  assets/demo-chat.gif      对话演示动图（README 直接播放）
  assets/demo-cover.png     封面图（首帧，用作视频 / 社交卡封面）

设计原则：**与 web/index.html 的视觉完全一致**（深色 + 琥珀强调），
让读者在 README 里看到的就是产品真实长相，而不是另画一套概念图。

对话内容取自 scripts/e2e_smoke.py 的真实实测记录（价格来自官方接口）。

用法：python tools/make_demo.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 视觉常量
# 全部取自 web/index.html 的 CSS 变量，勿随意改动
BG = "#12141a"
PANEL = "#1b1e26"
LINE = "#2b2f3a"
TX = "#e6e8ee"
TX2 = "#9aa1b2"
AMBER = "#ffce7a"
TERRA = "#e8925c"
USER_BG = "#2d3346"

W, H = 880, 560
SS = 3                      # 超采样倍数，避免圆角与文字锯齿
FONT = "C:/Windows/Fonts/msyh.ttc"
FONT_BD = "C:/Windows/Fonts/msyhbd.ttc"

HEADER_H = 64
FOOTER_H = 74
BUBBLE_R = 14
MAX_BUBBLE_W = 0.76         # 气泡最大宽度占内容区比例
PAD_X = 18                  # 气泡内水平内边距
PAD_Y = 13


def S(v: float) -> int:
    return int(round(v * SS))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BD if bold else FONT, S(size))


# ---------------------------------------------------------------- 对话数据
DIALOG: list[tuple[str, str]] = [
    ("user", "今天加班到九点，整个人都麻了"),
    ("bot", "辛苦了，加到九点是真的累。\n先别想别的，饿了吧？我看你上次还点的"
            "随心配加麦辣鸡翅，老样子再来一份？"),
    ("user", "就麦辣鸡腿堡那个三件套吧，多少钱？"),
    ("bot", "麦辣鸡腿汉堡三件套，¥33.5，没额外优惠。\n你是店里吃还是打包带走？"),
]


def wrap(draw: ImageDraw.ImageDraw, text: str, f, max_w: int) -> list[str]:
    """按像素宽度折行（中文无空格，只能逐字量）。"""
    lines: list[str] = []
    for para in text.split("\n"):
        cur = ""
        for ch in para:
            if draw.textlength(cur + ch, font=f) <= max_w:
                cur += ch
            else:
                lines.append(cur)
                cur = ch
        lines.append(cur)
    return lines


def bubble_size(draw, text: str, f, content_w: int):
    max_text_w = int(content_w * MAX_BUBBLE_W) - 2 * PAD_X * SS
    lines = wrap(draw, text, f, max_text_w)
    w = max(draw.textlength(ln, font=f) for ln in lines) + 2 * PAD_X * SS
    lh = f.size * 1.62
    h = len(lines) * lh + 2 * PAD_Y * SS
    return int(w), int(h), lines, lh


def draw_bubble(im: Image.Image, text: str, f, x: int, y: int,
                content_w: int, is_user: bool) -> tuple[int, int]:
    """画一个聊天气泡，返回 (宽, 高)。x 为气泡左边缘。"""
    d = ImageDraw.Draw(im)
    w, h, lines, lh = bubble_size(d, text, f, content_w)
    if is_user:
        d.rounded_rectangle([x, y, x + w, y + h], radius=S(BUBBLE_R), fill=USER_BG)
    else:
        d.rounded_rectangle([x, y, x + w, y + h], radius=S(BUBBLE_R),
                            fill=PANEL, outline=LINE, width=S(1))
    ty = y + PAD_Y * SS
    for ln in lines:
        d.text((x + PAD_X * SS, ty), ln, font=f, fill=TX)
        ty += lh
    return w, h


def draw_frame(messages: list[tuple[str, str]], thinking: int = 0) -> Image.Image:
    """渲染一帧。thinking=0 表示不显示；1..3 表示思考动画的点亮个数。

    消息**自下而上堆叠**（像真实聊天窗口），这样消息少时不会头顶一大片空白。
    """
    im = Image.new("RGB", (W * SS, H * SS), BG)
    d = ImageDraw.Draw(im)
    content_w = W * SS
    f = font(15)
    gap = S(12)

    # ---- header
    d.rectangle([0, 0, W * SS, S(HEADER_H)], fill=BG)
    d.line([0, S(HEADER_H), W * SS, S(HEADER_H)], fill=LINE, width=S(1))
    # 头像：琥珀圆团（对应前端 mascot.svg「光团子」的简化占位）
    cx, cy, r = S(38), S(32), S(17)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)
    d.ellipse([cx - S(7), cy - S(9), cx + S(7), cy + S(5)], fill="#7a5a20")
    d.text((S(66), S(15)), "麦麦陪餐搭子", font=font(17, True), fill=TX)
    d.text((S(66), S(38)), "一个人吃饭，但不孤单", font=font(12), fill=TX2)

    # ---- 先算总高，再决定起始 y（内容不足则贴底）
    blocks = []
    for role, text in messages:
        w, h, lines, lh = bubble_size(d, text, f, content_w)
        blocks.append(("b", role, text, w, h, lines, lh))
    if thinking:
        blocks.append(("t", None, None, S(76), S(42), None, None))

    total_h = sum(b[4] for b in blocks) + gap * max(0, len(blocks) - 1)
    chat_top = S(HEADER_H + 20)
    chat_bottom = H * SS - S(FOOTER_H + 20)
    y = max(chat_top, chat_bottom - total_h)

    # ---- 绘制
    for kind, role, text, w, h, lines, lh in blocks:
        if kind == "b":
            x = content_w - S(22) - w if role == "user" else S(22)
            draw_bubble(im, text, f, x, y, content_w, role == "user")
        else:                                   # 思考中的三点动画
            x = S(22)
            d.rounded_rectangle([x, y, x + w, y + h], radius=S(BUBBLE_R),
                                fill=PANEL, outline=LINE, width=S(1))
            for i in range(3):
                dot_r = S(4.5)
                dx = x + S(20) + i * S(18)
                dy = y + h // 2
                lit = i < thinking
                rr = dot_r * (1.25 if lit else 1.0)
                d.ellipse([dx - rr, dy - rr, dx + rr, dy + rr],
                          fill=AMBER if lit else "#3d4352")
        y += h + gap

    # ---- footer
    fy = H * SS - S(FOOTER_H)
    d.rectangle([0, fy, W * SS, H * SS], fill=BG)
    d.line([0, fy, W * SS, fy], fill=LINE, width=S(1))
    # 麦克风按钮（不用 emoji：PIL 渲染色 emoji 不可靠）
    mx, my, mr = S(20), fy + S(9), S(28)
    d.ellipse([mx, my, mx + mr * 2, my + mr * 2], fill=AMBER)
    ccx, ccy = mx + mr, my + mr
    d.rounded_rectangle([ccx - S(5), ccy - S(11), ccx + S(5), ccy + S(3)],
                        radius=S(5), fill="#201a0c")
    d.arc([ccx - S(9), ccy - S(4), ccx + S(9), ccy + S(10)],
          start=0, end=180, fill="#201a0c", width=S(2.5))
    d.line([ccx, ccy + S(10), ccx, ccy + S(15)], fill="#201a0c", width=S(2.5))
    # 输入框
    ix = mx + mr * 2 + S(12)
    d.rounded_rectangle([ix, my, W * SS - S(20), my + mr * 2],
                        radius=S(10), fill=PANEL, outline=LINE, width=S(1))
    d.text((ix + S(14), my + S(13)), "今天怎么样？想吃点啥…",
           font=font(15), fill=TX2)

    return im.resize((W, H), Image.LANCZOS)


def draw_endcard() -> Image.Image:
    """收尾卡：把「数据是真的」这个最容易被忽略的卖点讲清楚。"""
    im = Image.new("RGB", (W * SS, H * SS), BG)
    d = ImageDraw.Draw(im)
    cx = W * SS // 2

    r = S(36)
    cy = S(150)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)
    d.ellipse([cx - S(14), cy - S(18), cx + S(14), cy + S(10)], fill="#7a5a20")

    def center(text: str, y: int, f, fill: str) -> None:
        w = d.textlength(text, font=f)
        d.text((cx - w / 2, S(y)), text, font=f, fill=fill)

    center("数据全部来自麦当劳官方 MCP", 250, font(23, True), TX)
    center("历史订单 · 营养热量 · 实时价格 · 优惠券", 296, font(15), AMBER)
    d.line([cx - S(230), S(340), cx + S(230), S(340)], fill=LINE, width=S(1))
    center("所以它真的记得你 —— 不是人设扮演", 366, font(15), TX2)
    return im.resize((W, H), Image.LANCZOS)


# ---------------------------------------------------------------- 产品一图流
SHOWCASE_BANDS = [
    {
        "no": "01",
        "title": "它记得你",
        "desc": "开场就提起你上次点的东西。\n"
                "全部来自 order-list 真实订单，\n"
                "不是人设扮演。",
        "qa": ("今天加班到九点，整个人都麻了",
               "辛苦了，加到九点是真的累。\n我看你上次还点的随心配加麦辣鸡翅，"
               "老样子再来一份？"),
    },
    {
        "no": "02",
        "title": "价格是真的",
        "desc": "菜单与算价全走官方接口。\n"
                "¥33.5 与接口返回的 4150 分\n"
                "严格一致，一个数字都不编。",
        "qa": ("就麦辣鸡腿堡那个三件套吧，多少钱？",
               "麦辣鸡腿汉堡三件套，¥33.5，没额外优惠。\n你是店里吃还是打包带走？"),
    },
    {
        "no": "03",
        "title": "吃完有张卡",
        "desc": "饭后生成 1080×1080 分享卡。\n"
                "热量取自官方营养接口，查不到\n"
                "就留空 —— 绝不填一个假数字。",
        "image": "report-card-sample.png",
    },
]


def make_showcase() -> None:
    """生成 assets/demo-showcase.png：左侧界面片段 + 右侧卖点说明。"""
    SW, PAD, GAP, BAND_H, LEFT_W = 1080, 40, 24, 300, 560
    RIGHT_X = PAD + LEFT_W + 40
    RIGHT_W = SW - RIGHT_X - PAD
    HEAD_H, FOOT_H = 118, 56
    SH = HEAD_H + len(SHOWCASE_BANDS) * BAND_H + (len(SHOWCASE_BANDS) - 1) * GAP + FOOT_H

    im = Image.new("RGB", (SW * SS, SH * SS), BG)
    d = ImageDraw.Draw(im)

    d.text((S(PAD), S(40)), "麦麦陪餐搭子 · 一次完整的陪餐",
           font=font(27, True), fill=TX)
    d.text((S(PAD), S(82)), "从「今天吃啥」到「吃完这张卡」—— 全程真实数据，不是剧本",
           font=font(15), fill=TX2)

    f_title = font(21, True)
    f_desc = font(15)
    f_no = font(26, True)
    f_bub = font(16)

    for i, band in enumerate(SHOWCASE_BANDS):
        y = HEAD_H + i * (BAND_H + GAP)
        # 卡片底
        d.rounded_rectangle([S(PAD - 14), S(y), S(SW - PAD + 14), S(y + BAND_H)],
                            radius=S(18), fill=PANEL, outline=LINE, width=S(1))

        # ---- 左：界面片段
        lx = PAD + 6
        ly = y + 20
        lw = LEFT_W - 12
        lh = BAND_H - 40
        if band.get("qa"):
            user_text, bot_text = band["qa"]
            content_w = lw * SS
            # 先量高度，再垂直居中
            uw, uh, _, _ = bubble_size(d, user_text, f_bub, content_w)
            bw, bh, _, _ = bubble_size(d, bot_text, f_bub, content_w)
            total = uh + bh + S(14)
            cy = ly * SS + (lh * SS - total) // 2
            draw_bubble(im, user_text, f_bub, S(lx + lw) - uw, int(cy), content_w, True)
            draw_bubble(im, bot_text, f_bub, S(lx), int(cy + uh + S(14)), content_w, False)
        else:
            src = Image.open(OUT / band["image"]).convert("RGB")
            # 注意：(lh/lw 是逻辑尺寸) 必须乘 SS 才能对上超采样坐标系，
            # 否则图片会被缩到 1/SS —— 第一版就踩了这个坑。
            scale = min((lh * SS) / src.height, (lw * SS) / src.width)
            rs = src.resize((int(src.width * scale), int(src.height * scale)),
                            Image.LANCZOS)
            im.paste(rs, (S(lx) + (S(lw) - rs.width) // 2,
                          S(ly) + (S(lh) - rs.height) // 2))

        # ---- 右：序号 / 标题 / 说明
        rx = RIGHT_X
        d.text((S(rx), S(y + 52)), band["no"], font=f_no, fill=AMBER)
        d.text((S(rx + 52), S(y + 60)), band["title"], font=f_title, fill=TX)
        d.line([S(rx), S(y + 104), S(rx + RIGHT_W * 0.9), S(y + 104)],
               fill=LINE, width=S(1))
        ty = y + 128
        for ln in band["desc"].split("\n"):
            d.text((S(rx), S(ty)), ln, font=f_desc, fill=TX2)
            ty += 27

    d.text((S(PAD), S(SH - 40)),
           "对话与价格为真实实测记录 · 数据源：麦当劳 MCP（mcp.mcd.cn）",
           font=font(13), fill=TX2)

    im.resize((SW, SH), Image.LANCZOS).save(OUT / "demo-showcase.png")
    print(f"✓ demo-showcase.png {SW}×{SH}")


def main() -> None:
    frames: list[Image.Image] = []
    durations: list[int] = []

    def add(msgs, ms, thinking=0):
        frames.append(draw_frame(msgs, thinking))
        durations.append(ms)

    # 开场：只有界面
    add([], 900)

    # 逐条推进
    shown: list[tuple[str, str]] = []
    for i, (role, text) in enumerate(DIALOG):
        # AI 回复前先播思考中
        if role == "bot":
            for t in (1, 2, 3):
                add(list(shown), 220, thinking=t)
        shown.append((role, text))
        add(list(shown), 2300 if role == "bot" else 1500)

    # 结尾停留
    add(list(shown), 2600)

    # 收尾卡：讲清「这些数据是真的」
    frames.append(draw_endcard())
    durations.append(2800)

    # 封面取对话最满的那帧（不是收尾卡）
    cover_idx = len(frames) - 2
    frames[cover_idx].save(OUT / "demo-cover.png")

    frames[0].save(
        OUT / "demo-chat.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    kb = (OUT / "demo-chat.gif").stat().st_size / 1024
    print(f"✓ demo-chat.gif    {len(frames)} 帧 / {sum(durations)/1000:.1f}s / {kb:.0f} KB")
    print(f"✓ demo-cover.png   {frames[cover_idx].size}")
    make_showcase()


if __name__ == "__main__":
    main()
