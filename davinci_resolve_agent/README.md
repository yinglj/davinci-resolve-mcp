Terrabot
A JSON-RPC server for interacting with MCP servers using openai-agents.
Installation

Create a virtual environment:
python -m venv .venv
source .venv/bin/activate


Install dependencies:
pip install -r requirements.txt


Configure mcp_config.json with MCP servers and API keys.


Running
python unitemcp_server.py

The server runs at http://localhost:8080/rpc and /rpc/stream.
Testing
Test JSON-RPC endpoints using curl:
curl -X POST http://localhost:8080/rpc \
-H "Authorization: Bearer sk-1234567890abcdef" \
-H "Content-Type: application/json" \
-d '{"jsonrpc": "2.0", "method": "start_session", "params": {}, "id": 1}'

