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

## Checkpoint

Run this command from the repository root:

```bash
pytest -q tests/test_tools.py
```

Expected result: **4 passed**.

## What to be ready to explain

Why is `safe_path` used before every file operation, and why does `run_tests()` delegate to the Docker-backed runner instead of invoking Python directly?
