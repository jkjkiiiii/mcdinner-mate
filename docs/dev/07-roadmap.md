# 07 · 阶段拆解、排期与降级预案

> 赛事截止：**2026-10-25 23:59**　|　定榜：2026-10-26 00:00　|　评估日：2026-10-10（剩 15 天）

## 7.0 进度快照（2026-10-10 22:00）

| Phase | 状态 | 说明 |
| --- | --- | --- |
| 0 环境与凭证 | ✅ | venv / 依赖 / Token / 门店 1950814 / 收货地址 全部就位 |
| 1 MCP 打通 | ✅ | 地址 `https://mcp.mcd.cn`、协议 2025-06-18、35 工具；`server/mcp_client.py` + 离线单测 |
| 2 对话引擎 | ✅ | persona(两套)/状态机/engine；本地 Qwen3.8-27B-VL tool calling 实测可用；**算价链路提速 6.4×** |
| 3 语音链路 | ✅ | **ASR 已跑通**（faster-whisper large-v3 / 5090D / 4.7s 音频识别准确）；TTS ✅；前端单页 ✅ |
| 4 下单与报告 | ✅ | 报告卡 ✅；算价链路实测通过（三件套 ¥33.5 = `price: 3350` 分）；**真实建单已跑通，停在「待支付」**；订单确认卡片 ✅ |
| 5 打磨与交付 | ✅ | 参赛五件套 ✅、**报名 Issue [#356](https://github.com/M-China/mcd-developer-innovation-challenge/issues/356) 已提交**、开发文档 13 份已入库；**Demo 视频已录制合成** |
| 传播 | 🟡 | 已进榜（第 50 名 / 5★ → 实时 7★）。实测门槛同日 1★→3★，**推广需持续推进** |

**关键实现教训**（已沉淀，勿再踩）：
- 35 个 MCP 工具全量喂给 27B 模型 → `finish_reason=length` 空回复 → 工具白名单裁到 15 个
- 读工具不应按阶段限制（早期导致问热量时拿不到营养工具）
- 写操作（create-order 等）**永不重试**，避免重复下单
- MCP 返回正文含 `{字段名}` 占位花括号，解析须定位 `{"success"` 起点
- **大工具结果必须先瘦身再回灌**：`query-meals` 原返 7258 字符会被 6000 上限截成半截 JSON，
  模型读不懂就只能反复查详情 → 白烧 4 轮。压成 `code|名称|现价|原价` 后 3183 字符，一次看全
- **默认配置要显式写进系统提示**：不告诉模型"门店已配好"，它就会白跑一轮查店，还会挑错店
- **依赖要锁窄**：`av` 上游声明 `>=11`，但 19.x 移除了 faster-whisper 在用的
  `metadata_errors` 参数 → 必须 `av>=14,<19`

## 7.1 Phase 0 — 环境与凭证（Day 1-2）

- [ ] 建 GitHub 公开仓库 `jkjkiiiii/mcdinner-mate` 并首次提交（**尽早公开，Star 从现在开始积累**）
- [ ] 落地 5 个参赛必需文件（见 [09-submission.md](./09-submission.md)）
- [ ] 申请 MCP Token；填写 `{{TEST_PHONE}}` / `{{DEFAULT_STORE_ID}}` / 收货地址
- [ ] `uv` 建 venv，`pip install -r requirements.txt`（走清华源）
- [ ] **【新增】MCP 最小握手验证**：pin SDK 版本 → 两个 URL 都试 → `initialize` + `list_tools` 成功
- [ ] **【新增】ASR 可行性验证**：5090D 上跑一次本地 Whisper，实测中文延迟
- [ ] **【新增】定义 WebSocket 协议 + SQLite schema**

- **验收**：`python -c "from server.config import settings"` 不报错；MCP 握手脚本输出工具清单

## 7.2 Phase 1 — MCP 打通（Day 2-4）

- [ ] `mcp_client.py`：连接 + `list_tools` 成功
- [ ] 实测结果回写 [05-mcp-mapping.md](./05-mcp-mapping.md)，并写入 `MCP_INTEGRATION.md`
- [ ] 封装并各写 1 个 pytest：`order-list`、`query-meals`、`query-meal-detail`、`list-nutrition-foods`、`campaign-calendar`、`available-coupons`、`query-my-coupons`
- [ ] 30min 内存缓存 + 失败重试 1 次 + 退避
- [ ] **金额单位归一化（分 → 元）**、**营养 toon 格式解析器 + 单测**

- **验收**：脚本依次调用 7 个查询，输出格式化结果，无 401/429

## 7.3 Phase 2 — 对话引擎（Day 4-8）

- [ ] `persona.py`：两版 prompt（`gentle` 默认），含合规约束
- [ ] `engine.py`：LLM tool-calling 主循环（MCP 工具动态映射 + 本地工具：生成报告卡/切换人设）
- [ ] `state_machine.py` + `intents.py`：实现状态机，**补全每状态的进入动作/出口条件/兜底话术**
- [ ] 画像聚合层：`order-list` 原始数据 → "上周吃了 3 次麦辣"
- [ ] 纯文字版跑通完整流程（CLI）

- **验收**：CLI 走通"开场→推荐→领券→建单→报告"全流程，含一次工具失败兜底

## 7.4 Phase 3 — 语音链路（Day 8-12）

- [ ] `web/` 单页：录音按钮（MediaRecorder）→ WebSocket；字幕气泡；卡片展示区
- [ ] `asr.py`：本地 Whisper（主）+ 云端（备）
- [ ] `vad.py`：SileroVAD，实现打断
- [ ] `tts.py`：edge-tts（主）+ 浏览器 speechSynthesis（兜底）

- **验收**：浏览器里说"今天好累"→ 听到完整语音回复 + 字幕

## 7.5 Phase 4 — 下单与报告（Day 12-15）

- [x] 下单封装：入参校验（门店/商品/modification/预约时间）→ `calculate-price` → `create-order` → 只到待支付
- [x] 前端订单确认卡片（门店/取餐方式/金额/支付时限/订单号 + 「本工具不代付」）
      —— **刻意不做**支付链接与倒计时：不引导、不代付
- [x] `report/card.py`：Pillow 渲染 1080×1080 分享卡

- **验收**：真实账号完成一次到店取"待支付"订单（¥33.5，**未支付**，15 分钟后自动失效）✅

> ⚠️ **订单卡字段坑**：`create-order` 的返回**实测只带 `orderId`**，门店/金额/取餐方式/支付时限
> 全在 `query-order` 里。不补一次回读，前端订单卡就只剩一个订单号（已踩）。
> 补丁：`DialogEngine._enrich_order()` —— 只在缺字段时回读，且**建单结果优先、绝不覆盖**。

## 7.6 Phase 5 — 打磨与交付（Day 15，与传播并行）

- [x] `README.md`（参赛四要素：项目介绍/安装方法/使用示例/目标用户）+ 架构图 + Demo 视频
- [x] `MCP_INTEGRATION.md`、`mcp-config.example.json`、`CONTEST_DECLARATION.md`、`workbuddy.md`
- [ ] 限流压测：连续对话 5 分钟不触发 429
- [x] 录 Demo 视频（90s，1920×1080，真实界面截图 + 旁白字幕）
      —— `tools/record_demo.py` 采集 → `tools/make_demo_video.py` 合成
- [x] **提交报名 Issue（#356，不带图片）**

## 7.7 排期（两套）

| 场景 | 策略 |
| --- | --- |
| **每日 ≥6h** | 保留全部 Phase；功能冻结 10/22，10/23 提交报名，10/24 定稿，10/25 只做传播 |
| **每日 ≤3h** | 砍：下单降级为模拟订单卡、不做积分彩蛋、视频录屏直出不剪辑；**报告卡必须真实** |

> ⚠️ 原文档"缓冲约 4 天"与"最后 3 天只打磨"自相矛盾（10/22→10/25 只有 3 天），以本文件为准。

## 7.8 降级预案（按优先级）

| 优先级 | 模块 | 降级方式 |
| --- | --- | --- |
| P0 ❗不可降级 | 历史订单记忆、营养播报、报告卡 | 无 |
| P1 | 语音链路 | 若 ASR 实在跑不通 → 退化为文字输入 + TTS 播报（保住"陪伴"的一半） |
| P2 | 真实下单 | → 模拟订单确认卡片（数据来自真实 `calculate-price`，仅不调 `create-order`） |
| P3 | 领券播报 | → 只查询不自动领取 |
| P4 | 分享卡美化 | → Pillow 简单模板 |
| P5 | 积分/抽奖彩蛋 | → 直接砍 |

> **注意**：`create-order` 会真实创建订单并占用 15 分钟支付窗口与库存。Demo 前用测试小号、小额，不要反复创建。
