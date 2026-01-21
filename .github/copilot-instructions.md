# GitHub Copilot / AI Agent Instructions — DaVinci Resolve MCP Server

Purpose: short, actionable instructions to help AI coding assistants be productive in this repo.
##
- 我们自己交互使用中文
- 代码使用英文
- issues里面放了很多任务和设计文档，但进行代码设计时请优先参考这个文件和 `docs/TOOLS-USAGE.md`。同时发现好的思路和设计可以补充到 issues 里。

## Big picture (what matters) 🔧
- Modes: the server runs in three transports: `stdio`, `sse`, `streamable-http` (see `src/main.py` and README). Use `stdio` for local/embedded agents.
- Key components:
  - `src/main.py` — entrypoint and transport selection
  - `src/resolve_mcp_server.py` — MCP resource/tools registration, Resolve connection, `proxy_tool` decorator
  - `src/proxy.py` — canonical ToolProxy: register, search, execute tools
  - `src/api/` — modular tool modules (each exposes `register_tools(proxy)`)
  - `src/agent/` — planner (P1) / executor (P1) separation (planner in `src/agent/planner/skills/*`, executor in `src/agent/executor/skills/*`)
  - `davinci_resolve_agent/client_simulator.py` — example client CLI (includes `tools` subcommand)
- Why this layout: small, testable tool units are registered on a central proxy to keep MCP surface area small and searchable.

## How to add or update a tool (recipes) 🛠️
- Create a small, focused function in `src/api/<your_module>.py` and return structured dicts: prefer `{ "success": True|False, "result":..., "error":... }`.
- Provide a `register_tools(proxy)` function that calls `proxy.register_tool(...)` for each tool.
- Example (from `src/api/tools_operations.py`):

```python
# register with proxy
proxy.register_tool("fusion.create_composition", create_fusion_composition, category="fusion")
```

- For server-level commands (MCP resources) use the `proxy_tool` decorator in `src/resolve_mcp_server.py` and ensure `register_mcp_resources(mcp)` is called in `src/main.py`.
- Pattern for POC fallback: attempt to import planner/executor functions under try/except and fall back to simple deterministic responses (see `src/api/tools_operations.py`).
- Long-running tasks: schedule a job and return a `job_id`; implement `jobs.status` and `jobs.cancel` to manage lifecycle.

## Tests & CI ✅
- Unit tests: `tests/test_*.py`. Run `pytest -q` or `python -m pytest tests/test_tools_operations.py -q` for tools.
- Real Resolve tests: files named `tests/test_real_*.py` require DaVinci Resolve running and proper env vars (RESOLVE_SCRIPT_API, RESOLVE_SCRIPT_LIB). Run these only when Resolve is available.
- CI workflow: `.github/workflows/p2-03-ci-cd.yml` — keep changes that affect P1/P2 features covered by the pipeline.
- Quick syntax checks used in CI: `python -m py_compile <file>` (used across workflows).

## Debugging & local dev ⚙️
- Environment variables to check: `RESOLVE_SCRIPT_API`, `RESOLVE_SCRIPT_LIB`, `RESOLVE_MODULES_PATH` (see `src/utils/resolve_connection.py` & `scripts/check-resolve-ready.sh`).
- Run server locally:
  - Fast test (stdio): `python src/main.py --mode stdio --debug`
  - Network: `python src/main.py --mode streamable-http --port 8020`
  - Short helper: `./run-now.sh` or client-specific scripts in `scripts/`
- Logs: standard output and the logger `davinci-resolve-mcp`; check `logs/` for historical runs.

## Project conventions & style ✍️
- API surface: tools should be small, idempotent when possible, and return structured dictionaries (see `success_response` / `error_response` helpers in `src/utils/response.py`).
- Planner vs Executor: planners produce composition/specs; executors apply them to Resolve. Keep responsibilities separate (SRP).
- Typing: prefer type hints and docstrings. Files are linted via CI jobs and py_compile checks.
- Versioning & releases: bump `version` in `pyproject.toml` and update `docs/VERSION.md` and `RELEASE_*` docs; follow the release checklist in `docs/RELEASE-GUIDE-v1.4.0.md`.
- Commit message style (convention used): `type(scope): message` (e.g., `feat: add MCP tools_operations, client tools CLI, tests and docs (POC)`).

## Tests & PR checklist (short) ✅
- Add/modify unit tests for new tool logic (`tests/`)
- If a change requires Resolve, add or mark real-tests `tests/test_real_*.py`
- Run `python -m pytest` locally and ensure pipeline targets (`.github/workflows/p2-03-ci-cd.yml`) remain green
- Update docs (`docs/TOOLS-USAGE.md`), `pyproject.toml` version, and `RELEASE_NOTES` when applicable

## Useful files to reference 📚
- Entry, registration, transport: `src/main.py`, `src/resolve_mcp_server.py`
- Tool contract & registry: `src/proxy.py`, `src/api/tools_operations.py`
- Planner/Executor examples: `src/agent/planner/skills/fusion_composition.py`, `src/agent/executor/skills/fusion_executor.py`
- CLI & agents: `davinci_resolve_agent/client_simulator.py`, `davinci_resolve_agent/agnomcp_server.py`
- CI & release: `.github/workflows/p2-03-ci-cd.yml`, `docs/RELEASE-GUIDE-v1.4.0.md`

---
If you'd like, I can: (1) merge any text from `.cursorrules` into this file, (2) add brief examples for schema validation hooks (JSON Schema), or (3) add a short automation checklist to `docs/RELEASE-GUIDE-v1.4.0.md`. Which would you prefer? 
