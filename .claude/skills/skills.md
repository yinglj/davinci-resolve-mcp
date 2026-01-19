# DaVinci Resolve Agent — Skills (初始)

## 一句话概览 ✅
构建一个基于 DaVinci Resolve 的智能视频生成 Agent：利用已有的 MCP/Agent 框架和 Resolve API，把“自然语言 -> 计划 -> 自动编辑/合成 -> 渲染”变为可执行的技能集合。

---

## 快速扫描发现 🔎
- 现有 Agent 框架：`src/agent`（核心 `ResolveAgent`、`planner`、`executor`、`memory`、`feedback` 等）。
- Resolve API 封装：`src/api/*`（`project_operations.py`、`fusion_operations.py`、`app_operations.py` 等）。
- 工具与实用模块：`src/utils/*`（`resolve_connection.py`、`object_inspection.py`、`screenshot.py`、`layout_presets.py`）。
- RAG 文档支持：`src/agent/rag/resolve_doc_rag.py`，已有 Resolve 文档索引与检索逻辑。
- 多 MCP/Agent 入口：`davinci_resolve_agent/mcp_agents.py`，支持 MultiMCPTools 与 agent orchestration。
- 示例/测试：`examples/` 与 `tests/` 包含若干用例与测试脚本。

---

## 已有（可立即复用）的技能（Skills）🔧
每一项都可以作为 Agent 的 skill：

- **Resolve 连接与状态管理** — `src/utils/resolve_connection.py`（连通性检查、连接日志）。
- **应用控制** — `src/api/app_operations.py`, `src/utils/app_control.py`（启动、重启、退出、窗口控制）。
- **项目与时间线操作** — `src/api/project_operations.py`（创建/打开项目、时间线操作基础）。
- **Fusion 脚本调用** — `src/api/fusion_operations.py`（Fusion 相关的操作封装）。
- **对象检查与文档化** — `src/utils/object_inspection.py`（自动发现 API 方法/属性并生成帮助）。
- **屏幕截图 / 预览** — `src/utils/screenshot.py`（Mac 专用实现）。
- **Planner / Executor** — `src/agent/planner/*`, `src/agent/executor/*`（把“计划”转换为 Resolve API 调用）。
- **RAG（知识检索）** — `src/agent/rag/resolve_doc_rag.py`（针对 Resolve 文档的检索，支持解释和错误对策）。
- **记忆管理** — `src/agent/memory/memory_manager.py`（短期/长期记忆，保存偏好/历史）。
- **多 MCP agent 支持** — `davinci_resolve_agent/mcp_agents.py`（把 Agent 在服务端启动/运行）。

---

## 需要新增 / 强化的技能（优先级 & 描述）⚡
下面按优先级给出技能建议，以便快速实现“文本描述 -> 成片”的流水线。

短期（P0，优先）
- **脚本/分镜解析 Skill**：把用户的自然语言脚本（故事板）解析成 shot-level plan（镜头、时长、转场、素材需求）。
  - 入口：LLM -> Planner -> 生成 Plan JSON。
- **占位时间线创建 Skill**：基于 plan 在 Resolve 中创建 timeline，插入占位片段（或占位空白轨道）以便后续填充。
- **素材导入 & 管理 Skill**：从本地/云导入素材并管理 metadata（tags、时间码、来源）。
- **自动渲染/导出 Skill**：根据模板/分辨率/编码参数触发渲染并返回状态/输出路径。

中期（P1）
- **自动剪辑 & 节奏匹配 Skill**：根据脚本节奏与音乐自动选择剪切点与镜头时长。
- **Fusion 动态合成 Skill**：封装 Fusion 脚本（templates）以支持动态图形、标题与转场自动生成。
- **自动调色 Skill**：基于风格示例应用 LUT/分级并支持自动匹配（风格迁移）。
- **音频处理 Skill**：集成 TTS、配音合成、自动降噪与母带处理。

长期（P2）
- **Text→Visual（生成素材）集成**：对接外部生成模型（图像/视频/帧插补/扩展）并把结果自动导入 Resolve。注意版权与合规风险。 
- **闭环交互 & 学习 Skill**：用户评价 -> 更新记忆/偏好 -> 风格自适应。
- **视觉质量自动检测 Skill**：检测模糊、曝光、构图等自动 QA，并自动提出修复计划。

---

## 技术能力与工程化要求 🔧
- **可靠的工具封装**：为每个 skill 提供幂等、可测的 API 层与错误恢复策略。
- **模拟器 / Mock**：提供 Resolve API 的测试模拟器，方便 CI 中跑 unit/integration tests。
- **流式进度与反馈**：Agent 能通过 streaming（RunOutput）向前端回传步骤进度与中间预览（缩略图/时间线快照）。
- **RAG 扩展**：将用户的风格样例、示例项目索引入向量库，以便快速检索匹配风格。
- **权限与隐私**：处理素材时做好授权、隐私检测与合规检查。
- **性能监控**：记录渲染/生成任务的耗时、失败率与资源占用。

---

## Skill Entry 模板（建议格式）📋
- **名称**：
- **描述**：
- **输入**：（自然语言、JSON schema）
- **输出**：（结果/文件/状态）
- **入口文件 / 模块**：（例如 `src/agent/executor/task_executor.py` 或 新建模块）
- **优先级**：P0/P1/P2
- **测试**：需要哪些单元/集成测试

### 示例（脚本解析 Skill）
- 名称：ScriptToShots
- 描述：将自然语言脚本拆解为 shot list（每个 shot 含时长、动作、素材类型）。
- 输入：脚本文本
- 输出：JSON（shot list）
- 入口：`src/agent/planner/task_planner.py`（新增解析器）
- 优先级：P0
- 测试：文本脚本到 shot JSON 的转换测试，用 edge cases（长脚本、模糊指令）。

---

## 初始 Roadmap（任务清单 / Issue 建议）🛠️
1. Create: `.claude/skills/skills.md`（已完成） ✅
2. 创建 P0 技能：`ScriptToShots`、`CreatePlaceholderTimeline`、`ImportAndTagAssets`、`RenderPresetRunner`（各写单元测试）。
3. 为 `task_executor` 写模拟 Resolve 的测试 Mocks 并在 CI 中使用。
4. 补充 RAG 索引：把用户示例项目与偏好文件加入向量库，便于风格检索。 
5. 集成小型示例：`examples/generate_short_from_script.py`（演示从脚本到时间线的 POC）。

---

## 风险与注意事项 ⚠️
- 真实 DaVinci Resolve API 在不同版本上可能行为不一致，必须做版本检测与兼容处理（`src/utils/platform.py` / `resolve_connection.py`）。
- 外部生成模型涉及版权与隐私（需要审核流程）。
- 渲染是耗时与高资源操作，请做好异步队列与超时/恢复策略。

---

## 下一步建议（我可以帮你做的事）➡️
1. 我可以为 P0 技能生成具体的 issue / TODO 列表并在仓库中添加示例代码和测试。 
2. 我可以先实现 `ScriptToShots` 的 POC（planner + 单元测试），并提交 PR。 

---

> 如果你同意，我会先实现 **ScriptToShots POC**：实现解析器、样例测试与一个 `examples/` 演示脚本，然后把任务划分成 3 个小 PR（解析器、executor hook、示例）。

---

_文件由自动化扫描生成，基于 repo 当前代码与结构（2026-01-19）。如果你希望我把某些技能改为更高优先级或按你的产品目标调整路线，请告诉我具体目标（例如“短视频社媒”、“企业宣传片”或“自动扫描素材转片头”）。_