# 02 · 环境、凭证与本机约束

## 2.1 占位符清单

统一格式 `{{XXX}}`，⭐ 为必须项。集中在 `.env.example`。

| 占位符 | 说明 | 获取方式 | 状态 |
| --- | --- | --- | --- |
| `{{MCP_TOKEN}}` ⭐ | 麦当劳 MCP 访问 Token | 打开 open.mcd.cn/mcp，手机号登录后控制台激活，免费 | ❌ 待申请 |
| `{{MCP_SERVER_URL}}` | MCP 服务端地址 | 见 2.2 | ⚠️ 待实测 |
| `{{LLM_API_KEY}}` ⭐ | 大模型 API Key | Kimi(platform.moonshot.cn) / DeepSeek / 通义，**须支持 tool calling** | ❌ 待申请 |
| `{{LLM_MODEL}}` | 模型名 | 以平台实际可用 tool-calling 模型为准 | ❌ 待定 |
| `{{ASR_API_KEY}}` / `{{ASR_SECRET}}` | 语音识别 | 见 2.3，**推荐改用本地方案，此项可留空** | ⚪ 可选 |
| `{{TTS_API_KEY}}` | 语音合成 | MVP 用 `edge-tts` 免费方案，此项可留空 | ⚪ 可选 |
| `{{TEST_PHONE}}` ⭐ | 麦当劳 App 登录手机号（测试账号） | 用于下单链路与历史订单真实数据 | ❌ **待填（阻塞 Phase 4）** |
| `{{DEFAULT_STORE_ID}}` ⭐ | 常用门店 ID | `query-nearby-stores` 抓取 | ❌ **待填（阻塞 Phase 4）** |
| `{{DELIVERY_ADDRESS}}` / `{{ADDRESS_ID}}` | 外卖收货地址 | `delivery-query-addresses` 抓取 | ❌ 待填 |
| `{{LAT}}` / `{{LON}}` | 门店/收货经纬度 | 上述地址对应坐标 | ❌ 待填 |
| `{{GITHUB_USERNAME}}` ⭐ | GitHub 用户名 | 已确认：**jkjkiiiii** | ✅ |
| `{{REPO_NAME}}` | 仓库名 | 建议 `mcdinner-mate` | ❌ 待确认 |
| `{{PORTRAIT_MODE}}` | 人设 `sarcastic` / `gentle` | **建议默认改为 `gentle`**（合规考虑，见 01-product §1.7） | ⚠️ 待决策 |

## 2.2 MCP 服务端地址（两个版本，Phase 1 必须实测）

| 来源 | 地址 |
| --- | --- |
| 官方赛事 README + WorkBuddy 官方指南 | `https://mcp.mcd.cn` |
| `M-China/mcd-mcp-server` 仓库与多数第三方示例 | `https://mcp.mcd.cn/mcp-servers/mcd-mcp` |

- 认证：`Authorization: Bearer {{MCP_TOKEN}}`，Streamable HTTP
- **限流：600 次/分钟/Token，超限返回 429**
- ⚠️ **协议版本：仅支持 MCP Version 2025-06-18 及之前版本**（用新版 SDK 有握手失败风险，必须 pin 版本）
- 服务区域：仅中国大陆（不含港澳台）

> 两个地址都要试一次，实测结果回写到 [05-mcp-mapping.md](./05-mcp-mapping.md)。

## 2.3 本机环境实测结果（2026-10-10）

| 项 | 实测 | 结论 |
| --- | --- | --- |
| `uv` | `0.10.9` | ✅ 可用，用于项目内 venv |
| `python` | `3.13.14` | ✅ 可用（原方案写 3.11，本机没有，建议改用 3.12/3.13） |
| `conda` | `24.9.2`（含 Python 3.12） | ✅ 备选 |
| `git` | `2.55.0` | ✅ |
| `gh` | `2.96.0`，已登录 `jkjkiiiii` | ✅ |
| GPU | **NVIDIA GeForce RTX 5090 D，32 GB** | ⭐ **原方案完全未利用** — 建议用于本地 ASR/TTS |
| 项目 git 仓库 | ❌ 尚未初始化 | 需创建（仓库创建时间须在 2025-12-25 ~ 2026-10-25 窗口内） |

## 2.4 本机硬性约定（来自原文档"本机特性"，继续执行）

1. Python 环境用 `uv` 装到**项目内 venv**，不污染全局
2. `pip` / HuggingFace 模型下载一律走**国内源**（避免下载失败）
   - pip：`-i https://pypi.tuna.tsinghua.edu.cn/simple`
   - HF：`HF_ENDPOINT=https://hf-mirror.com`
3. `.env`、`mcp-config.json`、Token 等**必须写入 `.gitignore`**，公开仓库严禁泄露
4. GPU 优先用于本地推理（ASR）

## 2.5 缓存与限流策略（强制）

- 菜单、营养、活动日历等静态数据：**本地缓存 ≥ 30 分钟**
- 所有查询：**失败重试 1 次 + 指数退避**
- **Demo 前重启服务清缓存并重跑一遍** [08-test-cases.md](./08-test-cases.md)，避免现场 429
