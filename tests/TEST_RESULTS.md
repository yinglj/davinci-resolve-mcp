Test run summary (manual local runs)

- `tests/test_script_to_shots.py`: PASSED (ran via direct python invocation)
- `tests/test_create_placeholder_timeline.py`: PASSED (direct invocation)
- `tests/test_create_placeholder_timeline_resolve.py`: PASSED (using detailed resolve mock)
- `tests/test_executor_integration.py`: PASSED (integration test using FakeResolveServer)
- `tests/test_resolve_mocks.py`: PASSED (resolve mock basic checks)

Notes:
- Pytest may not be installed in the local environment; tests were executed via direct python execution of test files and validated via assertions.
- CI will run `pytest -q` on push/PR to validate the full test suite.
