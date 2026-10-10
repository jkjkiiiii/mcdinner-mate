# 10 · 风险登记册

> 严重度：🔴 致命 / 🟠 高 / 🟡 中 / ⚪ 低
> 状态：Open（未处理）/ Mitigating（缓解中）/ Closed（已关闭）/ Accepted（接受）

| ID | 风险 | 严重度 | 触发条件 | 缓解措施 | 状态 |
| --- | --- | --- | --- | --- | --- |
| R1 | 交付文件名不符合官方要求 → **报名失败** | 🔴 | 原样提交 `docs/SUBMISSION.md` | 改用官方文件名 + 官方原版声明文件，放根目录 | ✅ Closed（已用官方文件名，声明文件逐字节一致） |
| R2 | 缺 `mcp-config.example.json` → 报名失败 | 🔴 | 原样提交 | 补脱敏配置示例（仅环境变量占位符） | ✅ Closed（已补脱敏示例） |
| R3 | ASR（Web Speech）国内不可用 → 核心玩法失效 | 🔴 | Phase 3 才暴露 | 改本地 Whisper/SenseVoice（5090D），Phase 0 先验证 | ✅ Closed（本地 faster-whisper 已跑通） |
| R4 | 无 Star 传播 → 名次为零 | 🔴 | 只顾开发 | 传播与开发并行，见 [11-promotion.md](./11-promotion.md) | 🟠 Open（报名 #356 已提交，推广待启动） |
| R5 | "毒舌"人设触碰内容合规红线 | 🟠 | 评委人工审核 | 默认改 `gentle`；`sarcastic` 加显式边界约束 | ✅ Closed（默认 gentle + 边界约束） |
| R6 | MCP SDK 版本 > 2025-06-18 → 握手失败 | 🟠 | Phase 1 | pin 版本 + 首日最小握手验证 | ✅ Closed（pin 1.12.0，协议 2025-06-18 已验证） |
| R7 | 营养 toon 格式解析错误 → 热量数字造假 | 🟠 | 测试用例 #2 | 专用解析器 + 单测；解析失败拒绝回答 | ✅ Closed（专用解析器 + 单测） |
| R8 | 金额单位（分 vs 元）错误 → 卡片金额与官方不符 | 🟠 | 测试用例 #4 | MCP 层统一归一化 | ✅ Closed（add_yuan_fields 统一归一化） |
| R9 | MCP 限流 429（600/分/Token） | 🟡 | Demo 连续对话 | 30min 缓存 + 退避；Demo 前预热 | ✅ 已压测（30/30 无 429） |
| R10 | 真实下单占用库存 / 15 分钟支付窗口 | 🟡 | Phase 4 | 小号、小额、保留模拟订单卡降级 | 🟠 Open（待用户手动确认） |
| R11 | edge-tts 不稳定（403/限流） | 🟡 | Demo 现场 | 浏览器 speechSynthesis 兜底 | 🟡 Open（有 speechSynthesis 兜底） |
| R12 | 工期不足，Phase 3/4 无法完成 | 🟠 | 业余投入 | 提前定降级预案；报告卡必须真实 | ✅ Closed（全链路已通） |
| R13 | Token / 手机号等敏感信息泄露到公开仓库 | 🟡 | 提交时疏忽 | `.gitignore` + 提交前扫描 | ✅ Closed（git grep 三查全过） |
| R14 | MCP Server URL 有两个版本，连错浪费时间 | 🟡 | Phase 1 | 两条路径都试并记录 | ✅ Closed（实测 https://mcp.mcd.cn 可用） |
| R15 | VAD 被 TTS 回声误触发，打断失效 | 🟡 | Phase 3 | 回声消除 / 播放期压制 VAD | 🟡 Open |
| R16 | `order-list` 只返回"近期"订单，画像聚合不准 | 🟡 | Phase 2 | 本地 SQLite 做聚合；话术避免"上周"等强断言 | ✅ Closed（本地 SQLite 聚合） |
| R17 | LLM API 成本超预算（多轮 tool-calling） | 🟡 | 压测/长时间 Demo | 设花费上限；控制上下文长度 | ✅ n/a（本地模型，零推理成本） |
| R18 | 仓库创建时间不在窗口内 | ⚪ | 现已 2026-10-10，在窗口内 | **已创建**（2026-10-10） | ✅ Closed（2026-10-10 创建，在窗口内） |
| R19 | **仓库未创建 → Star 无法积累、无法报名** | 🔴 | 持续拖延 | 今天建公开仓库 + git init + 首次提交 | ✅ Closed（仓库已创建并公开） |
| R20 | **Star 门槛上涨**（同日 15:00 实测 1★，20:00 已涨至 **3★**） | 🟠 | 10/20 后 | 目标 10~20★ 而非 1★；传播与开发并行 | 🟠 Open（门槛已涨至 3★） |
| R21 | 榜单竞品拥挤（141 个上榜）但同质化严重 | 🟡 | — | 差异化落在"陪餐陪伴/情绪价值"，目前无人占位 | 🟡 Mitigating |
| R22 | `create-order` 到店场景 `takeWayCode` 必传，模型漏传 → 整单失败 | 🟠 | 用户说「下单」 | 引擎兜底注入（默认 `eat-in`）+ 提示词写明取值来源；外送场景不得带 | ✅ Closed |
| R23 | **算价链路 5 轮耗尽**（128s 后回落兜底话术「我卡了一下」） | 🔴 | e2e 第 3 轮复现 | 注入默认门店省 1 轮 + `_slim_result()` 压菜单省 4 轮 → **3 轮 20s，提速 6.4×** | ✅ Closed |
| R24 | PyAV 19 移除 `metadata_errors`，faster-whisper 启动即 TypeError | 🟠 | 装到最新 av | `requirements.txt` 锁 `av>=14,<19` 并注明原因 | ✅ Closed |
| R25 | ASR 模型 HF 缓存静默失败（文件 0 字节却报成功） | 🟠 | 首次加载 | curl 直下到本地目录，`ASR_MODEL` 填绝对路径 | ✅ Closed |

## 10.1 每周复盘要点

1. 是否有新 Closed 的风险
2. **R4（Star 传播）/ R10（真实下单）/ R20（门槛上涨）** 是否仍 Open —— 这三是当前命门
   （R1/R2/R3/R13/R19 等报名与合规类风险已全部 Closed）
3. 是否出现新风险 → 追加到本表并同步到 `FEASIBILITY.md`
