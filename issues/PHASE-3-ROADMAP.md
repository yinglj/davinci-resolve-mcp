# Phase 3 开发路线图：MCP Tools 扩展与 Agent 集成

**版本**: 1.0  
**时间范围**: 2026年2月-3月 (6-8周)  
**状态**: Planning

---

## 概览

Phase 3 的核心目标是将 Phase 1/2 中实现的高级功能（Fusion 动态合成、自动调色、Fairlight 音频处理等）**暴露为 MCP Tools**，并将其与 `davinci_resolve_agent` 子项目中的多角色 Agent 系统深度整合，形成一个端到端的 AI 视频编辑工作流。

### Phase 3 的核心价值

1. **MCP Tools 扩展**: 将内部 skill 函数注册为标准 MCP tools，供外部 AI 客户端调用
2. **Agent 能力升级**: 让 Director/Editor/Colorist/Sound Engineer 角色能直接调用新工具
3. **工作流自动化**: 支持复杂的多步骤视频编辑任务自动执行
4. **统一入口**: 通过 `client_simulator.py` 或外部 MCP 客户端访问所有功能

---

## 现有架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    davinci_resolve_agent                        │
│  ┌─────────────────┐      ┌─────────────────────────────────┐   │
│  │ client_simulator│─────▶│    agnomcp_server.py            │   │
│  │   (JSON-RPC)    │      │  ┌─────────────────────────┐    │   │
│  └─────────────────┘      │  │ QueryProcessor          │    │   │
│                           │  │  └─> Agno Agent         │    │   │
│                           │  │      (Director/Editor/  │    │   │
│                           │  │       Colorist/Sound)   │    │   │
│                           │  └─────────────────────────┘    │   │
│                           └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼ MultiMCPTools
┌─────────────────────────────────────────────────────────────────┐
│                src/resolve_mcp_server.py                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐ │
│  │ 169+ MCP Tools │  │ Tool Proxy     │  │ Resolve Connection │ │
│  │ (existing)     │  │ (@proxy_tool)  │  │                    │ │
│  └────────────────┘  └────────────────┘  └────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                     ▲
                                     │ Not Yet Exposed
┌─────────────────────────────────────────────────────────────────┐
│             src/agent/executor/skills/ (To be integrated)       │
│  ┌──────────────────────┐  ┌────────────────────────────────┐   │
│  │ fusion_executor.py   │  │ resolve_color_and_audio.py     │   │
│  │ - create_effect_chain│  │ - create_color_grade_from_style│   │
│  │ - add_transition     │  │ - normalize_audio_loudness     │   │
│  │ - create_nested_comp │  │ - generate_tts_voiceover       │   │
│  └──────────────────────┘  └────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ resolve_advanced_integration.py                          │   │
│  │ - create_fairlight_audio_chain                           │   │
│  │ - apply_color_grade_with_automation                      │   │
│  │ - monitor_audio_levels                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 3 详细计划

### 🔧 P3-01: 高级功能 MCP Tools 化 (5-7天)

**状态**: ✅ Completed (2026-01-20)

**目标**:
将 `src/agent/executor/skills/` 下的核心功能注册为 MCP tools，使其可被外部 AI 客户端和 Agent 调用。

**关键工作项**:

#### 1. Fusion 效果工具 (2天)

| 函数 | 新 MCP Tool 名称 | 描述 |
|------|------------------|------|
| `create_effect_chain` | `fusion_create_effect_chain` | 创建 Fusion 效果链 |
| `add_transition` | `fusion_add_transition` | 在图层间添加转场 |
| `create_nested_composition` | `fusion_create_nested_comp` | 创建嵌套合成 |
| `get_fusion_composition_status` | `fusion_get_status` | 获取当前合成状态 |

#### 2. 自动调色工具 (1.5天)

| 函数 | 新 MCP Tool 名称 | 描述 |
|------|------------------|------|
| `create_color_grade_from_style` | `color_apply_style` | 应用预设风格调色 |
| `apply_auto_color_to_shots` | `color_auto_grade_shots` | 自动为多镜头调色 |
| `apply_color_grade_with_automation` | `color_grade_with_keyframes` | 带关键帧的调色 |

#### 3. 音频处理工具 (1.5天)

| 函数 | 新 MCP Tool 名称 | 描述 |
|------|------------------|------|
| `normalize_audio_loudness` | `audio_normalize_loudness` | 音频响度标准化 |
| `generate_tts_voiceover` | `audio_generate_tts` | 生成 TTS 配音 |
| `create_fairlight_audio_chain` | `audio_create_fairlight_chain` | 创建 Fairlight 音频链 |
| `monitor_audio_levels` | `audio_monitor_levels` | 监控音频电平 |

#### 4. 实现方式

在 `src/resolve_mcp_server.py` 的 `register_mcp_resources()` 函数中添加新的 tool 注册：

```python
# 示例：注册 fusion_create_effect_chain
@mcp.tool()
async def fusion_create_effect_chain(
    effect_list: List[Dict[str, Any]],
    layer_name: str = 'effect_chain_layer'
) -> Dict[str, Any]:
    """Create a chain of Fusion effects on a composition layer."""
    from src.agent.executor.skills.fusion_executor import create_effect_chain
    return create_effect_chain(effect_list, layer_name, resolve)
```

**预期交付物**:

- ✅ 10+ 新 MCP tools
- ✅ 更新的 `resolve_mcp_server.py`
- ✅ 单元测试覆盖
- ✅ API 文档

**成功标准**:

- 所有新 tools 可通过 `list_tools` 发现
- 端到端调用验证通过
- 与现有 tools 无冲突

---

### 🤖 P3-02: Agent 多角色能力强化 (4-5天)

**状态**: Not Started

**目标**:
更新 `davinci_resolve_agent/prompts/system_prompts.py` 和 `mcp_agents.py`，使各角色 Agent 能更准确地识别和使用新工具。

**关键工作项**:

#### 1. 更新 System Prompts (2天)

- **Colorist** (`COLORIST_PROMPT`): 添加对 `color_apply_style`、`color_auto_grade_shots` 的引用
- **Sound Engineer** (`SOUND_ENGINEER_PROMPT`): 添加对 `audio_create_fairlight_chain`、`audio_normalize_loudness`、`audio_generate_tts` 的引用
- **Editor** (`EDITOR_PROMPT`): 添加对 `fusion_create_effect_chain`、`fusion_add_transition` 的引用
- **Director** (`DIRECTOR_PROMPT`): 更新委派逻辑，明确新功能的分工

#### 2. 增强工具发现机制 (1.5天)

- 在 `QueryProcessor` 中添加工具分类和推荐逻辑
- 实现基于用户意图的工具自动选择

#### 3. 添加工作流知识 (1.5天)

- 更新 `davinci_resolve_agent/knowledge/workflows.md`
- 添加常见任务的工具组合示例

**预期交付物**:

- ✅ 更新的 4 个角色 prompts
- ✅ 工具推荐逻辑
- ✅ 扩展的 knowledge base

---

### 🔄 P3-03: 多 Agent 协作与任务编排 (5-6天)

**状态**: Backlog

**目标**:
实现 Director Agent 对其他角色的有效委派，支持复杂的多步骤任务自动执行。

**关键工作项**:

#### 1. Agent 委派框架 (2天)

- 实现 Agent-to-Agent 通信机制
- 支持子任务分发和结果汇总

#### 2. 任务执行器增强 (2天)

- 整合 `src/agent/executor/task_executor.py`
- 添加对新 StepType 的支持：
  - `FUSION_COMPOSITION`
  - `COLOR_AUTOMATION`
  - `AUDIO_PROCESSING`
  - `TTS_GENERATION`

#### 3. 工作流模板 (2天)

- 预定义常见工作流（如"快速剪辑+调色+配乐"）
- 支持用户自定义工作流

---

### 📡 P3-04: 客户端增强与 API 扩展 (3-4天)

**状态**: Backlog

**目标**:
增强 `client_simulator.py` 的交互能力，并提供更丰富的 API 接口。

**关键工作项**:

#### 1. 客户端命令扩展 (1.5天)

- 添加快捷命令：`/fusion`、`/color`、`/audio`
- 支持预设工作流一键触发

#### 2. 状态监控与反馈 (1.5天)

- 实时显示任务执行进度
- 添加执行历史查询

#### 3. REST API 暴露 (可选) (1天)

- 将核心功能通过 HTTP API 暴露
- 支持外部应用集成

---

## 关键依赖关系

```
P2-01 ✅ (TaskPlanner/Executor 集成)
   ↓
P2-02 ✅ (真实 Resolve 测试)
   ↓
P2-03 ✅ (PR 合并)
   ↓
P3-01 (MCP Tools 化) → P3-02 (Agent 能力强化)
         ↓                    ↓
         └───────┬────────────┘
                 ↓
         P3-03 (多 Agent 协作)
                 ↓
         P3-04 (客户端增强)
```

---

## 时间表和里程碑

### Week 1-2 (2月中旬)

- **P3-01 执行**: MCP tools 注册和测试
- 目标: 完成所有 Fusion/Color/Audio tools 注册

### Week 3 (2月下旬)

- **P3-02 执行**: Agent prompts 和 knowledge 更新
- 目标: 各角色 Agent 能正确识别和使用新工具

### Week 4-5 (3月上旬)

- **P3-03 执行**: 多 Agent 协作框架
- 目标: Director 能有效委派任务给其他 Agent

### Week 6 (3月中旬)

- **P3-04 执行**: 客户端优化
- 目标: 完整的端到端用户体验

---

## 风险管理

### 高风险项

1. **MCP Tool 参数复杂度**
   - 缓解: 提供合理的默认值和参数验证
   - 备用: 简化部分 tool 的参数接口

2. **Agent 工具选择准确性**
   - 缓解: 在 prompt 中提供清晰的工具使用示例
   - 备用: 添加显式工具推荐机制

### 中风险项

1. **多 Agent 通信延迟**
   - 缓解: 优化消息传递机制
   - 备用: 在 Director 层面批量处理

---

## 成功度量指标 (KPI)

### 功能性

- [x] 新增 MCP tools ≥ 10 个 (11个已添加)
- [ ] 所有 tools 可被 Agent 正确调用
- [ ] 端到端工作流测试通过率 ≥ 95%

### 用户体验

- [ ] 常见任务可通过自然语言完成
- [ ] 任务执行反馈清晰
- [ ] 错误处理友好

---

## 下一步行动

### 立即 (本周)

1. [ ] 审查 P3-01 技术设计
2. [ ] 确认 MCP tool 命名规范
3. [ ] 准备开发环境

### 短期 (2-3 周)

1. [x] P3-01 MCP tools 实现 ✅
2. [ ] 单元测试编写
3. [ ] 初步集成测试

---

**文档版本**: 1.0  
**创建日期**: 2026年1月20日  
**维护者**: Development Team  
**相关 Issue**: #P3-01, #P3-02, #P3-03, #P3-04
