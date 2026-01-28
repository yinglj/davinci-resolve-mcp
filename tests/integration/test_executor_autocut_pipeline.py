import asyncio
# FIXME: src.agent removed
# FIXME: src.agent removed
# FIXME: src.agent removed
# FIXME: src.agent removed


async def _create_plan(planner, request_text):
    plan = await planner.create_plan(request_text, context=type('C', (), {'get_full_context': lambda self: {}})(), doc_rag=type('R', (), {'query': lambda self, q: ''})())
    return plan


def test_executor_autocut_pipeline():
    planner = TaskPlanner()

    request = "Create a timeline from script with music 120 bpm: Shot 1: Wide shot; Shot 2: Close up."
    plan = asyncio.run(_create_plan(planner, request))

    actions = [s.action for s in plan.steps]
    assert 'script_to_shots' in actions
    # Autocut step should be present due to bpm mention
    assert 'auto_cut' in actions
    assert 'create_placeholder_timeline' in actions

    # Prepare fake resolve server
    class FakeResolveServer:
        def __init__(self):
            self._tools = {}
            self._resources = {}

    fake = FakeResolveServer()

    # Provide script_to_shots tool returning static shots
    def tool_script_to_shots(**kwargs):
        return [
            {'id': 'shot_001', 'summary': 'Wide shot', 'duration': 1.0},
            {'id': 'shot_002', 'summary': 'Close up', 'duration': 2.0},
        ]

    fake._tools['script_to_shots'] = tool_script_to_shots
    fake._tools['auto_cut'] = auto_cut
    fake._tools['create_placeholder_timeline'] = create_placeholder_timeline

    executor = TaskExecutor(resolve_server=fake)
    result = asyncio.run(executor.execute_plan(plan))

    assert result['success'] is True
    executed = plan.get_executed_actions()
    assert any(e['action'] == 'auto_cut' for e in executed)
    assert any(e['action'] == 'create_placeholder_timeline' for e in executed)

    # Ensure the create_placeholder_timeline had shots with in/out set (via auto_cut output)
    tl_exec = [e for e in executed if e['action'] == 'create_placeholder_timeline'][0]
    res = tl_exec['result']
    # It should include 'shots' in the result
    assert res.get('shots') and isinstance(res.get('shots'), list)
    for s in res['shots']:
        assert 'in' in s and 'out' in s
