from starlette.testclient import TestClient

from src.__main__ import build_http_middleware
from src.core import mcp


def test_streamable_http_transport_handles_cors_preflight():
    app = mcp.http_app(
        transport="streamable-http",
        middleware=build_http_middleware(),
    )

    with TestClient(app) as client:
        response = client.options(
            "/mcp",
            headers={
                "Origin": "https://inspector.example",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"


def test_streamable_http_initialize_exposes_session_header_for_browser_clients():
    app = mcp.http_app(
        transport="streamable-http",
        middleware=build_http_middleware(),
    )

    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            headers={
                "Origin": "https://inspector.example",
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0"},
                },
            },
        )

    assert response.status_code == 200
    assert response.headers["mcp-session-id"]
    assert response.headers["access-control-expose-headers"] == (
        "mcp-session-id, mcp-protocol-version"
    )
