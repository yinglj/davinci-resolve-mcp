# P3-05: MCP Tools 生产化与异步任务系统

**版本**: 1.0  
**创建日期**: 2026-01-20  
**状态**: Planning  
**优先级**: High

---

## 目标概述 💡

将已实现的高级功能（Fusion 动态合成、AutoColor & Audio、TaskPlanner/Executor）以**可复用的 MCP Tools** 形式暴露，支持：

- 远程调用
- 异步执行 (Job Queue)
- 完整测试覆盖
- 生产环境就绪

---

## 范围

### 包含 ✅

- MCP Tools 设计与实现
- Server 路由/处理
- Client 调用接口
- 单元/集成/E2E 测试
- 文档
- CI 集成

### 不包含 ❌

- 大规模性能优化（后续迭代）
- Resolve API 底层改动（继续使用现有 wrapper/POC）

---

## 设计要点 🔧

### Tools 特性

- **原子/组合型操作**（如 `create_fusion_composition`, `auto_color_timeline`）
- 每个 tool 支持：
  - **同步 POC 响应**（Resolve 不连时返回模拟结果）
  - **异步执行**（返回 `job_id`，可 poll 或事件推送）
  - **明确 JSON Schema**（输入/输出）

### 安全性

- 复用现有 `agnomcp_server._validate_api_key`
- 日志不包含敏感 key

### 可观测性

- 每个 tool 记录日志
- 返回 `trace_id`
- CI/CD 测试覆盖可采集

### 可扩展性

- Tools 注册表/工厂模式
- 便于后续增加新 tool

---

## 建议的 MCP Tools 🛠️

### Fusion 相关

#### `tools.create_fusion_composition`

```
params: {
  script_summary: str,
  shot_list: [{start, end, desc}],
  style?: str,
  effect_intensity?: float,
  enable_3d?: bool
}
returns: { success: bool, job_id?: str, composition_spec?: {...}, note?: str }
```

#### `tools.apply_fusion_to_timeline`

```
params: { composition_spec, timeline_id?, frame_range? }
returns: { success, job_id, applied_to_timeline: bool }
```

### Audio 相关

#### `tools.create_audio_chain`

```
params: { target_loudness?, compression_ratio?, eq_profile? }
returns: { success, chain_id, processors: [...] }
```

### Color 相关

#### `tools.auto_color_timeline`

```
params: { timeline_id?, keyframe_strategy?, smoothing_type? }
returns: { success, job_id, summary }
```

### Render 相关

#### `tools.render_preview`

```
params: { timeline_id, start_frame, end_frame, preset? }
returns: { success, job_id, preview_url? }
```

### Job 生命周期

#### `tools.job_status`

```
params: { job_id }
returns: { status: queued|running|done|failed, progress, result }
```

#### `tools.cancel_job`

```
params: { job_id }
returns: { success, status }
```

---

## Server-side 变更 🔁

### 任务清单

1. **新建模块** `src/api/tools_operations.py`
   - 实现 methods 入参校验
   - POC 逻辑与 executor/planner 桥接

2. **注册路由**
   - 在 `resolve_mcp_server.py` 中注册到 FastMCP
   - 保持与现有 `src/api/*.py` 风格一致

3. **Job Queue**
   - 简单内存队列 + asyncio tasks
   - 后续可 swap 为 Redis/RQ/Kubernetes jobs

4. **日志 & Metric**
   - 为 jobs 添加 `trace_id`
   - 记录到现有 logger

5. **权限验证**
   - 复用 `_validate_api_key`

**估时**: 2-3 天

---

## Client-side 变更 📡

### client_simulator.py

- 增加交互命令：`fusion create`, `audio chain create`, `tools status <jobid>`
- 支持同步/异步模式
- 支持轮询或订阅进度

### agnomcp_server.py

- 添加代理/转发到 tools 的逻辑
- 示例调用脚本 (`examples/demo_tools_usage.py`)

**估时**: 1-2 天

---

## 测试计划 ✅

| 类型 | 内容 |
|------|------|
| **单元测试** | pytest: 每个 tool 的 input/output、POC path、错误 path |
| **集成测试** | mock Resolve: 验证 executor 调用、job lifecycle |
| **E2E 测试** | client_simulator → agnomcp_server → tools → job 完成 |
| **CI** | 在 `p2-03-ci-cd.yml` 新增 job (with/without Resolve stub) |

**估时**: 1-2 天

---

## 文档 📚

- 每个 tool 的 API 文档（method、params、responses、errors）
- 用例示例（client_simulator 命令）
- 更新 `RELEASE-GUIDE-v1.4.0.md`
- 更新 `RELEASE_NOTES`

**估时**: 0.5-1 天

---

## 验收标准 ✅

- [ ] 所有 tools 可通过 client_simulator 调用并返回期望格式
- [ ] 至少 5 个单元 + 3 个集成测试通过
- [ ] CI 在 PR 中自动运行并通过
- [ ] 文档覆盖每个 tool 的 API 和示例
- [ ] API key 验证生效，POC fallback 正确工作

---

## 风险 & 缓解 ⚠️

| 风险 | 缓解策略 |
|------|---------|
| Resolve 连接不可用 | POC fallback + 充分模拟测试 |
| 作业积压/并发 | 初期内存队列；高并发时迁移外部作业系统 |
| API key 泄露 | 日志不含敏感 key + 短期临时 key 机制 |

---

## 里程碑与时间表 ⏱️

| Day | 任务 |
|-----|------|
| 0 | 确定优先 tool 列表，定义 JSON schemas |
| 1-2 | 实现 `tools_operations.py` 基础方法 + 单元测试 |
| 3 | 实现 job queue + `job_status` + `cancel_job` + 集成测试 |
| 4 | client_simulator 新命令 + 示例脚本 + E2E 测试 |
| 5 | 文档 + CI 更新 + PR 提交 + Code Review |
| 6-7 | 修复反馈 + 合并 + 发布 (tag v1.4.0) |

---

## 下一步行动 ▶️

### 选项 A（推荐）

先实现 `create_fusion_composition` + 单元测试 + client command 示例

### 选项 B

先写完整 tools list + JSON Schemas + docs（确定接口契约）

**建议优先级**: Fusion → Audio → Job lifecycle

---

## 与现有 P3 计划的关系

此计划扩展了 P3-01 已完成的工作：

- **P3-01** ✅: 11 个基础 MCP tools (同步调用)
- **P3-05** 🆕: 生产化增强 (异步、Job Queue、完整测试)

---

**相关 Issue**: #P3-01, #P3-02, #P3-03, #P3-04
