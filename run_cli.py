# -*- coding: utf-8 -*-
"""命令行跑通全流程（不开语音），用于 Phase 2 验收。

用法：
    python run_cli.py
    python run_cli.py --stage        # 打印每轮阶段变化，便于调试状态机
"""
import argparse
import asyncio

from server.config import settings
from server.dialog.engine import DialogEngine
from server.mcp_client import MCPClient
from server.memory.db import DB


async def main(show_stage: bool = False):
    mcp = MCPClient(settings)
    tools = await mcp.list_tools()
    print(f"✅ MCP 已连接：{len(tools)} 个工具\n")

    engine = DialogEngine(settings, mcp, DB(settings.db_path))
    sid = "cli"
    print("麦麦陪餐搭子已就位（输入 q 退出）")
    print("─" * 50)

    while True:
        try:
            user = input("👤 ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in ("q", "quit", "exit"):
            break
        if not user:
            continue
        try:
            r = await engine.chat(sid, user)
        except Exception as e:                              # noqa: BLE001
            print(f"🤖 （出错了：{type(e).__name__}: {e}）")
            continue
        if show_stage:
            print(f"   [stage={r['stage']} persona={r['persona']}]")
        print(f"🤖 {r['reply']}")
        for c in r["cards"]:
            print(f"   🃏 卡片已生成：{c['image']}")
        print()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", action="store_true", help="显示阶段变化")
    a = ap.parse_args()
    asyncio.run(main(a.stage))
