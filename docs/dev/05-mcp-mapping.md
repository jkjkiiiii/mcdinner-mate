# 05 · ⭐ MCP 工具清单与意图映射

> **本文件是高频维护文件。Phase 1 跑通 `list_tools()` 后，必须把实测结果回写到这里。**
> 工具名来自官方文档 `open.mcd.cn/mcp/doc`（2026-10-10 核对）。中文名仅为意图描述，不是实际工具名。

## 5.1 官方真实工具清单

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
| 下单（到店取） | `query-nearby-stores` → `query-meals` → `query-meal-detail` → `query-store-coupons` → `calculate-price` → `create-order` | "就这个" / "帮我下单" | 只到待支付 |
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

## 5.4 Phase 1 待回写的实测结果

| 项 | 实测值 | 日期 |
| --- | --- | --- |
| 生效的 MCP Server URL | 待填 | |
| 握手成功的 `mcp` SDK 版本 / 协议版本 | 待填 | |
| `list_tools()` 返回的工具总数 | 待填（文档列 ~30） | |
| 与本文档清单的差异 | 待填 | |
| 各工具入参/出参样例 | 待填（写入 MCP_INTEGRATION.md） | |
