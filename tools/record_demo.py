# -*- coding: utf-8 -*-
"""Demo 视频素材采集：用 Playwright 驱动**真实前端**走完整剧本，逐幕截图。

不是画概念图 —— 每一帧都是真实运行的界面：真实本地大模型、真实麦当劳 MCP。

前置：服务已启动
    ./.venv/Scripts/python.exe -m uvicorn server.main:app --port 8010

用法：
    ./.venv/Scripts/python.exe tools/record_demo.py
产出：
    demo_raw/*.png        逐幕截图（2560×1440，viewport 1280×720 @ dsf=2）
    demo_raw/script.json  每轮真实文本 + 真实推理耗时（用于字幕与「已加速」说明）
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo_raw"
BASE = "http://127.0.0.1:8010"
REPO = "https://github.com/jkjkiiiii/mcdinner-mate"

VIEWPORT = {"width": 1280, "height": 720}
DSF = 2                      # 2 倍像素密度 → 2560×1440，缩到 1080p 更锐

# 用系统已装好的 Chromium 内核浏览器，避免下载 Playwright 自带 chromium
# （国内直连 CDN 实测 stalled，4 分钟 0 字节）。按顺序找第一个存在的。
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Users\28607\AppData\Local\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_browser() -> str | None:
    import os
    for p in BROWSERS:
        if os.path.exists(p):
            return p
    return None

# 剧本：与 README / SKILL.md 里对外宣称的场景完全一致
SCRIPT = [
    "今天加班到九点，累死了",
    "就麦辣鸡腿堡那个三件套吧，多少钱？",
    "店里吃",
    "我吃完了，走人",
]

TURN_TIMEOUT = 240_000       # 单轮最长等待（真实推理 + 工具往返）


def shot(page: Page, name: str) -> None:
    page.screenshot(path=str(OUT / f"{name}.png"))
    print(f"    📸 {name}.png")


def wait_bubbles(page: Page, cls: str, n: int) -> None:
    page.wait_for_function(
        "([cls, n]) => document.querySelectorAll('.bubble.' + cls).length >= n",
        arg=[cls, n], timeout=TURN_TIMEOUT,
    )


def main() -> int:
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    turns: list[dict] = []

    with sync_playwright() as p:
        exe = find_browser()
        if exe:
            print(f"浏览器：{exe}")
        browser = p.chromium.launch(headless=True, executable_path=exe)
        ctx = browser.new_context(
            viewport=VIEWPORT, device_scale_factor=DSF,
            color_scheme="dark", locale="zh-CN",
        )
        page = ctx.new_page()

        # ---------- 第 0 幕：连接就位
        page.goto(BASE, wait_until="load")
        page.wait_for_function(
            "() => [...document.querySelectorAll('.bubble.sys')]"
            ".some(e => e.textContent.includes('已就位'))",
            timeout=60_000,
        )
        page.wait_for_timeout(900)
        shot(page, "01_ready")

        # ---------- 逐轮对话
        for i, text in enumerate(SCRIPT, start=1):
            n_bot_before = page.eval_on_selector_all(".bubble.bot", "els => els.length")
            n_card_before = page.eval_on_selector_all(".card", "els => els.length")

            page.fill("#txt", text)
            page.wait_for_timeout(260)
            shot(page, f"{i:02d}a_user")
            page.press("#txt", "Enter")

            # 「…」思考态：抓一帧
            try:
                wait_bubbles(page, "sys", 1)
            except Exception:                               # noqa: BLE001
                pass
            page.wait_for_timeout(700)
            shot(page, f"{i:02d}b_thinking")

            t0 = time.perf_counter()
            page.wait_for_function(
                "n => document.querySelectorAll('.bubble.bot').length > n",
                arg=n_bot_before, timeout=TURN_TIMEOUT,
            )
            elapsed = time.perf_counter() - t0
            page.wait_for_timeout(700)
            shot(page, f"{i:02d}c_reply")

            reply = page.eval_on_selector_all(
                ".bubble.bot", "els => els[els.length - 1].textContent"
            )
            cards = page.eval_on_selector_all(
                ".card", "els => els.map(e => e.innerText)"
            )
            label = "order" if i == 3 else ("report" if i == 4 else "chat")
            turns.append({"i": i, "user": text, "reply": reply,
                          "cards": cards, "seconds": round(elapsed, 1),
                          "label": label})
            print(f"    ✓ 第 {i} 轮 {elapsed:.1f}s  → {reply[:40]}…")

            # 卡片刚出现时它就在视口底部 —— 此刻定格最完整。
            # （事后滚动定位不可靠：后续轮次会把日志继续往下推）
            if page.eval_on_selector_all(".card", "els => els.length") > n_card_before:
                page.wait_for_timeout(500)
                shot(page, f"{i:02d}d_card")

        # ---------- 报告卡大图（真实产出的 PNG）
        reports = sorted((ROOT / "data").glob("report_*.png"),
                         key=lambda p: p.stat().st_mtime)
        if reports:
            page.goto(f"{BASE}/audio/{reports[-1].name}", wait_until="load")
            page.wait_for_timeout(700)
            shot(page, "06_report_card")
            print(f"    📸 报告卡大图 {reports[-1].name}")

        # ---------- 收尾：仓库页（可选；失败不影响正片，视频会用生成的片尾卡兜底）
        try:
            page.goto(REPO, wait_until="domcontentloaded", timeout=25_000)
            page.wait_for_timeout(3000)
            shot(page, "07_repo")
        except Exception as e:                              # noqa: BLE001
            print(f"    ⚠️ 仓库页截图失败（片尾将用生成的品牌卡代替）："
                  f"{str(e)[:80]}")

        browser.close()

    (OUT / "script.json").write_text(
        json.dumps(turns, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total = sum(t["seconds"] for t in turns)
    print(f"\n素材完成 → {OUT}")
    print(f"真实推理总耗时 {total:.1f}s（视频将做加速说明，不假装实时）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
