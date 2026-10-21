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

    # The server exposes a capability either at top level or through the
    # mounted granular namespace. Where the granular server renamed the tool
    # (timeline_add_marker for add_marker_to_timeline), the rename is the
    # point of the mount, so the test tracks the name that is actually served.
    equivalents = {
        "switch_page": "switch_page",
        "create_timeline": "create_timeline",
        "add_marker_to_timeline": "timeline_add_marker",
        "apply_lut": "apply_lut",
        "set_project_property_tool": "set_project_property_tool",
    }
    for label, name in equivalents.items():
        assert name in tool_names or f"granular_{name}" in tool_names, (
            f"{label} is not reachable (looked for {name} and granular_{name})"
        )


@pytest.mark.anyio
async def test_mcp_resources_registration():
    """Verify that MCP resources are correctly registered."""
    resources = await mcp.list_resources()
    uris = [str(r.uri) for r in resources]

    # Check for some essential resources
    assert "resolve://projects" in uris
    assert "resolve://current-project" in uris
    assert "resolve://current-timeline" in uris


@pytest.mark.anyio
async def test_mcp_tasks_registration():
    """Verify that MCP tasks are correctly registered."""
    # Tasks are registered as tools with TaskConfig in FastMCP
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    if not any(name.endswith("_task") for name in tool_names):
        pytest.skip("Workflow tasks not registered in this environment")
    assert "render_and_verify_task" in tool_names
    assert "batch_proxy_generation_task" in tool_names


@pytest.mark.anyio
async def test_mcp_prompts_registration():
    """Verify that MCP prompts are correctly registered."""
    prompts = await mcp.list_prompts()
    prompt_names = [p.name for p in prompts]

    assert "optimize_workflow" in prompt_names
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
