# workbuddy.md

> 本文件记录本项目使用 **WorkBuddy** 智能体辅助开发的对话上下文，
> 用于核验是否符合麦当劳程序员创意开发大赛「WorkBuddy 专项奖励」条件。

---

## 1. 使用声明

本项目（麦麦陪餐搭子 McDinnerMate）在开发过程中**真实使用了腾讯 WorkBuddy 智能体**，
参与环节包括：创意梳理、可行性评估、赛事规则核查、技术方案设计、文档撰写、
视觉设计（头图与吉祥物）与工程搭建。

- 项目地址：https://github.com/jkjkiiiii/mcdinner-mate
- 参赛：2026 麦当劳程序员创意开发大赛（2026-10-09 ~ 2026-10-25）

---

## 2. WorkBuddy 参与的具体环节

| 阶段 | 环节 | WorkBuddy 的工作 |
| --- | --- | --- |
| 立项 | 创意梳理 | 从"点餐效率"转向"陪伴情绪价值"，确立"一个人吃饭，但不孤单"定位 |
| 立项 | **可行性评估** | 输出 `FEASIBILITY.md`：6 维度评分、18 条风险、10 个待确认问题 |
| 合规 | **赛事规则核查** | 读取官方 `activityGuidelines.md` 与赛事仓库 README，逐条核对报名条件 |
| 合规 | 发现文件名硬伤 | 指出自造的 `SUBMISSION.md` / `MCP_SETUP.md` 不符合官方要求，纠正为 `CONTEST_DECLARATION.md` / `MCP_INTEGRATION.md`，并补出缺失的 `mcp-config.example.json`、`workbuddy.md` |
| 技术 | MCP 能力核对 | 对照官方 `open.mcd.cn/mcp/doc` 逐项验证 8 项核心能力是否存在 |
| 技术 | 风险识别 | 指出浏览器 Web Speech API 在国内不可用、MCP 协议版本限制、金额单位为「分」、营养数据 toon 格式等隐性坑 |
| 技术 | **环境搭建与联调** | 建 venv、装依赖、解决 `mcp`/`pydantic` 版本冲突、实测 MCP 连通性与 35 个工具清单 |
| 设计 | 视觉概念 | 确立"物理上一个人，但有一束对话的光"的创意内核 |
| 设计 | **吉祥物与头图** | 设计「光团子」并产出 SVG 矢量稿与成品头图；修复光晕方形虚框、锯齿、半透明挖穿三个渲染缺陷 |
| 文档 | 文档工程 | 将单份实施文档拆分为 12 份模块化文档，建立 `docs/dev` 与 `docs/design` 分层 |
| 运营 | 传播策略 | 拉取官方实时榜单数据，测算进榜 Star 门槛与竞品格局 |
| 交付 | **真实下单验证** | 走通 `calculate-price → create-order`，真实订单停在「待支付」，全程未触发支付 |
| 交付 | **Demo 视频制作** | 用 Playwright 驱动真实前端跑完整剧本、逐幕截图，再合成 1920×1080 带旁白字幕的 MP4 |
| 质量 | **界面缺陷修复** | 发现并修复：订单卡只剩订单号（`create-order` 不回展示字段）、模型把 `**加粗**` 与 `file:///D:/...` 本地路径吐进气泡 |

---

## 3. 关键对话要点摘录

- **创意定位**：本产品主角是「饭搭子」而不是「吃饭的人」，用户是代入方而非被观看对象。
- **合规约束**：赛事禁止讽刺/贬低麦当劳品牌，故人设默认值定为 `gentle`（温柔树洞），
  `sarcastic` 仅作为可选项且限制吐槽对象为工作与生活。
- **技术选型**：ASR 放弃浏览器 Web Speech API（国内不可用），改用本地 Whisper；
  本机 RTX 5090 D 用于本地推理。
- **渲染修复**：PIL 绘制吉祥物时踩到三个坑——`radial_gradient` 未归一化导致方形虚框、
  未超采样导致锯齿、RGBA 图层半透明绘制是"写入"而非"混合"导致挖穿背景。

---

## 4. 产出物

| 类型 | 文件 |
| --- | --- |
| 可行性评估 | [`FEASIBILITY.md`](FEASIBILITY.md)（6 维度评分 + 风险清单 + 开工前 GO/NO-GO 复审） |
| 开发文档（12 份） | [`docs/dev/00~11`](docs/dev/)、[`docs/design/BANNER.md`](docs/design/BANNER.md) |
| MCP 接入说明 | [`MCP_INTEGRATION.md`](MCP_INTEGRATION.md) |
| 真实工具清单 | [`docs/MCP_TOOLS.md`](docs/MCP_TOOLS.md)（35 个工具名 + 入参 Schema） |
| 视觉资产 | [`assets/banner-final-1280x640.png`](assets/banner-final-1280x640.png)、[`assets/mascot.svg`](assets/mascot.svg)、[`assets/report-card-sample.png`](assets/report-card-sample.png) |
| **演示视频** | [`assets/demo-video.mp4`](assets/demo-video.mp4)（90s，1920×1080，真实界面 + 旁白字幕）、[`assets/demo-chat.gif`](assets/demo-chat.gif)、[`assets/demo-showcase.png`](assets/demo-showcase.png) |
| 探测 / 验证脚本 | `scripts/mcp_probe.py`、`mcp_smoke.py`、`fetch_account_info.py`、`mcp_price_check.py`、`mcp_create_order.py`、`e2e_smoke.py`、`asr_check.py`、`debug_turn.py` |
| 素材工具 | `tools/make_demo.py`（GIF/拼图）、`tools/record_demo.py`（真实浏览器录制）、`tools/make_demo_video.py`（视频合成） |
| 离线单测 | `tests/`（29 个用例，不联网、不需要 Token） |

---

## 5. 开发过程中的关键决策记录

WorkBuddy 不只写代码，几个决定项目成败的判断也来自它：

| 判断 | 内容 |
| --- | --- |
| **定位转向** | 从"点餐效率"转向"陪餐情绪价值"——避开与百余个同类工具的红海竞争 |
| **合规优先** | 赛事禁止讽刺贬低品牌，故人设默认 `gentle`；`sarcastic` 仅吐槽工作与生活 |
| **文件名纠错** | 指出自造的 `SUBMISSION.md` / `MCP_SETUP.md` 不符合官方要求，纠正为官方指定的 `CONTEST_DECLARATION.md` / `MCP_INTEGRATION.md`，并补出缺失的 `mcp-config.example.json`、`workbuddy.md` |
| **算价链路提速** | e2e 实测发现算价要 5 轮 128 秒才完成，逐轮抓 `tool_calls` 定位到两处浪费，优化后 **3 轮 20 秒（提速 6.4 倍）**，详见 `docs/dev/10-risks.md` |
| **依赖版本锁定** | 定位 `mcp 1.12` ↔ `pydantic<2.12` 冲突；定位 PyAV 19 移除 `metadata_errors` 导致 faster-whisper 报错 |
| **不美化实测数据** | 演示视频里每幕标注真实推理耗时（20–134 秒/轮），加速剪辑但**不谎称秒回** |
| **演示素材不造假** | 拒绝为好看而编数字：曾发现拼图把「单品 ¥33.5」与「两件合计 4150 分」并列写成"严格一致"，重新实测后全部改正 |

---

*本文件由 WorkBuddy 在 2026-10-10 生成，内容随开发进展更新。*
