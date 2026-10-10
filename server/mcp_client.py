"""麦当劳 MCP 客户端：连接、工具映射、缓存、限流、单位归一化、营养格式解析。

设计要点
--------
1. **写操作绝不重试** —— `create-order` / `auto-bind-coupons` 等重试会造成重复下单或重复领券。
2. **金额单位是「分」** —— 统一在本层转为「元」后再上抛，避免上层到处 ÷100。
3. **营养接口返回 toon 紧凑格式** —— 专用解析器；解析失败时上层必须拒绝回答，不允许模型编数字。
4. **静态数据缓存 30 分钟** —— 官方限流 600 次/分钟/Token。
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from .config import Settings

# ---------------------------------------------------------------- 金额


def fen_to_yuan(v: Any) -> float | None:
    """接口金额单位为「分」，转为「元」。无法解析时返回 None（不猜）。"""
    if v is None or v == "":
        return None
    try:
        return round(float(v) / 100.0, 2)
    except (TypeError, ValueError):
        return None


_AMOUNT_KEY = re.compile(r"(amount|price|fee|total|subtotal)", re.I)


def add_yuan_fields(d: dict) -> dict:
    """就地为金额字段追加 `*_yuan` 副本，**原字段保持不变**。

    接口里所有金额都是「分」，直接展示会差 100 倍（¥33.5 显示成 3350）。
    保留原字段是为了不破坏与官方 schema 的一致性；上层一律读 `*_yuan`。
    """
    for k, v in list(d.items()):
        if k.endswith("_yuan"):
            continue
        if isinstance(v, (int, float, str)) and not isinstance(v, bool) and _AMOUNT_KEY.search(k):
            y = fen_to_yuan(v)
            if y is not None:
                d[f"{k}_yuan"] = y
    return d


# ---------------------------------------------------------------- toon 解析

_TOON_HEADER = re.compile(r"\[(\d+)\]\{([^}]*)\}\s*:")


def parse_toon(text: str) -> list[dict[str, str]]:
    """解析 MCP 返回的 toon 紧凑格式。

    形如::

        [160]{productName,nutritionDescription,energyKj,energyKcal,...}:
          猪柳麦满分,null,1288,308,16,16,24,781,213
          中薯条,null,1210,289,4,12,38,165,18

    容错：行数与头部声明不符、某行列数不符时跳过该行而不整体失败。
    列名含多余逗号时，把多出的前段合并进第一列。
    """
    if not text:
        return []
    m = _TOON_HEADER.search(text)
    if not m:
        return []
    cols = [c.strip() for c in m.group(2).split(",") if c.strip()]
    ncol = len(cols)
    body = text[m.end():]
    rows: list[dict[str, str]] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < ncol:
            continue
        if len(parts) > ncol:                      # 名称里含逗号：多余部分并入首列
            parts = [",".join(parts[: len(parts) - ncol + 1])] + parts[len(parts) - ncol + 1:]
        rows.append(dict(zip(cols, parts)))
        # 达到头部声明的条数即停，避免把正文说明误当数据
        if len(rows) >= int(m.group(1)):
            break
    return rows


def nutrition_index(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    """把营养行转成 {品名: {energyKcal:int, protein:float, ...}}，数值统一转 float。"""
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        name = (r.get("productName") or "").strip()
        if not name:
            continue
        item: dict[str, Any] = {}
        for k, v in r.items():
            if k == "productName":
                continue
            if v in (None, "", "null"):
                item[k] = None
                continue
            try:
                f = float(v)
                item[k] = int(f) if f.is_integer() else f
            except ValueError:
                item[k] = v
        out[name] = item
    return out


def match_nutrition(index: dict[str, dict[str, Any]], query: str) -> tuple[str, dict] | None:
    """按菜品名查营养：先精确，再包含匹配，最后按字符重合度兜底。

    查不到返回 None —— 调用方必须据此拒绝回答，不允许编造热量。
    """
    q = query.strip()
    if not q:
        return None
    if q in index:
        return q, index[q]
    cands = [k for k in index if q in k or k in q]
    if not cands:
        # 字符级重合度兜底（"麦辣鸡腿堡" vs "麦辣鸡翅" 这类）
        qs = set(q)
        scored = sorted(
            index.keys(),
            key=lambda k: len(qs & set(k)) / max(1, len(qs | set(k))),
            reverse=True,
        )
        cands = scored[:1] if scored and len(qs & set(scored[0])) >= 2 else []
    if not cands:
        return None
    best = min(cands, key=len)          # 取最短（最通用）的匹配项
    return best, index[best]


# ---------------------------------------------------------------- 客户端


@dataclass
class CacheEntry:
    value: Any
    expires: float


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: dict

    def to_openai(self) -> dict:
        """转成 OpenAI function calling 的 tool schema。"""
        schema = self.input_schema or {"type": "object", "properties": {}}
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": (self.description or "")[:500],
                "parameters": schema,
            },
        }


class MCPClient:
    """对 MCP Server 的薄封装。所有业务语义在各 wrapper 方法里。"""

    def __init__(self, settings: Settings, ttl: int | None = None):
        self.cfg = settings
        self.ttl = ttl if ttl is not None else settings.cache_ttl
        self._tools: dict[str, MCPTool] = {}
        self._cache: dict[tuple, CacheEntry] = {}
        self._nutrition: dict[str, dict[str, Any]] | None = None

    # ---------------- 连接与工具发现

    async def list_tools(self) -> dict[str, MCPTool]:
        """连一次 MCP，把工具清单抓回来（不保持长连接，够用且省资源）。"""
        async with streamablehttp_client(
            url=self.cfg.mcp_server_url,
            headers={"Authorization": f"Bearer {self.cfg.mcp_token}"},
        ) as (r, w, _):
            async with ClientSession(r, w) as s:
                await s.initialize()
                res = await s.list_tools()
                self._tools = {
                    t.name: MCPTool(t.name, t.description or "", t.inputSchema or {})
                    for t in res.tools
                }
        return self._tools

    @property
    def tools(self) -> dict[str, MCPTool]:
        return self._tools

    def openai_tools(self, names: list[str] | None = None) -> list[dict]:
        src = self._tools.values()
        if names:
            src = [t for t in src if t.name in set(names)]
        return [t.to_openai() for t in src]

    # ---------------- 原始调用

    async def call_raw(self, name: str, args: dict | None = None) -> str:
        """调用工具，返回原始文本。

        - 写操作（create-order 等）**不重试**
        - 读操作失败重试 max_retry 次，指数退避
        """
        args = args or {}
        attempts = 1 if name in self.cfg.mutating_tools else (self.cfg.max_retry + 1)
        last_err: Exception | None = None
        for i in range(attempts):
            try:
                async with streamablehttp_client(
                    url=self.cfg.mcp_server_url,
                    headers={"Authorization": f"Bearer {self.cfg.mcp_token}"},
                ) as (r, w, _):
                    async with ClientSession(r, w) as s:
                        await s.initialize()
                        res = await s.call_tool(name, args)
                        text = "".join(getattr(c, "text", "") or "" for c in res.content)
                        if res.isError:
                            raise RuntimeError(f"{name} 返回错误: {text[:200]}")
                        return text
            except Exception as e:                      # noqa: BLE001
                last_err = e
                if i < attempts - 1:
                    await asyncio.sleep(0.6 * (2 ** i))
        raise RuntimeError(f"MCP 调用失败 {name}: {last_err}")

    async def call(self, name: str, args: dict | None = None, use_cache: bool = True):
        """调用并尽量把业务 JSON 抠出来；缓存只作用于白名单内的读接口。"""
        args = args or {}
        if use_cache and name in self.cfg.cacheable_tools:
            key = (name, json.dumps(args, sort_keys=True, ensure_ascii=False))
            hit = self._cache.get(key)
            if hit and hit.expires > time.time():
                return hit.value
        text = await self.call_raw(name, args)
        obj = self._extract_json(text)
        value = obj if obj is not None else text
        if use_cache and name in self.cfg.cacheable_tools:
            k = (name, json.dumps(args, sort_keys=True, ensure_ascii=False))
            self._cache[k] = CacheEntry(value, time.time() + self.ttl)
        return value

    @staticmethod
    def _extract_json(text: str):
        """从说明性文本中抠出业务 JSON。

        注意：返回正文常带 markdown 表格与 `{字段名}` 占位花括号，
        直接找第一个 '{' 会解析失败，必须定位 `{"success"` 起点。
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

    def clear_cache(self):
        self._cache.clear()

    # ---------------- 业务 wrapper

    async def now_time(self) -> dict:
        return await self.call("now-time-info")

    async def history_orders(self) -> list[dict]:
        """历史订单（核心：'被记住'）。只返回近期到店/外送订单，非商城订单。"""
        d = await self.call("order-list")
        return ((d or {}).get("data") or {}).get("list") or []

    async def nearby_stores(self, city: str, keyword: str, be_type: int = 1):
        d = await self.call("query-nearby-stores",
                            {"beType": be_type, "searchType": 2,
                             "city": city, "keyword": keyword})
        return (d or {}).get("data") or []

    async def delivery_addresses(self):
        d = await self.call("delivery-query-addresses")
        return ((d or {}).get("data") or {}).get("addresses") or []

    async def nutrition(self, refresh: bool = False) -> dict[str, dict[str, Any]]:
        """营养表（toon 格式解析，缓存 30min）。"""
        if self._nutrition is not None and not refresh:
            return self._nutrition
        d = await self.call("list-nutrition-foods")
        data = (d or {}).get("data")
        rows = parse_toon(data if isinstance(data, str) else "")
        self._nutrition = nutrition_index(rows)
        return self._nutrition

    async def calories(self, food: str) -> dict | None:
        """查某菜品热量。查不到返回 None —— 调用方必须拒绝回答而非编造。"""
        idx = await self.nutrition()
        hit = match_nutrition(idx, food)
        if not hit:
            return None
        name, item = hit
        return {"productName": name, "energyKcal": item.get("energyKcal"),
                "protein": item.get("protein"), "fat": item.get("fat"),
                "carbohydrate": item.get("carbohydrate"), "sodium": item.get("sodium")}

    async def meals(self, store_code: str, order_type: int = 1, be_type: int = 1, **kw):
        return await self.call("query-meals", {"storeCode": store_code,
                                               "orderType": order_type,
                                               "beType": be_type, **kw})

    async def campaign_calendar(self):
        return await self.call("campaign-calendar")

    async def available_coupons(self):
        return await self.call("available-coupons")

    async def auto_bind_coupons(self):
        """一键领券 —— 写操作，不重试。"""
        return await self.call("auto-bind-coupons", use_cache=False)

    async def my_coupons(self):
        return await self.call("query-my-coupons")

    async def calculate_price(self, **kw) -> dict:
        """算价。顶层与 productList 逐项都附加 *_yuan（接口原始单位为「分」）。

        实测返回结构（到店 beType=1）::

            price / productPrice / originalPrice / discount   → 分
            productList[].subtotal / originalSubtotal         → 分
            takeWayList[].code  → eat-in(堂食) / locker-in(外带)
                                 下单时 takeWayCode 必传，值取这里
        """
        d = await self.call("calculate-price", kw, use_cache=False) or {}
        data = dict(d.get("data") or d)
        add_yuan_fields(data)
        for p in data.get("productList") or []:
            if isinstance(p, dict):
                add_yuan_fields(p)
        return data

    async def create_order(self, **kw) -> dict:
        """创建订单 —— 只到待支付。写操作，不重试。"""
        return await self.call("create-order", kw, use_cache=False)
