import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pytest
from src.core import mcp


@pytest.mark.anyio
async def test_workflow_tasks_availability():
    """Check if workflow tasks are registered."""
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    # These are high-level workflow tasks
    if not any(name.endswith("_task") for name in tool_names):
        pytest.skip("Workflow tasks not registered in this environment")
    assert "render_and_verify_task" in tool_names
    assert "batch_proxy_generation_task" in tool_names


@pytest.mark.anyio
async def test_maintenance_tasks_availability():
    """Check if maintenance tasks are registered."""
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    if not any(name.endswith("_task") for name in tool_names):
        pytest.skip("Maintenance tasks not registered in this environment")
    assert "update_metadata_batch_task" in tool_names
