import asyncio
from src.agent.planner.task_planner import TaskPlanner


async def _create_plan_and_return(planner, request_text):
    plan = await planner.create_plan(request_text, context=type('C', (), {'get_full_context': lambda self: {}})(), doc_rag=type('R', (), {'query': lambda self, q: ''})())
    return plan


def test_integration_script_to_timeline():
    planner = TaskPlanner()
    request = "Create a timeline from script: Shot 1: Wide shot of a beach at dawn. Shot 2: Close up on a message in a bottle."
    plan = asyncio.run(_create_plan_and_return(planner, request))

    # Expect plan to contain a script_to_shots step
    actions = [s.action for s in plan.steps]
    assert 'script_to_shots' in actions
    # Ensure there is a create_placeholder_timeline dependent step
    assert 'create_placeholder_timeline' in actions

    # Find the generated shots step and verify parameters
    shot_steps = [s for s in plan.steps if s.action == 'script_to_shots']
    assert len(shot_steps) == 1
    shots_param = shot_steps[0].parameters.get('shots')
    assert shots_param and isinstance(shots_param, list) and len(shots_param) >= 1
