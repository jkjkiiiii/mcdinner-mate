"""用户画像：把 order-list 的原始订单聚合成「被记住」的那几句话。

MCP 只给近期原始订单，"上周你吃了 3 次麦辣"这类统计必须在这里做。
"""
from __future__ import annotations

from collections import Counter


def summarize_orders(orders: list[dict]) -> dict:
    """聚合历史订单 → 画像。"""
    items: Counter[str] = Counter()
    stores: Counter[str] = Counter()
    amounts: list[float] = []
    times: list[str] = []

    for o in orders:
        if o.get("storeName"):
            stores[o["storeName"]] += 1
        amt = o.get("realTotalAmount")
        try:
            if amt not in (None, ""):
                amounts.append(float(amt))
        except ValueError:
            pass
        if o.get("createTime"):
            times.append(o["createTime"][:10])
        for p in o.get("orderProductList") or []:
            name = p.get("productName")
            if name:
                items[name] += int(p.get("quantity") or 1)

    return {
        "total_orders": len(orders),
        "top_items": items.most_common(5),
        "top_store": stores.most_common(1)[0] if stores else None,
        "avg_amount": round(sum(amounts) / len(amounts), 1) if amounts else None,
        "last_date": max(times) if times else None,
    }


def describe(profile: dict) -> str:
    """把画像转成给模型用的一句中文（简洁，别堆数据）。"""
    if not profile or not profile.get("total_orders"):
        return "（暂无历史订单，这是第一次陪 TA 吃饭）"
    parts = [f"共 {profile['total_orders']} 单"]
    if profile.get("top_items"):
        names = "、".join(n for n, _ in profile["top_items"][:3])
        parts.append(f"常点 {names}")
    if profile.get("top_store"):
        parts.append(f"常去 {profile['top_store'][0]}")
    if profile.get("avg_amount"):
        parts.append(f"平均 {profile['avg_amount']} 元")
    if profile.get("last_date"):
        parts.append(f"上次 {profile['last_date']}")
    return "；".join(parts)
