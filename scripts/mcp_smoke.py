# -*- coding: utf-8 -*-
"""MCP 只读冒烟测试：验证核心能力是否真能取到数据。

只调用只读工具，**不会创建任何订单**。
用法：python scripts/mcp_smoke.py
"""
import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

URL = os.getenv("MCP_SERVER_URL", "https://mcp.mcd.cn")
TOKEN = os.getenv("MCP_TOKEN")

CALLS = [
    ("now-time-info", {}, 400),
    ("query-nearby-stores",
     {"beType": 1, "searchType": 2, "city": "北京", "keyword": "首都医科大学"}, 900),
    ("order-list", {}, 1200),
    ("delivery-query-addresses", {}, 700),
    ("list-nutrition-foods", {}, 600),
    ("campaign-calendar", {}, 500),
]


def brief(txt, n):
    txt = " ".join(str(txt).split())
    return txt[:n] + (" …" if len(txt) > n else "")


async def main():
    async with streamablehttp_client(
        url=URL, headers={"Authorization": f"Bearer {TOKEN}"}
    ) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for name, args, n in CALLS:
                try:
                    res = await s.call_tool(name, args)
                    body = ""
                    for c in res.content:
                        body += getattr(c, "text", "") or ""
                    flag = "❌" if res.isError else "✅"
                    print(f"{flag} {name}")
                    print(f"    {brief(body, n)}\n")
                except Exception as e:
                    print(f"❌ {name} 异常: {type(e).__name__}: {brief(e, 200)}\n")


if __name__ == "__main__":
    asyncio.run(main())
