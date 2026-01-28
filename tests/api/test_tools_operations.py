import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
import pytest
from src.core import mcp


@pytest.mark.anyio
async def test_mcp_tools_registration():
    """Verify that MCP tools are correctly registered with FastMCP."""
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    # Check for core and essential tools
    assert "switch_page" in tool_names
    assert "create_timeline" in tool_names
    assert "add_marker_to_timeline" in tool_names
    assert "apply_lut" in tool_names
    assert "get_project_properties" in tool_names


@pytest.mark.asyncio
async def test_mcp_resources_registration():
    """Verify that MCP resources are correctly registered."""
    resources = await mcp.list_resources()
    uris = [r.uri for r in resources]

    # Check for some essential resources
    assert "resolve://database/current" in uris
    assert "resolve://timeline/timecode" in uris
    assert "resolve://project/current" in uris


@pytest.mark.asyncio
async def test_mcp_tasks_registration():
    """Verify that MCP tasks are correctly registered."""
    # Tasks are registered as tools with TaskConfig in FastMCP
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    # Check for workflow and maintenance tasks
    assert "render_and_verify_task" in tool_names
    assert "project_cleanup_task" in tool_names
    assert "batch_proxy_generation_task" in tool_names


@pytest.mark.asyncio
async def test_mcp_prompts_registration():
    """Verify that MCP prompts are correctly registered."""
    prompts = await mcp.list_prompts()
    prompt_names = [p.name for p in prompts]

    assert "workflow_summary" in prompt_names
    assert "colorist_assistant" in prompt_names


if __name__ == "__main__":
    # Manual verification script
    async def run_checks():
        print("Checking FastMCP registrations...")
        tools = await mcp.list_tools()
        print(f"Tools: {len(tools)} registered")
        resources = await mcp.list_resources()
        print(f"Resources: {len(resources)} registered")
        prompts = await mcp.list_prompts()
        print(f"Prompts: {len(prompts)} registered")
        print("Verification complete.")

    asyncio.run(run_checks())
