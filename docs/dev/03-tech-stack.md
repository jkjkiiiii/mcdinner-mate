# 03 · 技术选型与决策记录

> 原则：**能跑 > 完美**。15 天单人赛程，任何"更优雅但需要调试"的选型都应让位。

## 3.1 选型表

| 层 | MVP 选型 | 升级项（有余力） | 理由 |
| --- | --- | --- | --- |
| 后端 | Python 3.12/3.13 + FastAPI | — | MCP 官方 SDK 生态最成熟，异步友好 |
| MCP 客户端 | 官方 `mcp` Python SDK（`streamablehttp_client`） | — | 直连官方 MCP，**须 pin ≤ 2025-06-18 协议版本** |
| 对话引擎 | `{{LLM_API_KEY}}`（tool-calling 模型） | 流式输出 | 人设 + 工具调度都靠它 |
| **ASR** | ⚠️ **本地 `faster-whisper` / `SenseVoiceSmall`（GPU）** | 流式 ASR | 见 ADR-001（**已变更**） |
| TTS | `edge-tts`（免费）+ 浏览器 `speechSynthesis` 兜底 | 讯飞/Azure/本地 Kokoro | 先让链路跑通 |
| VAD | SileroVAD（随本地 ASR 引入） | — | 打断（barge-in）必需 |
| 前端 | 单页 HTML/JS + MediaRecorder + WebSocket | H5 美化 | Demo 快 |
| 存储 | SQLite + JSON | — | 对话记录、用户画像、菜单缓存 |
| 分享卡片 | HTML 模板 + Pillow 渲染 PNG | Playwright 截图 | 传播点 |
| 部署 | 本地 + 内网穿透演示 | Docker | 比赛不强制上线 |

## 3.2 ADR-001：ASR 从 Web Speech API 改为本地 Whisper

- **状态**：✅ **已采纳并验证通过**（2026-10-10）
- **背景**：原方案 ASR 用浏览器 `Web Speech API`，理由"零成本、不依赖 Key"。
- **问题**：Chrome/Edge 的语音识别由 Google 服务提供，**中国大陆网络环境基本不可用**；而语音是本项目的核心交互入口，不可降级。届时会在 Phase 3 才暴露，返工成本极高。
- **决策**：改用本地 ASR。
  - **最终采用**：`faster-whisper` + **`large-v3`**，CTranslate2 加速，`float16` on CUDA
  - 备选（未采用）：`FunASR / SenseVoiceSmall`（中文效果更好，支持情感/事件标签）
- **收益**：零网络依赖、零 API 成本、自带 VAD（顺带解决打断需求）、可利用闲置 5090D
- **代价**：模型 3.09GB，首次需下载（走 `hf-mirror.com`）
- **✅ 验证结果**（2026-10-10 实测）
  - 音频「今天加班到九点，累死了，想吃个麦辣鸡腿堡」（4.7s）
    → 识别「今天加班到9点,累死了,想吃个麦辣鸡腿堡。」，耗时 **14.9s（含首次模型加载）**
  - 验证脚本：`scripts/asr_check.py`
- **⚠️ 实测踩到的两个坑**
  1. **HF 缓存静默失败**：`snapshot_download` 报成功，但缓存里文件全是 **0 字节**，
     直到加载时才炸 `File model.bin is incomplete`。改为 curl 直下到本地目录、
     `ASR_MODEL` 填绝对路径即可绕开（本地目录入参 `WhisperModel` 原生支持）。
  2. **必须锁 `av<19`**：PyAV 19 移除了 faster-whisper 在用的 `metadata_errors` 参数，
     装到最新版直接 `TypeError`。上游只声明 `av>=11`，所以必须自己锁 `av>=14,<19`。

## 3.3 ADR-002：Python 版本用 3.12/3.13 而非 3.11

- **状态**：✅ 建议采纳
- **背景**：原方案指定 Python 3.11，本机无 3.11（有 3.13.14 / conda 3.12.x）
- **决策**：直接用 3.12 或 3.13。`mcp` / `fastapi` / `uvicorn` 均兼容。
- **理由**：赛中引入"装 3.11"这个变量没有收益，只有风险。

## 3.4 ADR-003：MCP SDK 必须 pin 版本

- **状态**：✅ 必须执行
- **背景**：官方明确 **仅支持 MCP Version 2025-06-18 及之前**
- **决策**：`requirements.txt` 中固定 `mcp` 版本，Phase 0 先跑最小握手脚本验证 `initialize` + `list_tools` 成功，再进入 Phase 1
- **失败处理**：握手失败时优先降级 SDK 版本，而非排查业务代码

## 3.5 ADR-004：人设默认值改为 `gentle`

- **状态**：🟠 待确认
- **背景**：原方案默认 `sarcastic`（毒舌麦门信徒）
- **问题**：赛事规则禁止"讽刺、贬低麦当劳品牌/产品/形象"，毒舌风格有实质合规风险
- **决策**：默认 `gentle`；`sarcastic` 保留为可选项，但 prompt 中显式约束"只吐槽工作/生活，不吐槽麦当劳"

## 3.6 依赖清单（`requirements.txt` 初稿）

```
fastapi
uvicorn[standard]
mcp              # 固定版本，见 ADR-003
httpx
python-dotenv
openai           # 兼容 OpenAI 协议的 LLM 客户端（Kimi/DeepSeek 均适用）
edge-tts
pillow
faster-whisper   # ADR-001，或用 funasr
# 可选
playwright
pytest
```

> 安装一律用 `uv` 装进项目 venv，pip 走清华源。
