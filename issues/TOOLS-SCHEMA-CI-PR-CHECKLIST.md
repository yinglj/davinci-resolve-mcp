# TOOLS: JSON Schema, CI & PR Checklist (Follow-up)

**Status:** 📋 Planned
**Author:** GitHub Copilot
**Created:** 2026-01-21

## Summary
Add JSON Schema validation for MCP tools, unit tests for invalid inputs, CI enforcement, and a short PR checklist for tool changes. This consolidates follow-ups from `TOOLS-INTEGRATION-PLAN.md` and ensures tool inputs are discoverable and enforced.

## Tasks
- [ ] Define per-tool JSON Schemas and store them in `src/api/tool_schemas.py` (or co-locate next to tool implementation)
- [ ] Expose schema in `proxy.register_tool(..., parameters=SCHEMA)` or `parameters_schema` meta-key
- [ ] Add `jsonschema` to `requirements.txt` and CI job dependencies
- [ ] Add unit tests for each tool validating both valid and invalid payloads (`tests/test_tools_schema_validation.py`)
- [ ] Add integration test(s) that exercise `execute_resolve_tool` via `proxy.execute_tool` with schema validation enabled
- [ ] Update `.github/workflows/p2-03-ci-cd.yml` to run schema validation unit tests and fail on schema errors
- [ ] Add a short PR checklist item (see `docs/RELEASE-GUIDE-v1.4.0.md`) requiring schema for tools
- [ ] Update `docs/TOOLS-USAGE.md` with an example JSON Schema (and link to the code example in `src/api/tools_operations.py`)

## Acceptance Criteria
- All tools have associated JSON Schemas and tests
- CI runs schema validation tests on PRs and fails when invalid inputs are introduced
- Documentation includes an example and link to schema source

## Notes
- Prototype approach: validate inputs at tool entry (in tool wrapper) and return `{"success": False, "error": "invalid_parameters", ...}`
- Avoid breaking existing users: validation optional at first with a feature flag in `.resolve-mcp/config.json` (e.g., `validate_tool_inputs: true`)

---

Please assign owners and break this into sub-issues for parallel work if preferred.