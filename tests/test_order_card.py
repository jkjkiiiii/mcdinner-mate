# -*- coding: utf-8 -*-
"""订单确认卡片：从 create-order 返回里提取待支付卡片，字段缺失不编造。"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server.dialog.engine import DialogEngine as E  # noqa: E402


def test_order_card_basic():
    # 全用合成数据：真实订单号属于账号数据，不入库
    res = {"success": True, "data": {
        "orderId": "TESTORDER0000000000000001",
        "orderStatus": "待支付",
        "storeName": "某餐厅（测试门店）",
        "storeAddress": "某路 1 号",
        "takeWay": "堂食",
        "totalAmount": "33.5",
        "totalDiscountAmount": "0",
        "expirePayTime": "2026-10-10 23:14:20",
    }}
    c = E._order_card(res)
    assert c is not None
    assert c["type"] == "order"
    assert c["orderId"] == "TESTORDER0000000000000001"
    assert c["status"] == "待支付"
    assert c["total"] == "33.5"
    assert c["takeWay"] == "堂食"


def test_order_card_missing_fields_are_blank_not_invented():
    """字段缺失时留空字符串 —— 绝不编造门店名或金额。"""
    c = E._order_card({"success": True, "data": {"orderId": "X1"}})
    assert c is not None
    assert c["store"] == "" and c["total"] == "" and c["expire"] == ""
    assert c["status"] == "待支付"          # 该字段有明确默认语义


def test_order_card_rejects_failure_and_no_id():
    assert E._order_card({"success": False, "data": {"orderId": "X"}}) is None
    assert E._order_card({"success": True, "data": {}}) is None
    assert E._order_card("not a dict") is None
    assert E._order_card(None) is None


def test_order_card_falls_back_to_order_no():
    c = E._order_card({"success": True, "data": {"orderNo": "N9"}})
    assert c is not None and c["orderId"] == "N9"


def test_order_card_never_contains_pay_fields():
    """安全红线：卡片里不得出现任何支付动作字段。"""
    c = E._order_card({"success": True, "data": {
        "orderId": "TESTORDER0000000000000001",
        "payId": "TESTPAY0000000000000001", "paid": True,
    }})
    assert c is not None
    assert not any("pay" in k.lower() for k in c)


# ---------------------------------------------------------------- _enrich_order

class _FakeMCP:
    """最小替身：只实现 query-order。"""

    def __init__(self, detail):
        self.detail = detail
        self.calls = []

    async def call(self, name, args=None, use_cache=True):
        self.calls.append(name)
        if isinstance(self.detail, Exception):
            raise self.detail
        return self.detail


def _engine(mcp):
    e = E.__new__(E)          # 绕过 __init__（不连 LLM / DB）
    e.mcp = mcp
    return e


def test_enrich_fills_missing_fields_from_query_order():
    mcp = _FakeMCP({"success": True, "data": {
        "orderId": "TESTORDER0000000000000001", "orderStatus": "待支付",
        "storeName": "某门店", "totalAmount": "33.5",
        "takeWay": "堂食", "expirePayTime": "2026-10-10 23:14:20",
    }})
    res = {"success": True, "data": {"orderId": "TESTORDER0000000000000001"}}
    out = asyncio.run(_engine(mcp)._enrich_order(res))
    assert mcp.calls == ["query-order"]
    assert out["data"]["storeName"] == "某门店"
    c = E._order_card(out)
    assert c["total"] == "33.5" and c["takeWay"] == "堂食"


def test_enrich_skips_call_when_fields_already_present():
    mcp = _FakeMCP({"success": True, "data": {}})
    res = {"success": True, "data": {
        "orderId": "X1", "storeName": "S", "totalAmount": "1",
        "takeWay": "堂食", "expirePayTime": "T",
    }}
    out = asyncio.run(_engine(mcp)._enrich_order(res))
    assert mcp.calls == []                       # 省掉一次多余调用
    assert out["data"]["storeName"] == "S"


def test_enrich_failure_keeps_original_unchanged():
    """补字段失败必须原样返回，绝不能让建单结果被破坏。"""
    res = {"success": True, "data": {"orderId": "X1"}}
    out = asyncio.run(_engine(_FakeMCP(RuntimeError("boom")))._enrich_order(res))
    assert out == res


def test_enrich_does_not_overwrite_existing_values():
    mcp = _FakeMCP({"success": True, "data": {
        "orderId": "X1", "storeName": "新门店", "totalAmount": "99"}})
    res = {"success": True, "data": {"orderId": "X1", "totalAmount": "33.5"}}
    out = asyncio.run(_engine(mcp)._enrich_order(res))
    assert out["data"]["totalAmount"] == "33.5"      # 建单结果优先
    assert out["data"]["storeName"] == "新门店"       # 缺失的才补


def test_enrich_noop_on_failure_or_missing_id():
    e = _engine(_FakeMCP({"success": True, "data": {}}))
    assert asyncio.run(e._enrich_order({"success": False, "data": {}})) == \
        {"success": False, "data": {}}
    assert asyncio.run(e._enrich_order({"success": True, "data": {}})) == \
        {"success": True, "data": {}}
    assert asyncio.run(e._enrich_order("nope")) == "nope"

