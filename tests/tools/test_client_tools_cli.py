import json
import os
import sys

import pytest

pytest.importorskip("aiohttp")

# davinci_resolve_agent is a script directory, not a package: its modules do
# `from logger import logger`, so the directory itself has to be importable.
# examples/demo_tools_usage.py does the same thing.
_AGENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "davinci_resolve_agent")
if _AGENT_DIR not in sys.path:
    sys.path.insert(0, _AGENT_DIR)

from davinci_resolve_agent.client_simulator import ClientSimulator


@pytest.mark.asyncio
async def test_send_tool_request_monkeypatch(monkeypatch):
    client = ClientSimulator(api_key="test")

    async def fake_send_rpc_request(method, params):
        assert method == "execute_tool"
        assert "tool_name" in params
        return {"result": {"response": {"success": True}}}

    monkeypatch.setattr(client, "send_rpc_request", fake_send_rpc_request)

    resp = await client.send_tool_request("jobs.status", {"job_id": "abc"})
    assert resp["result"]["response"]["success"] is True


def test_tools_help_prints():
    # Basic string parsing check for 'tools' help message
    from davinci_resolve_agent.client_simulator import ClientSimulator

    client = ClientSimulator()
    # just ensure the method exists
    assert hasattr(client, "send_tool_request")
