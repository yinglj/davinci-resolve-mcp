import os
import sys
import pytest
from pathlib import Path

# Ensure project root is in path for all tests to allow "from src import ..."
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def resolve_connection():
    """Fixture to provide Resolve connection and check if available."""
    try:
        from src.core import resolve

        return resolve
    except Exception:
        return None


@pytest.fixture(scope="session")
def mcp_instance():
    """Fixture to provide the MCP server instance."""
    from src.core import mcp

    return mcp


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "real_resolve: marks tests that require a real DaVinci Resolve instance",
    )


def pytest_collection_modifyitems(config, items):
    """Automatically skip real_resolve tests if Resolve is not available."""
    from src.core import resolve

    if resolve is None:
        skip_resolve = pytest.mark.skip(
            reason="DaVinci Resolve not available or scripting API disabled"
        )
        for item in items:
            if "real_resolve" in item.keywords:
                item.add_marker(skip_resolve)

    project_root = Path(__file__).resolve().parent.parent
    agent_root = project_root / "src" / "agent"
    if not agent_root.exists():
        skip_agent = pytest.mark.skip(reason="Optional agent modules are not available")
        skip_paths = (
            str(project_root / "tests" / "api" / "color"),
            str(
                project_root
                / "tests"
                / "api"
                / "delivery"
                / "test_render_preset_runner.py"
            ),
            str(project_root / "tests" / "api" / "timeline"),
            str(project_root / "tests" / "helpers"),
            str(project_root / "tests" / "integration"),
        )
        for item in items:
            item_path = str(item.fspath)
            if item_path.startswith(skip_paths):
                item.add_marker(skip_agent)
