# Task 1: Define the agent's small vocabulary, 15 minutes

[Back to the activity overview](../README.md)

Create `core/models.py` and `core/ports.py` first. Do not call Ollama, Docker, or Gradio here.

Create small data objects for:

- a test result: `passed`, `output`, and `returncode`;
- an action requested by the model: `tool`, arguments, and optional public `summary`; and
- the final repair result: whether it passed, trace entries, changed files, workspace location, and the most recent test result.

In `core/ports.py`, describe the capabilities that the repair agent needs:

- a chat client with `chat(messages) -> str`;
- repair tools with `read_file`, `edit_file`, and `run_tests`; and
- optionally, a trace recorder with one `record(event, payload)` method.

Use Python `Protocol` types or small abstract interfaces. The repair agent will depend on these descriptions, not on Ollama or Docker classes.

## Prompt for your coding assistant

```text
Create core/models.py and core/ports.py only. Define minimal typed data
objects for a repair result, test result, and model action. Define interfaces
for a chat client and the three repair tools: read_file, edit_file, run_tests.
Use only the standard library and core modules. Do not import adapters,
Docker, Gradio, or an HTTP client. Add concise docstrings.
```

## Checkpoint

```bash
python -m compileall -q core
```
