# TOOLS Integration Plan: client_simulator ↔ agnomcp_server (MCP Tools)

**Status**: 📋 Planned
**Author**: GitHub Copilot
**Created**: 2026-01-20

## Summary

Make it simple for end users to produce videos via the client (`client_simulator.py`) driving the server (`agnomcp_server.py`) using a set of well-scoped MCP "tools". The result should be a clear phased plan and actionable tasks in issues so the work can be executed, reviewed, and tracked.

Related: `src/api/tools_operations.py`, `docs/TOOLS-USAGE.md`, tests/test_tools_operations.py

---

## Goals

- Expose Fusion / Audio / Color / Render operations as small, testable MCP tools
- Provide a minimal and ergonomic CLI experience in `client_simulator.py` (tools subcommand)
- Ensure server-side validation, job lifecycle (status/cancel), and POC fallback work reliably
- Provide unit/integration/E2E tests and docs, and integrate into CI

---

## Phases & Tasks

### Phase 0 — Design & API Contract (1 day)
- [ ] Finalize tool list and parameter JSON Schemas (fusion.create_composition, fusion.apply_to_timeline, audio.create_chain, color.auto_color_timeline, render.preview, jobs.status, jobs.cancel)
- [ ] Document request/response examples in `docs/TOOLS-USAGE.md`
- [ ] Define acceptance criteria and error codes

### Phase 1 — Server Implementation (1–2 days)
- [ ] Implement `src/api/tools_operations.py` with POC fallback (done — initial POC created)
- [ ] Integrate job store and lifecycle endpoints (status / cancel) (POC exists)
- [ ] Add robust input validation (JSON Schema) and API key guarding
- [ ] Add unit tests for each tool’s happy/failure paths (tests/test_tools_operations.py) (scaffold added)

### Phase 2 — Client Integration (1 day)
- [ ] Add ergonomic CLI commands to `client_simulator.py`: `tools list`, `tools call`, `tools status`, `tools cancel` (basic implementation added)
- [ ] Provide example scripts in `scripts/` or `examples/` to demonstrate typical workflows
- [ ] Add a demo scenario that performs: plan composition -> apply to timeline -> create audio chain -> render preview
- [ ] Add tests for client CLI interaction (tests/test_client_tools_cli.py) (scaffold added)

### Phase 3 — Integration & CI (1 day)
- [ ] Add integration tests that mock Resolve (end-to-end flows)
- [ ] Update CI (`.github/workflows/p2-03-ci-cd.yml`) to run new tests and coverage checks
- [ ] Ensure performance and memory KPIs in PHASE-2-ROADMAP are met (add targeted tests)

### Phase 4 — Docs & Release (0.5 day)
- [ ] Expand `docs/TOOLS-USAGE.md` with JSON schema and examples
- [ ] Add section in `docs/RELEASE-GUIDE-v1.4.0.md` about tools usage and release notes
- [ ] Prepare PR and tag release (v1.4.0 or next patch)

---

## Acceptance Criteria
- Tools callable via MCP `execute_tool` and `client_simulator.tools` commands
- Job lifecycle endpoints return deterministic states and support cancel
- Tests: unit (>=1 per tool), integration (mocked Resolve), E2E (client → server flow)
- CI runs and reports coverage for the new code
- Demo script demonstrates a full video creation flow

---

## Notes
- Initial POC code and tests have been added (`src/api/tools_operations.py`, `tests/test_tools_operations.py`, `docs/TOOLS-USAGE.md`, `client_simulator` support). This issue will organize follow-ups into explicit checklist items.
- Assign owners and due dates per task when ready.

---

## Next Actions
- [ ] Create sub-issues for JSON Schema, CI, Integration tests, and demo scripts
- [ ] Add this issue to `issues/INDEX.md` and reference in `PHASE-2-ROADMAP.md`

---

**References:** docs/TOOLS-USAGE.md, tests/test_tools_operations.py, src/api/tools_operations.py
