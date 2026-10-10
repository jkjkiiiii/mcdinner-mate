# -*- coding: utf-8 -*-
"""到店算价链路实测。

只读：query-meals → calculate-price，**不会创建任何订单**。
用途：验证「菜单取码 → 算价」这条下单前必经链路，并核对「分/元」单位。
用法：python scripts/mcp_price_check.py
"""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.config import settings  # noqa: E402
from server.mcp_client import MCPClient, fen_to_yuan  # noqa: E402

PICKS = ["9900005456", "521741"]  # 麦辣鸡腿汉堡三件套 / 脆薯饼


async def main():
    store = settings.default_store_id
    if not store:
        print("❌ .env 未配置 DEFAULT_STORE_ID")
        return

    c = MCPClient(settings)
    await c.list_tools()
    print(f"工具清单已加载：{len(c._tools)} 个\n")

    # 1) 取菜单
    menu = await c.call("query-meals", {"storeCode": store, "orderType": 1, "beType": 1})
    meals = (menu.get("data") or {}).get("meals") or {}
    print(f"[1] query-meals  门店={store}  菜品数={len(meals)}")

    items = []
    for code in PICKS:
        m = meals.get(code)
        if not m:
            print(f"    ⚠️ 菜单中无 {code}，跳过")
            continue
        print(f"    {code}  {m.get('name')}  现价¥{m.get('currentPrice')} 原价¥{m.get('originalPrice')}")
        items.append({"productCode": code, "quantity": 1})

    if not items:
        print("❌ 没取到可用商品码，无法继续")
        return

    # 2) 算价
    print(f"\n[2] calculate-price  商品 {len(items)} 项")
    r = await c.calculate_price(
        storeCode=store, orderType=1, beType=1, items=items, needTableware=False
    )
    print(json.dumps(r, ensure_ascii=False, indent=2)[:2000])

    # 3) 单位校验 + 逐项价格
    raw_total = r.get("price")
    print(f"[3] 单位校验：price={raw_total} 分 → ¥{fen_to_yuan(raw_total)}  "
          f"(原价 {r.get('originalPrice')} 分 → ¥{fen_to_yuan(r.get('originalPrice'))})")
    print(f"    折扣 discount={r.get('discount')} 分 → ¥{fen_to_yuan(r.get('discount'))}")
    for p in r.get("productList") or []:
        print(f"    · {p.get('productName'):<20} x{p.get('quantity')}  "
              f"小计 {p.get('subtotal')} 分 → ¥{p.get('subtotal_yuan')}")

    # 4) 取餐方式（create-order 的 takeWay 取值范围）
    ways = r.get("takeWayList") or []
    print(f"[4] takeWayList: {[w.get('code') for w in ways]}  "
          f"→ create-order 的 takeWay 只能从中选")


if __name__ == "__main__":
    asyncio.run(main())
