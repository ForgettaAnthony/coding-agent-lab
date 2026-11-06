# Task 2: Build the safe workspace and tools, 25 minutes

[Back to the activity overview](../README.md)

Create `adapters/sandbox/Dockerfile`, `runner.py`, `repair_tools.py`, and `tests/test_tools.py`.

Your Docker image should contain Python, pytest, and a non-root user. The runner must start a short-lived container with networking disabled and run `pytest -q` against the copied workspace. Mount the workspace into the container without giving the container access to the rest of the host filesystem.

`runner.py` has two jobs:

1. Copy the chosen `evals/<case>` directory to a newly created temporary workspace.
2. Run tests in that workspace through Docker and return a structured test result.

`repair_tools.py` has three methods:

| Method | Required behavior |
| --- | --- |
| `read_file(path)` | Resolve a relative path inside the workspace and return UTF-8 text. |
| `edit_file(path, content)` | Resolve safely, write UTF-8 text, and record the changed relative path once. |
| `run_tests()` | Delegate to the Docker-backed runner and return its test result. |

Write a `safe_path(workspace, requested_path)` helper. It must reject absolute paths and any resolved path outside the workspace. Do not use `subprocess` to run project Python or pytest on the host.

Write tests that prove the following:

1. a normal workspace file can be read;
2. `../` traversal and absolute paths are rejected;
3. an edit is written and appears once in `changed_files`; and
4. `run_tests()` delegates to the runner rather than launching host Python.

## Prompt for your coding assistant

```text
Implement only adapters/sandbox/Dockerfile, runner.py, repair_tools.py, and
tests/test_tools.py. The host may invoke Docker, but it must never execute a
fixture's Python or pytest directly. Copy a selected eval project into a
temporary workspace. Enforce workspace-relative paths before every read or
write. Implement read_file, edit_file, and run_tests only. Do not add a shell
tool or Internet access. Write focused pytest tests for path containment,
editing, and delegation to the Docker runner.
```

## Checkpoint

```bash
python -m pytest -q tests/test_tools.py
docker build -t coding-agent-lab-runner adapters/sandbox
```

Expected outcome: your unit tests pass, and Docker builds the runner image. Do not run an evaluation project with host Python to test this task.

## Where to go next

Open [Task 3: Define prompts and model clients](03-prompts-and-clients.md).
