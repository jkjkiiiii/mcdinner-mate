<p align="center">
  <img src="assets/banner-final-1280x640.png" alt="麦麦陪餐搭子" width="100%">
</p>

<h1 align="center">麦麦陪餐搭子 · McDinnerMate</h1>

<p align="center">
  <b>一个人吃饭，但不孤单。</b><br>
  基于麦当劳 MCP 的语音陪餐陪伴 Skill —— 不只是点餐，是有人陪你吃完这顿饭。
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> ·
  <a href="#它到底能干什么">功能</a> ·
  <a href="#架构">架构</a> ·
  <a href="MCP_INTEGRATION.md">MCP 接入说明</a> ·
  <a href="#目标用户">目标用户</a>
</p>

---

## 它解决什么问题

一个人吃饭这件事，难吃的不是饭，是**没人说话**。

市面上的点餐助手都在解决"怎么更快地点完"，但没人解决"这一顿饭谁来陪"。麦麦陪餐搭子把麦当劳的真实数据（你吃过什么、热量多少、有什么券、附近哪家店）变成一个有记忆、会接话的饭搭子——**它记得你上周吃了三次麦辣鸡腿堡，也会在你加班到九点的时候陪你把这顿饭吃完**。

## 目标用户

- 一线城市 22–35 岁的独居打工人 / 程序员
- 工作日 17:00–21:00 的一人食场景（门店堂食 / 到店取 / 麦乐送外卖）
- 想要"有人陪着吃"，但不想社交的人

## 它到底能干什么

| 能力 | 说明 | 依赖的 MCP 工具 |
| --- | --- | --- |
| **记忆感** | 开场就知道你最近吃了什么，"上周你吃了 3 次麦辣，今天换个口味？" | `order-list` |
| **专业感** | 随口报热量、给替代方案，**数据全部来自官方接口，绝不编造** | `list-nutrition-foods` |
| **实利感** | 陪聊中顺手查活动、自动把券领好 | `campaign-calendar` / `available-coupons` / `auto-bind-coupons` |
| **闭环感** | 真的帮你下单，到"待支付"为止 | `query-meals` → `calculate-price` → `create-order` |
| **陪伴感** | 等餐和吃饭时陪你吐槽老板、需求和 bug | 本地大模型 + 人设 prompt |
| **仪式感** | 吃完生成一张可分享的饭后报告卡 | 本地渲染 |

### 一段真实对话

```
👤 "（打开页面）今天加班到九点，累死了……"
🤖 "辛苦了啊。我瞅瞅你最近吃了啥。"
   →【order-list】"你最近常点麦辣鸡翅和随心配。今天建议温柔点 ——
      双层吉士去酸黄瓜 + 无糖可乐，约 460 大卡，比你常点的那套轻一些。"
👤 "行，听你的"
🤖 "我看看有啥活动……有张券，已帮你领好 👌"
   →【campaign-calendar + auto-bind-coupons】
🤖 "老样子到店取？给你约了 21:00。"
   →【create-order】—— 展示订单确认卡片 ——
🤖 "下单了，去小程序支付就行。等餐这几分钟，吐槽吐槽今天？"
👤 "（陪聊……）"
👤 "我吃完了，走人"
🤖 "今日报告来了 📋" → 生成分享卡片
```

> ⚠️ 下单链路**只到"待支付"为止**，不集成支付、不自动支付，支付需前往麦当劳 App / 小程序完成。

### 明确不做

多端同步 · 真实支付 · 声纹 / 情感识别 · 推荐算法训练。
（不做这些不是偷懒，是为了在有限时间内把"陪伴"这件事做扎实。）

## 架构

```
┌────────────── 浏览器（单页）──────────────┐
│    录音(MediaRecorder)   播放   卡片展示    │
└──────────────────┬───────────────────────┘
                   │ WebSocket (音频帧 + 事件)
┌──────────────────▼───────────────────────┐
│  FastAPI 后端                             │
│  ASR(本地 Whisper) → 对话引擎(LLM+tools)  │
│  TTS(edge-tts)  ←   · 人设 prompt         │
│                     · 状态机              │
│                     · 记忆读写(SQLite)    │
│  MCP 工具层（缓存 / 限流 / 单位归一化）     │
└─────────────────────────┬─────────────────┘
                          │ Streamable HTTP
                   https://mcp.mcd.cn (Bearer Token)
```

一轮完整对话：录音 → 本地 ASR 出文本 → 组装 prompt（人设 + 记忆 + 近期对话）→ LLM 决策调工具 → MCP 层（先查缓存）→ 结果回灌 LLM → 生成回复 → TTS 播报 + 前端渲染卡片 → 关键事件写 SQLite。

## 快速开始

### 1. 申请 MCP Token（免费）

访问 [open.mcd.cn/mcp](https://open.mcd.cn/mcp) → 手机号登录 → 右上角「控制台」→ 激活 → 复制 Token。

### 2. 安装

```bash
git clone https://github.com/jkjkiiiii/mcdinner-mate.git
cd mcdinner-mate

uv venv .venv && .venv\Scripts\activate        # Windows
# source .venv/bin/activate                    # macOS / Linux
uv pip install -r requirements.txt

cp .env.example .env     # 填入你的 MCP_TOKEN
```

### 3. 验证 MCP 连通

```bash
python scripts/mcp_probe.py      # 输出生效地址、协议版本与真实工具清单
python scripts/mcp_smoke.py      # 只读冒烟测试，确认核心工具能取到数据
```

### 4. 启动

```bash
python -m server.main            # 打开 http://localhost:8000
```

> 默认使用本地大模型（vLLM / OpenAI 兼容接口，如 `http://localhost:8001/v1`）。
> 没有本地模型也没关系，把 `.env` 里的 `LLM_BASE_URL` / `LLM_API_KEY` 换成任意支持 tool calling 的云端服务即可。

## 为什么必须用 MCP

没有 MCP，这就是个普通的聊天机器人。是 MCP 让它变成"饭搭子"：

- **它真的记得你** —— 历史订单是真实数据，不是人设扮演
- **它真的懂菜单** —— 热量和营养来自官方接口，一个数字都不会编
- **它真的能帮你省钱** —— 活动与优惠券是实时可领的
- **它真的能帮你下单** —— 陪伴的终点是一份真的取得到餐的订单

## 配置说明

所有配置走 `.env`，**公开仓库里只提交 `.env.example`（纯占位符）**，真实 Token 与手机号不会入库。详见 [`.env.example`](.env.example) 与 [`mcp-config.example.json`](mcp-config.example.json)。

| 变量 | 必需 | 说明 |
| --- | --- | --- |
| `MCP_TOKEN` | ✅ | 麦当劳 MCP Token |
| `MCP_SERVER_URL` | | 默认 `https://mcp.mcd.cn` |
| `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` | ✅ | 支持 tool calling 的大模型 |
| `TEST_PHONE` | ✅ | 麦当劳账号手机号 |
| `DEFAULT_STORE_ID` | ✅ | 常用门店编码 |
| `PORTRAIT_MODE` | | `gentle`（默认）/ `sarcastic` |

> MCP 限流 600 次/分钟/Token，静态数据（菜单、营养、活动）本地缓存 30 分钟。

## 目录结构

```
mcdinner-mate/
├── README.md                  # 本文件
├── CONTEST_DECLARATION.md     # 参赛声明（官方文件，内容不可改动）
├── MCP_INTEGRATION.md         # MCP 接入说明
├── mcp-config.example.json    # 脱敏配置示例
├── workbuddy.md               # WorkBuddy 开发上下文
├── server/                    # 后端：MCP 客户端 / 对话引擎 / 语音 / 报告
├── web/                       # 单页前端
├── scripts/                   # MCP 探测与冒烟测试
├── assets/                    # 头图与吉祥物
└── docs/                      # 真实工具清单与接口样例
```

## 参与赛事

本项目参加 **2026 麦当劳程序员创意开发大赛**（2026-10-09 ~ 10-25）。
参赛声明见 [`CONTEST_DECLARATION.md`](CONTEST_DECLARATION.md)。

> 本项目为参赛作品，由开发者独立开发，**非麦当劳官方产品**。
> 项目输出仅供参考，不构成医疗、营养或其他专业建议；
> 餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。
