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
    assert "render_and_verify_task" in tool_names
    assert "batch_proxy_generation_task" in tool_names


@pytest.mark.asyncio
async def test_maintenance_tasks_availability():
    """Check if maintenance tasks are registered."""
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    assert "project_cleanup_task" in tool_names
    assert "update_metadata_batch_task" in tool_names
