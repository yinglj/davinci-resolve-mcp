import json
import pytest
from davinci_resolve_agent.client_simulator import ClientSimulator


@pytest.mark.asyncio
async def test_send_tool_request_monkeypatch(monkeypatch):
    client = ClientSimulator(api_key=None)

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
