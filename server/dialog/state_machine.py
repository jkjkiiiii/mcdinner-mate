"""轻量状态机：只做「阶段提示」，不硬编码意图关键词。

真正的意图判断交给大模型的 tool calling；状态机的作用是
① 约束当前阶段该用哪些工具 ② 给模型一句阶段指引 ③ 记录兜底话术。
"""
from __future__ import annotations

from dataclasses import dataclass

# 各阶段允许调用的工具（None 表示不限制）
STAGE_TOOLS: dict[str, list[str] | None] = {
    "IDLE":   ["now-time-info", "order-list"],
    "CHAT":   ["now-time-info", "order-list", "list-nutrition-foods", "campaign-calendar"],
    "MEMORY": ["order-list", "now-time-info"],
    "RECO":   ["query-meals", "query-meal-detail", "list-nutrition-foods",
               "query-nearby-stores", "order-list"],
    "COUPON": ["campaign-calendar", "available-coupons", "auto-bind-coupons",
               "query-my-coupons", "query-store-coupons"],
    "ORDER":  ["query-store-coupons", "calculate-price", "create-order",
               "query-nearby-stores", "delivery-query-addresses", "delivery-query-stores"],
    "WAIT":   ["query-order", "campaign-calendar", "list-nutrition-foods"],
    "REPORT": ["generate_report_card", "order-list", "list-nutrition-foods"],
}

# 工具调用后自动推进到的阶段
TOOL_NEXT_STAGE: dict[str, str] = {
    "order-list":             "RECO",
    "query-meals":            "RECO",
    "query-meal-detail":      "RECO",
    "list-nutrition-foods":   "RECO",
    "campaign-calendar":      "COUPON",
    "available-coupons":      "COUPON",
    "auto-bind-coupons":      "ORDER",
    "query-store-coupons":    "ORDER",
    "calculate-price":        "ORDER",
    "create-order":           "WAIT",
    "generate_report_card":   "CHAT",
}

# 工具失败时的兜底口播（不中断对话）
FALLBACK: dict[str, str] = {
    "order-list":           "我这边没翻到你的历史订单，不碍事，你直接说今天想吃啥。",
    "list-nutrition-foods": "热量我没查到，这个我不乱说。你想知道的话我再去查一次。",
    "query-meals":          "菜单没拉下来，你说个想吃的，我帮你看看有没有。",
    "campaign-calendar":    "活动日历没取到，不影响点单，先走起。",
    "available-coupons":    "券这会儿查不到，先点着，回头我再帮你看看。",
    "auto-bind-coupons":    "领券没成功，不耽误吃饭。",
    "query-store-coupons":  "这家店的可用券没查到，先按原价给你算。",
    "calculate-price":      "价格没算出来，我再说一遍你要的，你用 App 自己点也行。",
    "create-order":         "下单这步没成，你去 App 看看，我陪你把这顿吃完好吗。",
}


@dataclass
class SessionState:
    session_id: str
    stage: str = "IDLE"
    persona: str = "gentle"
    history: list = None            # type: ignore[assignment]

    def __post_init__(self):
        if self.history is None:
            self.history = []


class StateMachine:
    def __init__(self):
        self.sessions: dict[str, SessionState] = {}

    def get(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id)
        return self.sessions[session_id]

    def allowed_tools(self, stage: str) -> list[str] | None:
        return STAGE_TOOLS.get(stage)

    def advance(self, state: SessionState, tool_name: str):
        # 用户说"吃完了"已进入总结阶段，别再被工具调用打回推荐阶段
        if state.stage == "REPORT":
            return
        nxt = TOOL_NEXT_STAGE.get(tool_name)
        if nxt:
            state.stage = nxt

    def advance_by_text(self, state: SessionState, text: str):
        """极轻量的文本兜底推进（主要用于 CLI 与断网场景）。"""
        t = text.strip()
        if any(k in t for k in ("吃完了", "走了", "结账", "报告", "吃好了")):
            state.stage = "REPORT"
        elif state.stage == "IDLE" and t:
            state.stage = "MEMORY"
        return state.stage

    @staticmethod
    def fallback(tool_name: str) -> str:
        return FALLBACK.get(tool_name, "这会儿接口有点卡，咱先聊着。")
