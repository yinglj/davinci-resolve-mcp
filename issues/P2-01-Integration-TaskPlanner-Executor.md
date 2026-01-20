# P2-01: Integration with TaskPlanner/Executor Pipeline

## 概要
将P1-02(Fusion Dynamic Composition)和P1-03(AutoColor & Audio Enhancement)集成到主TaskPlanner和TaskExecutor流程中，实现端到端的自动化视频编辑能力。

## 目标
- ✅ 注册fusion_composition为TaskPlanner的规划技能
- ✅ 注册fusion_executor为TaskExecutor的执行技能
- ✅ 为resolve_advanced_integration添加TaskPlanner集成
- ✅ 完善resolve_advanced_integration的TaskExecutor集成
- ✅ 添加完整的端到端集成测试
- ✅ 支持StepType.FUSION_COMPOSITION和StepType.COLOR_AUTOMATION新步骤类型

## 技术细节

### 1. TaskPlanner集成 (src/agent/planner/task_planner.py)
```python
# 新增方法
async def _plan_fusion_composition(self, plan: Plan, entities: Dict):
    """计划Fusion动态合成任务"""
    step = PlanStep(
        step_type=StepType.FUSION_COMPOSITION,
        action="plan_fusion_composition",
        parameters={
            "script_summary": entities.get("script_summary"),
            "shot_list": entities.get("shot_list"),
            "style": entities.get("style", "modern"),
            "effect_intensity": entities.get("effect_intensity", 0.7),
            "enable_3d": entities.get("enable_3d", False)
        }
    )
    plan.add_step(step)

async def _plan_color_automation(self, plan: Plan, entities: Dict):
    """计划高级调色自动化任务"""
    step = PlanStep(
        step_type=StepType.COLOR_AUTOMATION,
        action="apply_color_grade_with_automation",
        parameters={
            "shots": entities.get("shots"),
            "style": entities.get("style", "cinematic"),
            "auto_keyframes": entities.get("auto_keyframes", True),
            "enable_temporal_smoothing": entities.get("enable_temporal_smoothing", True)
        }
    )
    plan.add_step(step)

async def _plan_fairlight_audio(self, plan: Plan, entities: Dict):
    """计划Fairlight音频链处理"""
    step = PlanStep(
        step_type=StepType.AUDIO_PROCESSING,
        action="create_fairlight_audio_chain",
        parameters={
            "target_loudness": entities.get("target_loudness", -23.0),
            "compression_ratio": entities.get("compression_ratio", 4.0),
            "gate_threshold": entities.get("gate_threshold", -40.0),
            "eq_profile": entities.get("eq_profile", "neutral")
        }
    )
    plan.add_step(step)
```

### 2. TaskExecutor集成 (src/agent/executor/task_executor.py)
```python
# 新增导入和处理
from .skills.fusion_executor import create_fusion_page, create_effect_chain, create_nested_composition
from .skills.resolve_advanced_integration import (
    create_fairlight_audio_chain,
    apply_color_grade_with_automation,
    monitor_audio_levels,
    export_color_metadata
)

# 在_execute_step中新增分支
elif step.step_type == StepType.FUSION_COMPOSITION:
    return await self._execute_fusion_composition(step)
elif step.step_type == StepType.COLOR_AUTOMATION:
    return await self._execute_color_automation(step)
elif step.step_type == StepType.AUDIO_PROCESSING:
    return await self._execute_audio_processing(step)
```

### 3. 新增StepType枚举值 (src/agent/planner/plan.py)
```python
class StepType(Enum):
    RESOLVE_API = "resolve_api"
    VIDEO_ANALYSIS = "video_analysis"
    DOCUMENTATION = "documentation"
    VALIDATION = "validation"
    COMPOSITE = "composite"
    FUSION_COMPOSITION = "fusion_composition"  # 新增
    COLOR_AUTOMATION = "color_automation"      # 新增
    AUDIO_PROCESSING = "audio_processing"      # 新增
```

## 集成清单

### Phase 1: 核心集成
- [ ] 更新plan.py添加新StepType
- [ ] 添加intent识别模式（fusion_composition, color_automation, fairlight_audio）
- [ ] 实现TaskPlanner的3个新规划方法
- [ ] 实现TaskExecutor的3个新执行方法
- [ ] 添加参数验证和依赖检查

### Phase 2: 完整流程测试
- [ ] 创建集成测试: tests/test_integration_p1_02_p1_03.py
- [ ] 测试Fusion composition完整流程
- [ ] 测试Color automation完整流程
- [ ] 测试Fairlight audio完整流程
- [ ] 测试多步骤链式执行
- [ ] 测试错误恢复和重试机制

### Phase 3: 优化和文档
- [ ] 添加请求意图识别规则
- [ ] 编写集成文档 (docs/P2-01-INTEGRATION.md)
- [ ] 添加使用示例
- [ ] 性能基准测试
- [ ] 端到端场景测试

## 技术需求

### 依赖关系
- P1-02需求: src/agent/planner/skills/fusion_composition.py ✅
- P1-02需求: src/agent/executor/skills/fusion_executor.py ✅
- P1-03需求: src/agent/executor/skills/resolve_advanced_integration.py ✅
- 依赖已完成

### 关键接口
1. **TaskPlanner.create_plan()** - 需要支持新的intent类型
2. **TaskExecutor.execute_plan()** - 需要支持新的StepType处理
3. **Plan.add_step()** - 支持依赖关系定义
4. **PlanStep.dependencies** - 定义步骤间依赖

## 集成场景

### 场景1: 完整的Fusion+ColorGrading+Audio工作流
```
用户请求: "为我的视频添加Fusion效果、调色并处理音频"

生成的计划:
1. [VALIDATION] 验证时间线和媒体
2. [FUSION_COMPOSITION] 规划Fusion合成(style=cinematic)
3. [FUSION_COMPOSITION] 创建Fusion页面并执行合成
4. [COLOR_AUTOMATION] 应用调色自动化
5. [AUDIO_PROCESSING] 创建Fairlight链和音频处理
6. [DOCUMENTATION] 导出处理结果和元数据
```

### 场景2: 仅Fusion效果
```
用户请求: "为这个片段添加动态图形效果"

生成的计划:
1. [VALIDATION] 验证片段
2. [FUSION_COMPOSITION] 规划Fusion合成
3. [FUSION_COMPOSITION] 执行合成
```

### 场景3: 音频处理链
```
用户请求: "标准化音频并应用音频链"

生成的计划:
1. [VIDEO_ANALYSIS] 分析音频特性
2. [AUDIO_PROCESSING] 创建Fairlight链
3. [AUDIO_PROCESSING] 监控和验证
```

## 估时
- Phase 1(核心集成): 2-3 天
- Phase 2(完整测试): 1-2 天
- Phase 3(优化文档): 1 天
- **总计: 4-6 天**

## 成功标准
- ✅ 所有新intent识别正确工作
- ✅ TaskPlanner能生成包含新步骤的完整计划
- ✅ TaskExecutor能正确执行所有新步骤
- ✅ 集成测试100%通过
- ✅ 支持参数传递和依赖解析
- ✅ 错误恢复机制工作正常
- ✅ 完整的端到端场景测试通过

## 相关文件
- src/agent/planner/task_planner.py (需更新)
- src/agent/executor/task_executor.py (需更新)
- src/agent/planner/plan.py (需更新)
- src/agent/planner/skills/fusion_composition.py ✅
- src/agent/executor/skills/fusion_executor.py ✅
- src/agent/executor/skills/resolve_advanced_integration.py ✅
- tests/test_integration_p1_02_p1_03.py (新建)

## 风险项
- 参数传递和类型验证需要严格处理
- Resolve API可用性需要graceful fallback
- 异步执行中的并发问题
- 大型时间线的性能

## 依赖项
- P1-02: Fusion Dynamic Composition ✅ (已完成)
- P1-03: AutoColor & Audio Enhancement ✅ (已完成)
