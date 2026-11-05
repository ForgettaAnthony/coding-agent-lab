# Exercise 1: Safe tools (25 minutes)

[Back to the lab guide](../../README.md)

## Goal

Implement the three tools through which the agent can read, edit, and test a repair workspace. The tools must keep all file access inside the workspace and must never execute project code on the host.

## Modify only

`adapters/sandbox/repair_tools.py`

1. `read_file(path)` must resolve through `safe_path` and return UTF-8 text.
2. `edit_file(path, content)` must resolve safely, write content, and record each changed relative path once.
3. `run_tests()` must delegate to `run_pytest(self.workspace)`.

Do not add a host shell, subprocess call, or host-Python execution tool. `run_command()` is already supplied as a constrained Docker inspection capability; do not broaden its allowlist in this lab.

### Vibe-coding handoff: safe tools

If you use Codex, Claude, Cursor, or another coding assistant, give it this task after it has read `adapters/sandbox/repair_tools.py`, `adapters/sandbox/runner.py`, and `tests/test_tools.py`:

```text
Modify only adapters/sandbox/repair_tools.py.

Implement the three TODO methods in RepairTools:
1. read_file(path) must use safe_path(self.workspace, path) and return UTF-8 text.
2. edit_file(path, content) must use safe_path, write UTF-8 text, and add the
   workspace-relative path to changed_files only once.
3. run_tests() must return run_pytest(self.workspace).

Do not add subprocess calls, a host shell, host-Python execution, new tools, or
changes to runner.py or the tests. Keep run_command unchanged. Run
pytest -q tests/test_tools.py when finished.
```

## Checkpoint

Run this command from the repository root:

```bash
pytest -q tests/test_tools.py
```

Expected result: **4 passed**.

## What to be ready to explain

Why is `safe_path` used before every file operation, and why does `run_tests()` delegate to the Docker-backed runner instead of invoking Python directly?
