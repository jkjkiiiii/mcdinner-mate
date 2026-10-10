# -*- coding: utf-8 -*-
"""MCP 连通性探测：确认可用地址、协议版本、真实工具清单。

用法：python scripts/mcp_probe.py
结果写入 docs/MCP_TOOLS.md（真实工具清单，供对话引擎映射使用）
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

try:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
except ImportError:
    sys.exit("缺少 mcp 包：uv pip install mcp")

TOKEN = os.getenv("MCP_TOKEN")
if not TOKEN or TOKEN.startswith("{{"):
    sys.exit("未配置 MCP_TOKEN（检查 .env）")

# 官方赛事 README 写这个；仓库与第三方示例写另一个
URLS = [
    os.getenv("MCP_SERVER_URL", "https://mcp.mcd.cn"),
    "https://mcp.mcd.cn/mcp-servers/mcd-mcp",
]

try:
    from mcp.types import LATEST_PROTOCOL_VERSION as SDK_VER
except Exception:
    SDK_VER = "unknown"
print(f"本地 mcp SDK 声明的协议版本: {SDK_VER}\n")


async def probe(url: str):
    print(f"─── 尝试 {url} ───")
    try:
        async with streamablehttp_client(
            url=url, headers={"Authorization": f"Bearer {TOKEN}"}
        ) as (r, w, _):
            async with ClientSession(r, w) as s:
                info = await s.initialize()
                print(f"  ✅ 连接成功")
                print(f"     服务端: {info.serverInfo.name} {info.serverInfo.version}")
                print(f"     协议版本: {info.protocolVersion}")
                res = await s.list_tools()
                names = [t.name for t in res.tools]
                print(f"     工具总数: {len(names)}")
                for t in res.tools:
                    desc = (t.description or "").replace("\n", " ")
                    print(f"       • {t.name:<28} {desc[:56]}")
                return url, info.protocolVersion, res.tools
    except Exception as e:
        print(f"  ❌ 失败: {type(e).__name__}: {str(e)[:400]}")
        return None


async def main():
    for u in URLS:
        r = await probe(u)
        if r:
            url, ver, tools = r
            out = ROOT / "docs" / "MCP_TOOLS.md"
            out.parent.mkdir(exist_ok=True)
            lines = [
                "# MCP 真实工具清单（实测生成，勿手改）",
                "",
                f"- 生效地址：`{url}`",
                f"- 协议版本：`{ver}`（官方要求 ≤ 2025-06-18）",
                f"- 工具总数：{len(tools)}",
                "",
                "| 工具名 | 说明 |",
                "|---|---|",
            ]
            for t in tools:
                desc = (t.description or "").replace("\n", " ").replace("|", "/")
                lines.append(f"| `{t.name}` | {desc[:120]} |")
            lines += [
                "",
                "## 入参 Schema",
                "",
                "```json",
                json.dumps(
                    {t.name: (t.inputSchema or {}) for t in tools},
                    ensure_ascii=False, indent=2,
                ),
                "```",
            ]
            out.write_text("\n".join(lines), encoding="utf-8")
            print(f"\n💾 工具清单已写入 {out}")
            print(f"✅ 生效地址 = {url} ｜ 协议版本 = {ver}")
            return
    print("\n❌ 两个地址均失败，请检查 Token / 网络")


if __name__ == "__main__":
    asyncio.run(main())
