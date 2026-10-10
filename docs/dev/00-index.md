# 开发文档索引

> 本目录是 `McDinnerMate` 的**开发过程文档**，按主题切分，便于长期维护与分工修改。
> 原 `McDinnerMate_实施文档.md` 保留在项目根目录作为初版快照，**后续不再更新，一切以本目录为准**。

## 文档地图

| 文件 | 主题 | 何时读 | 维护频率 |
| --- | --- | --- | --- |
| [01-product.md](./01-product.md) | 项目定位、目标用户、核心玩法、功能范围与边界 | 开工前、范围争议时 | 低 |
| [02-env-config.md](./02-env-config.md) | 环境变量、凭证清单、本机环境约束 | 环境搭建时 | 中 |
| [03-tech-stack.md](./03-tech-stack.md) | 技术选型与决策记录 | 选型/换技术时 | 中 |
| [04-architecture.md](./04-architecture.md) | 系统架构、数据流、目录结构 | 写代码前 | 中 |
| [05-mcp-mapping.md](./05-mcp-mapping.md) | ⭐ MCP 真实工具清单与意图映射 | Phase 1 后每日参照 | **高** |
| [06-dialog-design.md](./06-dialog-design.md) | 对话状态机、人设、意图路由 | 写对话引擎时 | 高 |
| [07-roadmap.md](./07-roadmap.md) | 阶段拆解、排期、降级预案 | 每日站会 | **高** |
| [08-test-cases.md](./08-test-cases.md) | 验收测试用例清单 | 自测与 Demo 前 | 中 |
| [09-submission.md](./09-submission.md) | ⭐ 赛事交付物（官方合规要求） | 提交前逐项核对 | 中 |
| [10-risks.md](./10-risks.md) | 风险登记册 | 每周复盘 | 中 |
| [11-promotion.md](./11-promotion.md) | ⭐ Star 传播策略（决定名次） | 每周 | **高** |

## 相关文档（本目录之外）

| 文件 | 主题 |
| --- | --- |
| [`../design/BANNER.md`](../design/BANNER.md) | 🔒 Banner 与吉祥物设计规范（**已冻结**，设计资产，非参赛交付物） |
| [`../../FEASIBILITY.md`](../../FEASIBILITY.md) | 项目可行性评估 |

## 关键结论速查

- **名次由 GitHub Star 数决定**（前 100 名获奖）→ 见 [11-promotion.md](./11-promotion.md)
- **参赛文件名不可自定义** → 见 [09-submission.md](./09-submission.md)
- **MCP 工具名以 `list_tools()` 实测为准**，文档中的中文名仅为意图描述 → 见 [05-mcp-mapping.md](./05-mcp-mapping.md)
- **ASR 不建议用浏览器 Web Speech API**（国内不可用）→ 见 [03-tech-stack.md](./03-tech-stack.md)
- **Banner/吉祥物设计已冻结**，改动前先看 [`../design/BANNER.md`](../design/BANNER.md)

## 文档约定

- 占位符统一 `{{XXX}}` 格式，⭐ 标记必填项
- 严重度标记：🔴 致命 / 🟠 高 / 🟡 中 / ⚪ 低
- 所有"以实测为准"的结论，必须在本目录中回写，**不要只留在聊天记录里**
