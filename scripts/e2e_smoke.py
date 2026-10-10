# -*- coding: utf-8 -*-
"""端到端冒烟：真实大模型 + 真实 MCP，跑一遍核心对话链路。

只走到「算价」为止，**不会创建订单**。
用法：python scripts/e2e_smoke.py
"""
import asyncio
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.config import settings  # noqa: E402
from server.dialog.engine import DialogEngine  # noqa: E402
from server.mcp_client import MCPClient  # noqa: E402
from server.memory.db import DB  # noqa: E402

TURNS = [
    "今天加班到九点，整个人都麻了",
    "那有什么吃的推荐吗，我想吃点实在的",
    "就麦辣鸡腿堡那个三件套吧，多少钱？",
]


async def main():
    mcp = MCPClient(settings)
    tools = await mcp.list_tools()
    print(f"MCP 已连接：{len(tools)} 个工具")
    print(f"LLM：{settings.llm_model} @ {settings.llm_base_url}")
    print("=" * 62)

    eng = DialogEngine(settings, mcp, DB(settings.db_path))
    sid = f"e2e-{int(time.time())}"   # 每次跑都用新会话，免得上一次的失败记录污染上下文
    for i, t in enumerate(TURNS, 1):
        print(f"\n[{i}] 👤 {t}")
        t0 = time.time()
        r = await eng.chat(sid, t)
        dt = time.time() - t0
        print(f"    🤖 {r['reply']}")
        print(f"    [stage={r['stage']} persona={r['persona']} {dt:.1f}s]")
        for c in r.get("cards") or []:
            print(f"    🃏 卡片：{c.get('image')}")


if __name__ == "__main__":
    asyncio.run(main())
