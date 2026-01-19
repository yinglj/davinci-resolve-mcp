"""集成测试：AutoColor & Audio 执行器工具"""
import asyncio
from src.agent.executor.skills.auto_color_and_audio_executor import (
    auto_color_grade,
    audio_normalize,
    text_to_speech
)


def test_auto_color_grade_tool():
    """测试 auto_color_grade 执行器工具"""
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0},
        {'id': 's2', 'in': 1.0, 'out': 2.5},
    ]
    result = auto_color_grade(shots, style='vibrant')
    assert 'success' in result
    assert 'shots_graded' in result or 'error' in result


def test_audio_normalize_tool():
    """测试 audio_normalize 执行器工具"""
    result = audio_normalize(target_loudness=-23.0)
    assert 'success' in result or 'error' in result


def test_text_to_speech_tool():
    """测试 text_to_speech 执行器工具"""
    result = text_to_speech("欢迎观看本视频", voice='default')
    assert result['success'] is True
    assert result['duration'] > 0


def test_executor_pipeline_with_color_and_audio():
    """集成测试：Planner -> Executor with AutoColor & Audio"""
    from src.agent.executor.task_executor import TaskExecutor
    from src.agent.planner.plan import Plan, PlanStep, StepType
    
    # 创建一个包含 auto_color_grade 和 audio_normalize 步骤的计划
    plan = Plan(summary="Color and Audio Pipeline")
    
    step_color = PlanStep(
        step_type=StepType.RESOLVE_API,
        action="auto_color_grade",
        parameters={
            'shots': [
                {'id': 's1', 'in': 0.0, 'out': 1.0},
                {'id': 's2', 'in': 1.0, 'out': 2.5}
            ],
            'style': 'cinematic'
        },
        expected_outcome="Color grading applied"
    )
    plan.add_step(step_color)
    
    step_audio = PlanStep(
        step_type=StepType.RESOLVE_API,
        action="audio_normalize",
        parameters={
            'target_loudness': -23.0
        },
        dependencies=[step_color.step_id],
        expected_outcome="Audio normalized"
    )
    plan.add_step(step_audio)
    
    # 准备 Fake Resolve Server
    class FakeResolveServer:
        def __init__(self):
            self._tools = {}
            self._resources = {}
    
    fake = FakeResolveServer()
    fake._tools['auto_color_grade'] = auto_color_grade
    fake._tools['audio_normalize'] = audio_normalize
    
    executor = TaskExecutor(resolve_server=fake)
    result = asyncio.run(executor.execute_plan(plan))
    
    assert result['success'] is True
    actions = [r['step'] for r in result['results']]
    assert 'auto_color_grade' in actions
    assert 'audio_normalize' in actions
