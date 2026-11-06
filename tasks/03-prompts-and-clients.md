# Task 3: Add predictable prompts and model clients, 15 minutes

[Back to the activity overview](../README.md)

Create `core/prompts.py`, `adapters/models/scripted.py`, and `adapters/models/ollama.py`.

Keep all model-facing text in `core/prompts.py`. The system instruction must tell the model to repair an existing bug, first reproduce it by testing, and respond with exactly one JSON object. It must state that only these tools exist:

```json
{"summary":"Read the failing test","tool":"read_file","path":"test_calculator.py"}
{"summary":"Reproduce the bug","tool":"run_tests"}
{"tool":"edit_file","path":"calculator.py","content":"..."}
```

The prompt should contain the selected case name and a supplied relative file list. This prevents the model from inventing project paths.

`scripted.py` must implement the chat interface with a predetermined sequence of replies. Use it to test the repair loop without a model, token, Internet connection, or Docker execution of generated code.

`ollama.py` must call a local Ollama server. Use `qwen2.5-coder:7b` as the default model, allow `OLLAMA_MODEL` or a CLI option to replace it, and make temperature configurable. Request JSON output from Ollama, but still validate its returned text yourself.

## Checkpoint

```bash
python -m compileall -q core adapters/models
```

No live model call is required for this task.
