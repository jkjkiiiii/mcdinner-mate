"""对话引擎：本地大模型 + MCP 工具 + 状态机 + 记忆。

设计要点
--------
- 意图判断交给模型的 tool calling，状态机只做「阶段约束 + 阶段提示」
- 工具失败时把**兜底话术**作为工具结果回灌，让模型自然地说出来，不中断对话
- 每轮最多 5 次工具往返，防止死循环
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from ..config import Settings
from ..mcp_client import MCPClient
from ..memory.db import DB
from ..memory.profile import describe, summarize_orders
from ..report.card import render_card
from .persona import get_persona, stage_hint
from .state_machine import StateMachine

MAX_ROUNDS = 5

# 对话引擎真正会用到的工具。
# 教训：MCP 一共有 35 个工具，全量塞给 27B 模型会让它在 max_tokens 内吐不出内容
# （finish_reason=length、content 为空）。这里只暴露场景必需的 15 个。
DIALOG_TOOLS: tuple[str, ...] = (
    "now-time-info", "order-list",
    "query-meals", "query-meal-detail", "list-nutrition-foods",
    "campaign-calendar", "available-coupons", "auto-bind-coupons",
    "query-my-coupons", "query-store-coupons",
    "query-nearby-stores", "delivery-query-addresses",
    "calculate-price", "create-order", "query-my-account",
)

LOCAL_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "generate_report_card",
            "description": "用户说吃完了/要走了时，生成今日饭后分享报告卡（1080x1080 PNG）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {"type": "array", "items": {"type": "string"},
                              "description": "今天吃了什么，来自订单或对话"},
                    "kcal": {"type": "integer", "description": "总热量；不知道就省略，不要编"},
                    "mood": {"type": "string", "description": "今日心情关键词，如『有点累但还行』"},
                },
                "required": ["items"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "switch_persona",
            "description": "切换陪餐人设。gentle=温柔树洞，sarcastic=毒舌（只吐槽工作与生活）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["gentle", "sarcastic"]},
                },
                "required": ["mode"],
            },
        },
    },
]


class DialogEngine:
    def __init__(self, settings: Settings, mcp: MCPClient, db: DB | None = None):
        self.cfg = settings
        self.mcp = mcp
        self.db = db or DB(settings.db_path)
        self.sm = StateMachine()
        self.llm = AsyncOpenAI(
            base_url=settings.llm_base_url, api_key=settings.llm_api_key
        )
        self.cards: dict[str, list[dict]] = {}

    # ---------------------------------------------------------------- 上下文

    async def _profile_text(self) -> str:
        cached = self.db.get_profile("summary")
        if cached:
            return describe(cached)
        try:
            orders = await self.mcp.history_orders()
            prof = summarize_orders(orders)
            self.db.set_profile("summary", prof)
            return describe(prof)
        except Exception:                                   # noqa: BLE001
            return "（历史订单暂时取不到，别提这件事）"

    def _system(self, state, profile_text: str) -> str:
        return (
            get_persona(state.persona, self.cfg)
            + f"\n## 当前阶段指引\n{stage_hint(state.stage)}\n"
            + f"\n## 你对这位用户的记忆\n{profile_text}\n"
            + "\n（以上记忆来自真实历史订单，可以自然地提起，但别一开口就报数据。）"
        )

    # 只「关」写操作，读工具全程可用。
    # 教训：早期版本按阶段限制读工具，导致用户问热量时模型拿不到营养工具，
    # 只能回答"查不到"——功能上是错的。阶段只用来决定要不要放出下单。
    GATED_WRITE_TOOLS = {"create-order", "cancel-order", "draw-lottery",
                         "mall-create-order", "party-order-create"}
    WRITE_ALLOWED_STAGES = {"ORDER", "WAIT"}

    def _tools_for(self, state) -> list[dict]:
        tools = [
            t for t in self.mcp.openai_tools()
            if t.get("function", {}).get("name") in DIALOG_TOOLS
        ]
        if state.stage not in self.WRITE_ALLOWED_STAGES:
            tools = [
                t for t in tools
                if t.get("function", {}).get("name") not in self.GATED_WRITE_TOOLS
            ]
        return list(tools) + LOCAL_TOOLS

    # ---------------------------------------------------------------- 工具执行

    async def _dispatch(self, state, name: str, args: dict) -> tuple[Any, dict | None]:
        """返回 (给模型的工具结果, 需要前端渲染的卡片)。"""
        card = None

        if name == "generate_report_card":
            items = args.get("items") or []
            path = render_card(
                items=items,
                kcal=args.get("kcal"),
                mood=args.get("mood"),
                out_path=str(Path(self.cfg.db_path).parent / f"report_{state.session_id}.png"),
            )
            card = {"type": "report", "image": str(path), "items": items,
                    "kcal": args.get("kcal"), "mood": args.get("mood")}
            return {"ok": True, "card": str(path)}, card

        if name == "switch_persona":
            mode = args.get("mode", "gentle")
            state.persona = mode if mode in ("gentle", "sarcastic") else "gentle"
            return {"ok": True, "persona": state.persona}, None

        if name == "get_profile_summary":
            return {"summary": await self._profile_text()}, None

        # 其余交给 MCP
        args = self._fill_order_defaults(name, args)
        use_cache = name in self.cfg.cacheable_tools
        try:
            res = await self.mcp.call(name, args, use_cache=use_cache)
            if isinstance(res, (dict, list)):
                text = json.dumps(res, ensure_ascii=False)
            else:
                text = str(res)
            # 上下文可能很长（菜单/营养全表），截断保护
            if len(text) > 6000:
                text = text[:6000] + " …(已截断)"
            return {"ok": True, "data": text}, None
        except Exception as e:                              # noqa: BLE001
            self.sm.advance(state, name)
            return {"ok": False, "error": str(e)[:200],
                    "fallback": self.sm.fallback(name)}, None

    @staticmethod
    def _fill_order_defaults(name: str, args: dict) -> dict:
        """补齐 MCP 写接口的必传字段。

    `create-order` 在到店场景（orderType=1）**必须**带 `takeWayCode`，
    取值只能是 calculate-price 返回的 takeWayList[].code（eat-in / locker-in）。
    模型偶尔会漏，这里兜底成「堂食」，避免整单白跑。
        """
        a = dict(args or {})
        if name == "create-order":
            order_type = int(a.get("orderType", 1) or 1)
            if order_type == 1 and not a.get("takeWayCode"):
                a["takeWayCode"] = "eat-in"
            a.setdefault("beType", 1)
            a.setdefault("needTableware", False)
        return a

    # ---------------------------------------------------------------- 主流程

    async def chat(self, session_id: str, user_text: str) -> dict:
        state = self.sm.get(session_id)
        self.sm.advance_by_text(state, user_text)

        self.db.add_message(session_id, "user", user_text)
        profile_text = await self._profile_text()

        messages: list[dict] = [
            {"role": "system", "content": self._system(state, profile_text)}
        ]
        messages += self.db.get_messages(session_id, limit=12)

        tools = self._tools_for(state)
        cards: list[dict] = []
        reply = ""

        for _ in range(MAX_ROUNDS):
            resp = await self.llm.chat.completions.create(
                model=self.cfg.llm_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=768,
            )
            ch = resp.choices[0]
            msg = ch.message
            # 输出被截断且没内容：本轮作废，下一轮放宽 token 再试，避免死循环
            if ch.finish_reason == "length" and not (msg.content or "").strip() \
                    and not msg.tool_calls:
                continue
            messages.append(msg.model_dump(exclude_none=True))

            if not msg.tool_calls:
                reply = (msg.content or "").strip()
                break

            for tc in msg.tool_calls:
                fname = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result, card = await self._dispatch(state, fname, args)
                if card:
                    cards.append(card)
                self.sm.advance(state, fname)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False)[:4000],
                })
            # 工具调用后阶段可能变化，下一轮更新可用工具
            tools = self._tools_for(state)

        if not reply:
            # 兜底：模型可能一直在调工具而没给出最终回复。
            # 再问一次，这次不给工具，强制它说人话。
            try:
                resp = await self.llm.chat.completions.create(
                    model=self.cfg.llm_model,
                    messages=messages + [{"role": "system",
                                          "content": "现在不要再调用任何工具，直接用一句口语回复用户。"}],
                    temperature=0.7,
                    max_tokens=256,
                )
                reply = (resp.choices[0].message.content or "").strip()
            except Exception:                               # noqa: BLE001
                reply = ""

        if not reply:
            reply = "（我卡了一下）你想吃点啥？我帮你看。"

        self.db.add_message(session_id, "assistant", reply)
        return {"reply": reply, "cards": cards, "stage": state.stage,
                "persona": state.persona}
