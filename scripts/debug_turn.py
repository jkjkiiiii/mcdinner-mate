# -*- coding: utf-8 -*-
"""单轮调试：逐轮打印大模型的 tool_calls 与 finish_reason。

定位「模型反复调工具却给不出回复」这类问题。
用法：python scripts/debug_turn.py "就麦辣鸡腿堡那个三件套吧，多少钱？"
"""
import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.config import settings  # noqa: E402
from server.dialog.engine import MAX_ROUNDS, DialogEngine  # noqa: E402
from server.mcp_client import MCPClient  # noqa: E402
from server.memory.db import DB  # noqa: E402


async def main():
    text = sys.argv[1] if len(sys.argv) > 1 else "就麦辣鸡腿堡那个三件套吧，多少钱？"
    mcp = MCPClient(settings)
    await mcp.list_tools()
    eng = DialogEngine(settings, mcp, DB(settings.db_path))

    state = eng.sm.get("dbg")
    state.stage = "RECO"
    messages = [
        {"role": "system", "content": eng._system(state, await eng._profile_text())},
        {"role": "user", "content": text},
    ]
    tools = eng._tools_for(state)
    print(f"可用工具 {len(tools)} 个 | 阶段 {state.stage}")
    print(f"用户：{text}\n" + "=" * 62)

    for i in range(MAX_ROUNDS):
        t0 = time.time()
        resp = await eng.llm.chat.completions.create(
            model=settings.llm_model, messages=messages, tools=tools,
            tool_choice="auto", temperature=0.7, max_tokens=768,
        )
        ch = resp.choices[0]
        msg = ch.message
        dt = time.time() - t0
        print(f"[轮 {i+1}] {dt:.1f}s  finish={ch.finish_reason}")
        if msg.content:
            print(f"   文本: {msg.content[:120]}")
        if not msg.tool_calls:
            print("   → 无工具调用，循环结束")
            break
        messages.append(msg.model_dump(exclude_none=True))
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            print(f"   调用: {tc.function.name}  args={json.dumps(args, ensure_ascii=False)[:160]}")
            result, _ = await eng._dispatch(state, tc.function.name, args)
            body = json.dumps(result, ensure_ascii=False)
            print(f"   返回: {len(body)} 字符  ok={result.get('ok')}")
            messages.append({
                "role": "tool", "tool_call_id": tc.id, "content": body[:4000],
            })


if __name__ == "__main__":
    asyncio.run(main())
