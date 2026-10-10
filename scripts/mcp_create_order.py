# -*- coding: utf-8 -*-
"""真实下单链路实测：菜单取码 → 算价 → 建单（**只到「待支付」，不触发任何支付**）。

⚠️ 这是**写操作**，会在真实麦当劳账号下创建一笔真实订单（状态=待支付）。
   需要显式加 `--yes` 才会执行，避免误跑。

用法：
    python scripts/mcp_create_order.py            # 演练：只跑到算价，不建单
    python scripts/mcp_create_order.py --yes      # 真实建单（待支付）

安全设计：
- 取餐码 `takeWayCode` 不写死，从 `calculate-price` 的 `takeWayList` 里取官方给的值；
- 订单类型固定到店（orderType=1），不走外送（外送不得传 takeWayCode）；
- 建单后立刻用 `query-order` 回读状态，确认停在「待支付」。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.config import settings            # noqa: E402
from server.mcp_client import MCPClient, fen_to_yuan   # noqa: E402

PRODUCT_CODE = "9900005456"   # 麦辣鸡腿汉堡三件套
QUANTITY = 1

# create-order 返回里的状态字段可能叫 status / orderStatus，取值含义以官方为准。
# 这里只做「是否已支付」的粗判，用于自我校验「没有触发支付」。
PAID_HINTS = ("已支付", "paid", "PAID", "已完成")


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yes", action="store_true",
                    help="真实创建订单（仅到待支付）。不加则只演练到算价。")
    args = ap.parse_args()

    store = settings.default_store_id
    if not store:
        print("❌ .env 未配置 DEFAULT_STORE_ID")
        return 1

    c = MCPClient(settings)
    await c.list_tools()
    print(f"工具清单 {len(c.tools)} 个 | 门店 {store}\n")

    # ---- 1) 菜单取码
    menu = await c.meals(store, order_type=1, be_type=1)
    meals = (menu.get("data") or {}).get("meals") or {}
    m = meals.get(PRODUCT_CODE)
    if not m:
        print(f"❌ 菜单中不存在商品码 {PRODUCT_CODE}")
        return 1
    print(f"[1] query-meals      {PRODUCT_CODE} {m.get('name')} "
          f"现价¥{m.get('currentPrice')} 原价¥{m.get('originalPrice')}")

    items = [{"productCode": PRODUCT_CODE, "quantity": QUANTITY}]

    # ---- 2) 算价（拿 price 与 takeWayList）
    priced = await c.calculate_price(
        storeCode=store, orderType=1, beType=1,
        items=items, needTableware=False,
    )
    price_fen = priced.get("price")
    ways = priced.get("takeWayList") or []
    take_way = next((w.get("code") for w in ways if w.get("code")), None)
    print(f"[2] calculate-price  price={price_fen} 分 = ¥{fen_to_yuan(price_fen)}")
    for w in ways:
        print(f"    takeWayList → {w.get('code')}  {w.get('title')} / {w.get('subtitle')}")
    if not take_way:
        print("❌ 算价没返回 takeWayList，无法确定 takeWayCode，终止（不猜）")
        return 1

    if not args.yes:
        print("\n（演练模式）已跑到算价为止，未创建订单。加 --yes 才真实建单。")
        return 0

    # ---- 3) 建单（真实写操作，只到待支付）
    payload = {
        "storeCode": store, "orderType": 1, "beType": 1,
        "items": items, "takeWayCode": take_way, "needTableware": False,
    }
    print(f"\n[3] create-order     payload={json.dumps(payload, ensure_ascii=False)}")
    res = await c.create_order(**payload)
    print(json.dumps(res, ensure_ascii=False, indent=2)[:2000])

    data = (res or {}).get("data") or {}
    order_id = data.get("orderId") or data.get("orderNo") or ""
    status = str(data.get("status") or data.get("orderStatus") or "")
    print(f"\n>>> orderId={order_id!r}  status={status!r}")
    if any(h in status for h in PAID_HINTS):
        print("⚠️ 订单状态看起来像已支付，请立即人工检查！")
        return 2

    # ---- 4) 回读确认
    if order_id:
        try:
            detail = await c.call("query-order", {"orderId": order_id}, use_cache=False)
            print("\n[4] query-order 回读：")
            print(json.dumps(detail, ensure_ascii=False, indent=2)[:1500])
        except Exception as e:                          # noqa: BLE001
            print(f"[4] query-order 回读失败（不影响建单结论）：{e}")

    print("\n✅ 建单完成，停在「待支付」。付款需自行前往麦当劳 App / 小程序。")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
