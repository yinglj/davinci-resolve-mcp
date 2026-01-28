# Test Suite Modernization Plan

## TL;DR

> **Quick Summary**: Refactor the test suite to align with the new FastMCP-based modular architecture, fixing broken imports and path issues across all test files.
> 
> **Deliverables**:
> - Modernized `tests/api/test_tools_operations.py`
> - Batch updated `sys.path` in all Python test files
> - Standardized `pytest-asyncio` configuration
> - Validated MCP tool/task registration tests
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Path Fix Script → MCP Registration Tests → Logic Mapping

---

## Context

### Original Request
The user requested to fix `tests/api/test_tools_operations.py` and apply similar fixes to all other tests in the `tests` directory, following the structural changes in `src` (removal of `src.agent`, introduction of modular `mcp_tools`/`mcp_tasks`).

### Interview Summary
**Key Discussions**:
- Confirmed re-targeting tests from old `src.agent` skill tests to new `mcp_tools` or `mcp_tasks`.
- Agreed on a batch update approach for `sys.path`.
- Standardized on `pytest` and `pytest-asyncio` for async tests.

**Research Findings**:
- `src.agent` is gone; logic is now in `src/api` and `src/mcp_tools`.
- `test_tools_operations.py` relies on `tools_operations.py` which no longer exists.
- Directory depth changes have broken `sys.path.insert(0, str(Path(__file__).parent.parent / "src"))` in many files.

### Metis Review
**Identified Gaps** (Self-resolved):
- Environment variable dependency: Ensure `RESOLVE_SCRIPT_API` and `RESOLVE_SCRIPT_LIB` are handled if required by tests.
- Cross-platform paths: Use `Path` objects consistently for `sys.path` injection.
- Scope control: Focus on making tests runnable and import-correct before deep logic refactoring.

---

## Work Objectives

### Core Objective
Restore the functionality of the test suite by aligning imports and directory structures with the project's v1.4.0 modular architecture.

### Concrete Deliverables
- `tests/api/test_tools_operations.py`: Fully functional test for MCP tool/resource/task registration.
- `tests/conftest.py`: Shared pytest fixtures and async configuration.
- `scripts/fix_test_paths.py`: A helper script to batch update `sys.path` in all tests.

### Definition of Done
- [ ] `pytest tests/api/test_tools_operations.py` passes.
- [ ] All Python files in `tests/` have correct `sys.path` to find `src`.
- [ ] No files in `tests/` import from `src.agent`, `src.proxy`, or `src.utils.tools_operations`.

### Must Have
- Comprehensive mapping of old skill tests to new API/Tool implementations.
- Automated path correction to avoid manual errors in 30+ files.

### Must NOT Have (Guardrails)
- Do NOT modify any files in `src/`.
- Do NOT delete existing test files unless they are confirmed redundant and empty.

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES
- **User wants tests**: YES (TDD for modernized tests)
- **Framework**: pytest + pytest-asyncio

### If TDD Enabled

Each TODO follows RED-GREEN-REFACTOR for the test logic itself:

**Task Structure**:
1. **RED**: Verify current test fails with `ModuleNotFoundError` or `ImportError`.
2. **GREEN**: Apply fixes (path, import, mock).
3. **REFACTOR**: Standardize with `pytest` decorators.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Environment & Paths):
├── Task 1: Setup conftest.py and standard paths
└── Task 2: Batch update all test files with fix script

Wave 2 (Logic Migration):
├── Task 3: Modernize test_tools_operations.py
└── Task 4: Re-map specific skill tests (Color, Audio, Media)

Critical Path: Task 1 → Task 2 → Task 3
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 2 | None |
| 2 | 1 | 3, 4 | None |
| 3 | 2 | None | 4 |
| 4 | 2 | None | 3 |

---

## TODOs

- [ ] 1. Initialize `tests/conftest.py` and Pytest Config

  **What to do**:
  - Create `tests/conftest.py`.
  - Configure `asyncio_mode = auto` if using newer pytest-asyncio, or provide a shared event loop fixture.
  - Add a fixture to verify DaVinci Resolve connection status to skip "Real Resolve" tests if unavailable.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`pytest`]
    - `pytest`: Standardizing the test environment.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: None

  **Acceptance Criteria**:
  - `pytest --version` works in the environment.
  - `tests/conftest.py` exists.

- [ ] 2. Batch Update `sys.path` and Remove Obsolete Imports

  **What to do**:
  - Create and run `scripts/fix_test_paths.py`.
  - The script should:
    - Walk through `tests/`.
    - Detect directory depth.
    - Replace old `sys.path.insert` lines with a robust version using `Path(__file__).resolve().parents[N]`.
    - Identify and flag files importing from `src.agent` for manual review in Task 4.

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: [`python`]
    - `python`: Required for writing the automation script.

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Task 1

  **Acceptance Criteria**:
  - All `.py` files in `tests/` have correct path injection.
  - `grep -r "src.agent" tests/` returns zero matches (except possibly in comments).

- [ ] 3. Modernize `tests/api/test_tools_operations.py`

  **What to do**:
  - Rewrite to import `mcp` from `src.core`.
  - Implement async tests to verify:
    - Tool registration (list all registered tools).
    - Resource registration (verify URIs).
    - Task registration (verify high-level workflow tasks).
  - Remove references to `tools_operations` and `proxy`.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`pytest`, `mcp`]
    - `pytest`: For test structure.
    - `mcp`: To interact with FastMCP instance.

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocked By**: Task 2

  **Acceptance Criteria**:
  - `pytest tests/api/test_tools_operations.py` passes.

- [ ] 4. Re-map Individual Skill Tests

  **What to do**:
  - Update `tests/api/color/test_auto_color_and_audio.py` to use functions from `src.api.color_operations` or `src.mcp_tools.color`.
  - Update `tests/api/media/test_import_and_tag_assets.py` to use `src.api.media_operations`.
  - Update `tests/mcp_tasks/test_script_to_shots.py` to use the new `mcp_tasks` workflow logic.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`python`, `pytest`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocked By**: Task 2

  **Acceptance Criteria**:
  - The updated tests compile and run (passing or correctly skipping if Resolve is missing).

---

## Success Criteria

### Verification Commands
```bash
pytest tests/api/test_tools_operations.py
grep -r "src.agent" tests/  # Should be empty
```

### Final Checklist
- [ ] No `ModuleNotFoundError` for `src.agent`.
- [ ] No `ImportError` for `tools_operations`.
- [ ] All tests use `Path` for `sys.path`.
- [ ] Async tests use `pytest.mark.asyncio`.
