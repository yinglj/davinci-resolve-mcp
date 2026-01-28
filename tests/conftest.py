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
