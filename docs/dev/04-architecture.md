# 04 · 系统架构与目录结构

## 4.1 架构图

```
┌────────────── 浏览器（单页）──────────────┐
│  录音(MediaRecorder)  播放(audio)  卡片展示  │
└──────────────────┬───────────────────────┘
                   │ WebSocket (音频帧 + 事件)
┌──────────────────▼───────────────────────┐
│  FastAPI 后端                             │
│  ┌─────────┐  ┌───────────────────────┐  │
│  │ ASR 适配 │→ │ 对话引擎 (LLM+tools)  │  │
│  │ +VAD    │  │  · 人设 system prompt │  │
│  └─────────┘  │  · 状态机              │  │
│  ┌─────────┐  │  · tool schema 映射    │  │
│  │ TTS 适配 │← │  · 记忆读写(SQLite)   │  │
│  └─────────┘  └─────────┬─────────────┘  │
│  ┌──────────────────────▼─────────────┐  │
│  │ MCP 工具层（缓存/限流/单位归一化/兜底）│  │
│  └──────────────────────┬─────────────┘  │
└─────────────────────────┼────────────────┘
                          │ Streamable HTTP
                   https://mcp.mcd.cn (Bearer {{MCP_TOKEN}})
```

## 4.2 一轮完整对话的数据流

1. 浏览器推音频（MediaRecorder）→ 后端 ASR 出文本
2. 对话引擎组装 prompt（人设 + 记忆 + 最近对话）→ LLM tool calling
3. LLM 决策调用 MCP 工具 → MCP 层（先查缓存）→ `mcp.mcd.cn` → 结果回灌 LLM
4. LLM 生成回复 → TTS 播报 + 前端渲染卡片（订单卡 / 报告卡）
5. 关键事件写 SQLite（订单、画像更新）

## 4.3 待补充的设计（开工前必须定义，否则 Phase 2 返工）

| # | 待定义项 | 说明 |
| --- | --- | --- |
| 1 | **WebSocket 消息协议** | 帧类型（`audio` / `text` / `event` / `card` / `error`）、二进制 vs JSON、分片与结束标志 |
| 2 | **SQLite schema** | `users` / `messages` / `orders` / `profile` / `cache` 表结构 |
| 3 | **会话与并发管理** | session id 绑定、单页面多轮、断线重连 |
| 4 | **MCP 错误分级与兜底** | 401 / 429 / 超时 / 业务错误分别如何处理；退避与熔断 |
| 5 | **打断（barge-in）机制** | VAD 触发 → 停止 TTS 播放 → 切到收音，需防回声误触发 |

## 4.4 目录结构

```
mcdinner-mate/
├── README.md                    # ⭐参赛必须：项目介绍/安装/使用示例/目标用户（文件名不可改）
├── CONTEST_DECLARATION.md       # ⭐参赛必须：官方原文件，内容不可改动
├── MCP_INTEGRATION.md           # ⭐参赛必须：MCP Server/Tool/调用流程/业务价值（文件名不可改）
├── mcp-config.example.json      # ⭐参赛必须：脱敏配置示例，仅环境变量占位符
├── workbuddy.md                 # ⭐WorkBuddy 专项奖励必须（文件名不可改）
├── FEASIBILITY.md               # 可行性评估
├── .env.example / .gitignore
├── requirements.txt
├── docs/
│   └── dev/                     # 开发过程文档（本目录）
├── server/
│   ├── main.py                  # FastAPI 入口
│   ├── config.py                # 读 .env，占位符未填时启动报错
│   ├── mcp_client.py            # MCP 连接/工具列表/缓存/重试/单位归一化
│   ├── dialog/
│   │   ├── engine.py            # LLM tool-calling 主循环
│   │   ├── persona.py           # 人设 prompt（gentle / sarcastic）
│   │   ├── state_machine.py     # 状态机
│   │   └── intents.py           # 意图路由
│   ├── memory/
│   │   ├── profile.py           # 画像：爱吃的/常去的/平均客单/频率
│   │   └── db.py                # SQLite
│   ├── voice/
│   │   ├── asr.py               # 本地 Whisper / 云端 双适配
│   │   ├── vad.py               # SileroVAD（打断）
│   │   └── tts.py               # edge-tts / 浏览器 双适配
│   ├── report/
│   │   └── card.py              # 饭后报告 PNG 生成
│   └── routers/
│       └── ws.py                # WebSocket 路由
├── web/
│   ├── index.html               # 单页：录音按钮/字幕气泡/卡片区
│   └── app.js
└── demo/
    └── demo_video.mp4           # ≤3 分钟
```

> ⚠️ 原方案把参赛文档放在 `docs/` 下（`docs/SUBMISSION.md` / `docs/MCP_SETUP.md`），**文件名不符合官方要求且位置有核验风险**，已改为根目录 + 官方文件名。详见 [09-submission.md](./09-submission.md)。
