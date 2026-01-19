# Summary

This PR implements the Script->Shots -> Create Placeholder Timeline workflow and test coverage.

## What changed
- Register `ScriptToShots` integration in `TaskPlanner` (detect script intent and create plan steps)
- Add `ScriptToShots` POC parser: `src/agent/planner/skills/script_to_shots.py` (parser, tests, example)
- Add `create_placeholder_timeline` POC that now integrates with Resolve if available: `src/agent/executor/skills/create_placeholder_timeline.py`
- Enhance `TaskExecutor` to resolve step-parameter references and to execute dependent steps correctly: `src/agent/executor/task_executor.py`
- Add detailed Resolve mock for testing: `tests/mocks/resolve_mock.py`
- Add unit and integration tests: `tests/test_script_to_shots.py`, `tests/test_create_placeholder_timeline.py`, `tests/test_create_placeholder_timeline_resolve.py`, `tests/test_executor_integration.py`, `tests/test_resolve_mocks.py`
- Add CI workflow for running tests: `.github/workflows/python-ci.yml`

## Why
- Provide a baseline for converting natural language scripts to edit plans and creating placeholder timelines in Resolve for iterative refinement.

## Testing
- Unit tests and integration tests included. See `tests/` for details.
- Local test runs executed (individual tests for parser, timeline POC and integration passed). See `tests/TEST_RESULTS.md` for run summary.

## Notes
- `create_placeholder_timeline` uses `src.resolve_mcp_server.get_resolve()` when available; otherwise it falls back to a deterministic local representation (suitable for CI and offline testing).

## Reviewer checklist ✅
- [ ] Code quality and style look good
- [ ] Planner integration is correct and non-breaking
- [ ] Executor correctly handles dependencies and result propagation
- [ ] Tests are comprehensive and deterministic (mocks used where appropriate)
- [ ] CI status: Green (if failing, ask for logs and reproduce locally)

| Files touched | Purpose |
|---|---|
| `src/agent/planner/*` | Planner & skills integration |
| `src/agent/executor/*` | Executor + placeholder timeline skill |
| `tests/*` | Unit and integration tests, and mocks |

Please attach additional test logs or screenshots if you want them included here.
