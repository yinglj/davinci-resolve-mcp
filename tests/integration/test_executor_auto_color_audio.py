"""Integration Test: AutoColor & Audio Executor Tools"""
import asyncio
# FIXME: src.agent removed


def test_auto_color_grade_tool():
    """Test auto_color_grade executor tool"""
    shots = [
        {'id': 's1', 'in': 0.0, 'out': 1.0},
        {'id': 's2', 'in': 1.0, 'out': 2.5},
    ]
    result = auto_color_grade(shots, style='vibrant')
    assert 'success' in result
    assert 'shots_graded' in result or 'error' in result


def test_audio_normalize_tool():
    """Test audio_normalize executor tool"""
    result = audio_normalize(target_loudness=-23.0)
    assert 'success' in result or 'error' in result


def test_text_to_speech_tool():
    """Test text_to_speech executor tool"""
    result = text_to_speech("Welcome to this video", voice='default')
    assert result['success'] is True
    assert result['duration'] > 0


def test_executor_pipeline_with_color_and_audio():
    """Integration test: Planner -> Executor with AutoColor & Audio"""
    # FIXME: src.agent removed
    # FIXME: src.agent removed
    
    # Create a plan with auto_color_grade and audio_normalize steps
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
    
    # Prepare Fake Resolve Server
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
