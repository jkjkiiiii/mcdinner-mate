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

`list_tools()` 实测返回 **35 个工具**。本项目按对话意图映射使用其中 12 个：

| 意图 | Tool | 业务价值 |
| --- | --- | --- |
| 开场记忆：你最近吃了啥 | **`order-list`** | ⭐ 核心。让 AI 真的"记得"用户，这是纯聊天机器人给不了的"被记住"感 |
| 报热量 / 给替代方案 | **`list-nutrition-foods`** | 数据来源官方，**解析失败时拒绝回答，绝不编造数字** |
| 看菜单 / 选餐品 | **`query-meals`**、**`query-meal-detail`** | 真实在售餐品、套餐组成与可替换选项 |
| 查活动 | **`campaign-calendar`** | 当月营销日历（进行中 / 往期 / 未来） |
| 领券 | **`available-coupons`**、**`auto-bind-coupons`** | 陪聊中顺手把券领好，并口头播报结果 |
| 查我的券 | **`query-my-coupons`** | — |
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
  ↓
query-meals                → 当前门店在售餐品
query-meal-detail          → 套餐组成与可替换项
  ↓
list-nutrition-foods       → 热量 / 营养（本地缓存 30min）
  ↓
query-store-coupons        → 该门店可用券
  ↓
calculate-price            → 应付金额（分 → 元 归一化）
  ↓
create-order               → 待支付订单 + 支付链接（15 分钟内有效）
```

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
| **单位归一化** | MCP 所有金额单位为「分」，在 MCP 层统一 ÷100 转为「元」后再上抛 |
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
python scripts/mcp_probe.py         # 打印生效地址、协议版本、35 个工具清单
python scripts/mcp_smoke.py         # 只读冒烟：时间 / 门店 / 历史订单 / 地址 / 营养 / 活动
python scripts/fetch_account_info.py# 抓取门店与收货地址 ID
```

> 全部为**只读调用**，不会创建任何订单。
