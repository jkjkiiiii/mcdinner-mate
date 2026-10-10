# 05 · ⭐ MCP 工具清单与意图映射

> **本文件是高频维护文件。Phase 1 跑通 `list_tools()` 后，必须把实测结果回写到这里。**
> 工具名来自官方文档 `open.mcd.cn/mcp/doc`（2026-10-10 核对）。中文名仅为意图描述，不是实际工具名。

## 5.1 官方真实工具清单

> 以下按业务域归类便于阅读；**完整 35 个工具的入参 Schema 见 [`../MCP_TOOLS.md`](../MCP_TOOLS.md)**
> （由 `scripts/mcp_probe.py` 实测生成，非手工整理，因此不会与官方漂移）。

### 地址与门店

| 工具名 | 说明 |
| --- | --- |
| `query-nearby-stores` | 查询用户提供地址附近的麦当劳餐厅 |
| `delivery-query-stores` | 外送场景下查询收货地址附近可配送门店 |
| `delivery-query-addresses` | 查询用户已创建的配送地址列表 |
| `delivery-create-address` | 新增配送地址 |
| `query-meal-assistance` | 查询助餐服务（仅企业团餐场景） |

### 菜单与点餐

| 工具名 | 说明 |
| --- | --- |
| `query-meals` | 查询当前门店可售餐品列表（分类、餐品编码、标签） |
| `query-meal-detail` | 根据餐品编码查详情、套餐组成与可替换选项 |
| `query-store-coupons` | 查询用户在**当前门店**可使用的优惠券 |
| `calculate-price` | 根据选购商品（可含优惠券）计算金额、配送费、优惠、应付总价 |
| `create-order` | 创建订单，**返回订单详情与支付链接** |
| `query-order` | 查询订单状态、内容、配送信息 |
| `order-list` | **查询历史订单**（近期到店/外送，非商城） |

### 优惠与积分

| 工具名 | 说明 |
| --- | --- |
| `campaign-calendar` | 麦当劳中国当月营销活动日历（进行中/往期/未来） |
| `available-coupons` | 可领取的麦麦省优惠券列表 |
| `auto-bind-coupons` | 一键领取所有可用券（无需指定 couponId） |
| `query-my-coupons` | 我已有的优惠券 |
| `query-my-account` | 积分账户（可用/累计/冻结/即将过期） |
| `mall-points-products` | 麦麦商城可积分兑换商品列表 |
| `mall-product-detail` | 商城商品详情 |
| `mall-create-order` | 积分兑换下单，返回券码 |
| `mall-order-list` / `mall-order-detail` | 商城订单查询/详情 |

### 其他

| 工具名 | 说明 |
| --- | --- |
| `list-nutrition-foods` | **餐品营养成分列表**（热量/蛋白质/脂肪/碳水/钠/钙） |
| `now-time-info` | 获取当前完整时间（帮助 LLM 知道日期）⭐ 建议默认注入 |
| `query-lottery-info` | 积分抽奖活动信息 |
| `draw-lottery` | 执行一次积分抽奖 |
| `query-my-prizes` | 我的奖品 |
| `query-party-city` / `query-party-store` | 主题活动城市/门店 |
| `query-partystore-date` / `query-partystore-session` | 主题活动可预约日期/场次 |
| `party-order-create` | 主题活动订单创建 |

## 5.2 意图 → 工具映射表（对话引擎使用）

| 意图 | 真实工具 | 触发话术 | 备注 |
| --- | --- | --- | --- |
| 查 TA 爱吃什么 ⭐ | **`order-list`** | "我上周吃了啥" / 开场记忆 | 核心"被记住"感；**只返回近期原始订单，聚合统计需本地做** |
| 报热量/营养 | **`list-nutrition-foods`** | "这个多少卡" | ⚠️ toon 紧凑格式，需专用解析器；本地缓存 |
| 推荐菜 | **`query-meals`** + **`query-meal-detail`** | "今天吃啥" | 结合画像 + 营养做二选一 |
| 查活动 | **`campaign-calendar`** | "最近有啥活动" | 缓存 30min |
| 领券 | **`available-coupons`** + **`auto-bind-coupons`** | "有啥券" / 下单前自动 | 领成功要口头播报 |
| 门店可用券 | **`query-store-coupons`** | 下单前精算 | 比 `available-coupons` 更贴合当前门店 |
| 我的券 | **`query-my-coupons`** | "我有哪些券" | 原文档写成 `my-coupons`，**名称错误** |
| 下单（到店取） | `query-meals` → `calculate-price` → `create-order` | "就这个" / "帮我下单" | 只到待支付。**`create-order` 必带 `takeWayCode`**（取自 `calculate-price` 返回的 `takeWayList`）；`.env` 已配门店时**无需**再 `query-nearby-stores`（实测省 1 轮，见 R23） |
| 下单（麦乐送） | `delivery-query-addresses` → `delivery-query-stores` → ... → `create-order` | "送到公司" | 传 `addressId` |
| 查积分/抽奖 | **`query-my-account`** / `query-lottery-info` / `draw-lottery` | "我多少积分" | "积分规划师"彩蛋 |
| 时间基准 | **`now-time-info`** | 开场自动调用 | ⭐ 让 LLM 正确理解"今天/上周" |

## 5.3 ⚠️ 已知数据格式坑

| 坑 | 说明 | 处理 |
| --- | --- | --- |
| **金额单位为「分」** | 所有金额需 ÷100 得元 | 在 MCP 层统一归一化，对外只暴露「元」 |
| **营养数据是 toon 紧凑格式** | 非标准 JSON，为省 Token 设计 | 专写解析器 + 单测；**解析失败时必须拒绝回答，不允许 LLM 编数字** |
| `order-list` 非商城订单 | 商城订单需 `mall-order-list` | 画像聚合时区分来源 |
| 订单 15 分钟支付窗口 | `create-order` 返回链接后超时失效 | 卡片上倒计时提示 |
| **`takeWayCode` 是必传项** | 到店场景 `create-order` 必带，取值只能来自 `calculate-price` 的 `takeWayList[].code`（`eat-in`/`locker-in`）；外送场景不得传 | 提示词写明取值来源 + 引擎兜底注入（默认 `eat-in`） |
| **`query-meals` 的 `data.meals` 是字典** | 形如 `{code: {name, currentPrice, ...}}`，**不是数组**（用下标会 KeyError） | 按 key 取值；大表先瘦身再回灌模型 |
| 大工具结果会被截断 | `query-meals` 原返 7000+ 字符，超 6000 上限后成为半截 JSON，模型读不懂 | 在 `engine._slim_result()` 里先压成紧凑文本 |

## 5.4 ✅ 实测结果回写（2026-10-10 完成）

| 项 | 实测值 |
| --- | --- |
| **生效的 MCP Server URL** | **`https://mcp.mcd.cn`**（仓库示例中的 `/mcp-servers/mcd-mcp` 实测未通过） |
| **握手成功的 SDK / 协议版本** | `mcp==1.12.0`（配 `pydantic==2.11.7`）/ 协议 **`2025-06-18`** |
| **`list_tools()` 返回工具总数** | **35 个**（§5.1 是按业务域归类，非逐条罗列） |
| 与本文档清单的差异 | 实测另有 `mall-order-list`、`mall-order-detail`、`query-partystore-*` 等；**完整清单见 [`../MCP_TOOLS.md`](../MCP_TOOLS.md)** |
| 各工具入参 / 出参样例 | Schema 见 [`../MCP_TOOLS.md`](../MCP_TOOLS.md)；接口原始返回样例见 `docs/samples/`（已 gitignore，含账号数据） |
| 对话引擎实际暴露的工具数 | **15 个**（`DIALOG_TOOLS`），原因见 [`../../MCP_INTEGRATION.md`](../../MCP_INTEGRATION.md) §2 |

### 实测补充的关键字段（文档里没有、踩过才知道）

| 字段 | 说明 |
| --- | --- |
| **`calculate-price` → `takeWayList[]`** | 返回 `eat-in`（堂食）/ `locker-in`（外带），是下一步 `create-order` 的 `takeWayCode` **唯一合法取值来源** |
| **`create-order` → `takeWayCode`** | 到店场景（`orderType=1`）**必传**，漏传直接建单失败；外送场景（`orderType=2`）**不得传**，传了报错 |
| `query-meals` → `data.meals` | 是 **`{code: {name, currentPrice, originalPrice}}` 字典**，不是数组（`meals[0]` 会 KeyError）；`data.categories[].meals[]` 只有 `{code, tags}` |
| `calculate-price` 嵌套金额 | `productList[].subtotal` 同样是**分**，只转顶层会漏 |
