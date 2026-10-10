# -*- coding: utf-8 -*-
"""抓取关键账号信息（门店 / 收货地址 / 历史订单），回填 .env。

只调用只读工具，不创建订单。
原始返回同时落盘到 docs/samples/，供后续写解析器时对照。
"""
import asyncio
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
SAMPLES = ROOT / "docs" / "samples"
SAMPLES.mkdir(parents=True, exist_ok=True)

URL = os.getenv("MCP_SERVER_URL")
TOKEN = os.getenv("MCP_TOKEN")
# 门店搜索用中性关键词，避免把开发者的常驻位置写进公开仓库
NEARBY_CITY = os.getenv("NEARBY_CITY", "北京")
NEARBY_KEYWORD = os.getenv("NEARBY_KEYWORD", "国贸")


def parse_json_obj(text: str):
    """从 MCP 返回的说明性文本中抠出业务 JSON。

    注意：返回正文常带 markdown 表格与 `{字段名}` 占位花括号，
    直接找第一个 '{' 会解析失败 —— 必须定位真实响应起点 `{"success"`，
    找不到时再逐个 '{' 尝试 raw_decode。
    """
    dec = json.JSONDecoder()
    i = text.find('{"success"')
    if i >= 0:
        try:
            obj, _ = dec.raw_decode(text[i:])
            return obj
        except json.JSONDecodeError:
            pass
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = dec.raw_decode(text[m.start():])
            if isinstance(obj, dict) and "success" in obj:
                return obj
        except json.JSONDecodeError:
            continue
    return None


async def call(s, name, args=None):
    res = await s.call_tool(name, args or {})
    text = "".join(getattr(c, "text", "") or "" for c in res.content)
    (SAMPLES / f"{name}.txt").write_text(text, encoding="utf-8")
    return parse_json_obj(text)


async def main():
    async with streamablehttp_client(
        url=URL, headers={"Authorization": f"Bearer {TOKEN}"}
    ) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()

            print("=== 附近门店（到店自提）===")
            d = await call(s, "query-nearby-stores",
                           {"beType": 1, "searchType": 2, "city": NEARBY_CITY,
                            "keyword": NEARBY_KEYWORD})
            stores = (d or {}).get("data") or []
            for st in stores[:6]:
                print(f"  {st.get('storeCode')} | {st.get('storeName')} | "
                      f"{st.get('distance')}m | 预约={st.get('reservation')} | "
                      f"beCode={st.get('beCode')}")

            print("\n=== 收货地址 ===")
            d2 = await call(s, "delivery-query-addresses")
            addrs = ((d2 or {}).get("data") or {}).get("addresses") or []
            for a in addrs:
                print(f"  {a.get('addressId')} | {a.get('fullAddress')} | "
                      f"{a.get('contactName')}")

            print("\n=== 历史订单（核心：记忆感）===")
            d3 = await call(s, "order-list")
            lst = ((d3 or {}).get("data") or {}).get("list") or []
            print(f"  订单总数: {len(lst)}")
            for o in lst[:5]:
                prods = ", ".join(
                    p.get("productName", "")
                    for p in (o.get("orderProductList") or [])[:3])
                print(f"  {o.get('createTime')} | {o.get('storeName')} | "
                      f"{o.get('realTotalAmount')} | {prods}")

            print(f"\n💾 原始返回已保存到 {SAMPLES}")


if __name__ == "__main__":
    asyncio.run(main())
