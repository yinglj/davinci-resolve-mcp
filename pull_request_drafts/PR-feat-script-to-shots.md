Title: feat(planner+executor): ScriptToShots -> Placeholder Timeline (Resolve integration) 

Body:
This PR adds a POC for converting natural-language scripts to shot lists and creating a placeholder timeline in DaVinci Resolve.

Changes:
- Register `ScriptToShots` detection in `TaskPlanner` and add `_plan_script_to_shots` step.
- Add `parse_script_to_shots` POC parser with unit tests and example: `src/agent/planner/skills/script_to_shots.py`.
- Implement `create_placeholder_timeline` that attempts to use Resolve API (`create_empty_timeline` + `add_marker`) when available, otherwise returns a deterministic local representation: `src/agent/executor/skills/create_placeholder_timeline.py`.
- Enhance `TaskExecutor` to resolve parameters referencing previous steps (e.g., `shots_reference_step`) and execute dependent steps in order.
- Add detailed Resolve mock for tests: `tests/mocks/resolve_mock.py`.
- Add unit & integration tests: `tests/test_script_to_shots.py`, `tests/test_create_placeholder_timeline*.py`, `tests/test_executor_integration.py`, `tests/test_resolve_mocks.py`.
- Add CI workflow `.github/workflows/python-ci.yml` to run tests in GitHub Actions.

Test results:
- Local test files ran successfully (assertion-based runs). See `tests/TEST_RESULTS.md`.
- Screenshot summary: `tests/test_screenshots/test_results_summary.svg` (visible in PR)

Reviewer checklist:
- [ ] Confirm Planner changes are safe and detect script intents appropriately.
- [ ] Confirm Executor dependency handling and parameter resolution logic.
- [ ] Review Resolve integration logic; validate fallback behavior when Resolve is not connected.
- [ ] Confirm tests are sufficient and deterministic.

PR link (create): https://github.com/yinglj/davinci-resolve-mcp/pull/new/feat/script-to-shots-placeholder-timeline

Notes:
- CI will run pytest on PR; please attach any additional test logs if desired.
- I can open the PR via API if you provide a GitHub token with repo:status and public_repo scopes, or you can open the link above to create the PR manually.
