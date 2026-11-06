# Task 4: Implement the repair loop, 40 minutes

[Back to the activity overview](../README.md)

Create `core/repair_agent.py` and `tests/test_agent.py`. This is the central part of the activity.

The repair agent must follow this sequence:

```text
selected case and file list
        ↓
system and user messages
        ↓
model returns one JSON action
        ↓
validate action, enforce policy, call one tool
        ↓
append the tool observation to conversation history
        ↓
repeat until a verified repair or a stop condition
```

Implement these requirements:

1. Start with a system message and user message built from `core/prompts.py`.
2. Call `client.chat(messages)` once per decision.
3. Parse exactly one JSON object. Reject prose, Markdown fences, arrays, malformed JSON, duplicate fields, unknown tools, missing fields, and extra fields.
4. Add the model reply to history, then return the tool observation as the next user message.
5. Allow only `read_file`, `run_tests`, and `edit_file`.
6. Require at least one successful local `read_file` action and one failing sandboxed `run_tests` result before an edit.
7. Return success only after a later `run_tests` result passes.
8. Stop and return a failed result after invalid JSON or a fixed decision budget, such as eight decisions.
9. Record visible events named `repair_started`, `model_response`, `tool_result`, and `repair_finished`.

The trace may include the public action summary and tool result. It must not ask the model for hidden reasoning.

Write deterministic tests using `ScriptedClient`. Test a successful repair sequence, invalid JSON that executes no tool, a budget exhaustion, and a rejected edit before a reproduced failing test.

## Prompt for your coding assistant

```text
Implement only core/repair_agent.py and tests/test_agent.py. Use the existing
core data objects, prompt helpers, and interfaces. Build a bounded loop that
accepts only strict JSON actions for read_file, run_tests, and edit_file. It
must read local code and reproduce a failing sandboxed test before editing.
Append every model reply and tool observation to history, record visible trace
events, and stop on verified tests, invalid JSON, or an eight-step budget.
Use ScriptedClient for deterministic tests. Do not import Docker, Ollama,
Gradio, or adapters from core/repair_agent.py.
```

## Checkpoint

```bash
python -m pytest -q tests/test_agent.py
python -m pytest -q
```

Expected outcome: all tests you wrote pass. The tests must not contact Ollama or execute generated project code on the host.
