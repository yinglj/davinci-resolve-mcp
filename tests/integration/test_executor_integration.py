import asyncio
# FIXME: src.agent removed
# FIXME: src.agent removed
# FIXME: src.agent removed


async def _create_plan(planner, request_text):
    plan = await planner.create_plan(request_text, context=type('C', (), {'get_full_context': lambda self: {}})(), doc_rag=type('R', (), {'query': lambda self, q: ''})())
    return plan


def test_executor_runs_script_to_timeline_workflow():
    planner = TaskPlanner()
    request = "Create a timeline from script: Shot 1: Wide shot of a beach. Shot 2: Close up on a message in a bottle."
    plan = asyncio.run(_create_plan(planner, request))

    # Prepare a fake resolve_server with tools
    class FakeResolveServer:
        def __init__(self):
            self._tools = {}
            self._resources = {}

    fake = FakeResolveServer()

    # Tool: script_to_shots -> returns shots from planner parameters
    def tool_script_to_shots(**kwargs):
        # emulate parsing: return the shots based on an input script or a static list
        return [
            {'id': 'shot_001', 'summary': 'Wide shot of a beach', 'duration': 5, 'shot_type': 'wide'},
            {'id': 'shot_002', 'summary': 'Close up on a message in a bottle', 'duration': 4, 'shot_type': 'close'},
        ]

    fake._tools['script_to_shots'] = tool_script_to_shots
    fake._tools['create_placeholder_timeline'] = create_placeholder_timeline

    executor = TaskExecutor(resolve_server=fake)

    # Run the plan
    result = asyncio.run(executor.execute_plan(plan))

    assert result['success'] is True
    actions = [r['step'] for r in result['results']]
    # both script_to_shots and create_placeholder_timeline should have run
    assert 'script_to_shots' in actions
    assert 'create_placeholder_timeline' in actions

    # Ensure plan recorded executed actions
    executed = plan.get_executed_actions()
    assert any(e['action'] == 'script_to_shots' for e in executed)
    assert any(e['action'] == 'create_placeholder_timeline' for e in executed)
