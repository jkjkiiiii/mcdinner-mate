# MCP 接入说明 · MCP_INTEGRATION

> 说明本项目实际使用的麦当劳 MCP Server、Tool、调用流程与业务价值。
> 文中工具清单由 `scripts/mcp_probe.py` 实测生成，同步保存在 [`docs/MCP_TOOLS.md`](docs/MCP_TOOLS.md)。

---

## 1. 接入的 MCP Server

| 项 | 值 |
| --- | --- |
| 官方名称 | `mcd-mcp` |
| **实际生效地址** | `https://mcp.mcd.cn` |
| 传输协议 | Streamable HTTP |
| 鉴权 | `Authorization: Bearer ${MCP_TOKEN}` |
| **协议版本** | `2025-06-18`（官方要求 ≤ 2025-06-18，已实测匹配） |
| 限流 | 600 次 / 分钟 / Token，超限返回 429 |
| 服务区域 | 中国大陆（不含港澳台） |

### 地址说明

官方文档与赛事 README 写 `https://mcp.mcd.cn`，仓库示例中另有 `https://mcp.mcd.cn/mcp-servers/mcd-mcp`。
本项目实测 **前者可用**，后者未通过，故采用 `https://mcp.mcd.cn`。

### SDK 版本约束（踩过的坑）

官方仅支持协议 ≤ `2025-06-18`，因此固定 `mcp==1.12.0`。
同时 **`mcp 1.12` 依赖 `pydantic<2.12` 的 `eval_type_backport`**，故必须锁 `pydantic==2.11.7`，
否则启动即报 `ImportError: cannot import name 'eval_type_backport'`。

---

## 2. 实际使用的 Tool

`list_tools()` 实测返回 **35 个工具**。本项目按对话意图映射使用其中 **15 个**
（对应 `server/dialog/engine.py` 的 `DIALOG_TOOLS`）。**只暴露这 15 个是有意为之**：
把 35 个工具全量喂给 27B 模型会让它在 `max_tokens` 内吐不出内容（`finish_reason=length`、content 为空）。

| 意图 | Tool | 业务价值 |
| --- | --- | --- |
| 开场记忆：你最近吃了啥 | **`order-list`** | ⭐ 核心。让 AI 真的"记得"用户，这是纯聊天机器人给不了的"被记住"感 |
| 报热量 / 给替代方案 | **`list-nutrition-foods`** | 数据来源官方，**解析失败时拒绝回答，绝不编造数字** |
| 看菜单 / 选餐品 | **`query-meals`**、**`query-meal-detail`** | 真实在售餐品、套餐组成与可替换选项 |
| 查活动 | **`campaign-calendar`** | 当月营销日历（进行中 / 往期 / 未来） |
| 领券 | **`available-coupons`**、**`auto-bind-coupons`** | 陪聊中顺手把券领好，并口头播报结果 |
| 查我的券 | **`query-my-coupons`** | — |
| 我的账号 | **`query-my-account`** | 积分 / 卡券概览，补充"被记住"的上下文 |
| 门店可用券 | **`query-store-coupons`** | 下单前精算，比"可领券"更贴合当前门店 |
| 找门店 | **`query-nearby-stores`** | 到店自提场景按城市 + 关键词检索，返回 `storeCode` |
| 收货地址 | **`delivery-query-addresses`** | 麦乐送场景取 `addressId` |
| 算价 | **`calculate-price`** | 含优惠的应付金额（**注意：接口单位为「分」**） |
| 下单 | **`create-order`** | ⭐ 闭环。返回订单详情与支付链接，**只到待支付** |
| 时间基准 | **`now-time-info`** | 让模型正确理解"今天 / 上周" |

### 完整工具清单

见 [`docs/MCP_TOOLS.md`](docs/MCP_TOOLS.md)（含 35 个工具名、说明与入参 Schema）。
接口返回样例见 `docs/samples/`。

---

## 3. 调用流程

### 到店取餐（orderType=1）

```
query-nearby-stores        → 取 storeCode / beCode
                             （.env 已配常去门店时跳过，本项目默认注入到系统提示）
  ↓
query-meals                → 当前门店在售餐品（实测 124 项）
query-meal-detail          → 套餐组成与可替换项
  ↓
list-nutrition-foods       → 热量 / 营养（本地缓存 30min）
  ↓
query-store-coupons        → 该门店可用券
  ↓
calculate-price            → 应付金额（分 → 元 归一化）
                             ★ 同时返回 takeWayList，供下一步取值
  ↓
create-order               → 待支付订单 + 支付链接（15 分钟内有效）
                             ★ 到店场景 takeWayCode 必传
```

> **两个实测踩到的坑（都已修，见 commit 记录）**
>
> 1. **`create-order` 的 `takeWayCode` 必传**。到店场景（`orderType=1`）必须带上它，
>    取值**只能**来自 `calculate-price` 返回的 `takeWayList[].code`：
>    `eat-in`（堂食）/ `locker-in`（外带）。漏传直接建单失败 —— 而大模型并不天然
>    知道有这么一个字段。本项目做了**双保险**：`engine._fill_order_defaults()` 里兜底注入
>    （默认 `eat-in`），同时在提示词里写明取值来源。
>    注意外送场景（`orderType=2`）**不能**带该字段，带了反而报错。
> 2. **金额单位是「分」不是「元」**。`calculate-price` 返回 `price: 4150` 即 ¥41.5，
>    `productList[].subtotal` 同样是分，直接展示会差 100 倍 —— 见下节归一化处理。

### 麦乐送（orderType=2）

```
delivery-query-addresses   → 取 addressId
delivery-query-stores      → 该地址可配送门店
  ↓ （后续同上：query-meals → calculate-price → create-order）
```

### 开场陪伴流程（本项目特色）

```
now-time-info              → 确定"今天"
  ↓
order-list                 → 拉取历史订单
  ↓ （本地 SQLite 聚合）
"你最近常点麦辣鸡翅和随心配，今天换个口味？"
```

> `order-list` 只返回**近期原始订单**，"上周吃了 3 次麦辣"这类聚合统计由本项目在
> SQLite 侧完成，不依赖 MCP 提供。

---

## 4. 工程化处理

| 措施 | 说明 |
| --- | --- |
| **缓存** | 菜单、营养、活动日历等静态数据本地缓存 ≥ 30 分钟 |
| **限流** | 失败重试 1 次 + 指数退避，避免 Demo 时触发 429 |
| **单位归一化** | MCP 所有金额单位为「分」。`add_yuan_fields()` 在 MCP 层为**顶层与 `productList` 逐项**追加 `*_yuan` 副本（原字段保留，以维持与官方 schema 一致），上层一律读 `*_yuan` |
| **营养解析** | `list-nutrition-foods` 返回 toon 紧凑格式（如 `[160]{productName,energyKcal,...}`），本项目写专用解析器并加单测；**解析失败时拒绝回答** |
| **兜底话术** | 工具失败时口播兜底（如"麦门信号不好，先直接给你看菜单"），不中断对话 |

---

## 5. 边界与合规

- **只到待支付**：`create-order` 返回支付链接后即停止，不集成支付、不自动支付。
  订单 15 分钟内有效，是否支付由用户自行决定。
- **不编造数据**：营养、价格、库存一律以接口返回为准。
- **不使用品牌素材**：项目 UI 与文档中不使用麦当劳 Logo 或商标图形。
- **不比较、不贬低**：人设话术仅吐槽工作与生活，不涉及餐品、价格、门店与品牌评价。

---

## 6. 复现验证

```bash
python scripts/mcp_probe.py          # 打印生效地址、协议版本、35 个工具清单
python scripts/mcp_smoke.py          # 只读冒烟：时间 / 门店 / 历史订单 / 地址 / 营养 / 活动
python scripts/fetch_account_info.py # 抓取门店与收货地址 ID
python scripts/mcp_price_check.py    # 菜单取码 → 算价 → 单位核对（只读）
python scripts/e2e_smoke.py          # 端到端：真实大模型 + 真实 MCP 跑 3 轮对话（只读）
python scripts/asr_check.py          # 本地 ASR 冒烟（TTS 合成音频 → 识别回文字）
python scripts/debug_turn.py "就这个，多少钱？"   # 单轮调试，逐轮打印 tool_calls 与 finish_reason
```

> **以上全部为只读调用，不会创建任何订单。**
> `create-order` 仅在真实对话中由用户确认后才触发，且只到「待支付」为止。

### 实测记录（真实调用，非构造数据）

| 项 | 实测结果 |
| --- | --- |
| 工具数 | `list_tools()` → **35 个** |
| 菜单 | 门店 `1950814` → **122~124 项**（`data.meals` 是 `{code: {...}}` 字典，不是数组） |
| 算价（单品） | 三件套 → `price: 3350` 分 = **¥33.5**，`productList[].subtotal` 同为 3350 分 |
| 算价（两件） | 三件套 ¥33.5 + 薯饼 ¥8.0 → `price: 4150` 分 = **¥41.5**，逐项 `subtotal` 与 `productList` 严格吻合 |
| **建单** | `create-order`（orderType=1 + `takeWayCode=eat-in`）**真实建单成功**，`query-order` 回读 `orderStatus="待支付"`、`status="10"`、`totalAmount="33.5"`、`takeWay="堂食"`、`expirePayTime` 为 15 分钟后；**全程未触发任何支付** |
| **建单返回的坑** | `create-order` 的 `data` **只带 `orderId`**，门店/金额/取餐方式/支付时限都在 `query-order` 里 → 必须回读一次才能渲染完整订单卡 |
| 取餐方式 | `takeWayList` → `eat-in`（堂食）/ `locker-in`（外带） |
| 历史订单 | `order-list` → 返回真实历史订单，用于开场"被记住"（聚合在本地 SQLite 完成） |
| 营养 | `list-nutrition-foods` → toon 紧凑格式，解析后热量与官方一致 |
