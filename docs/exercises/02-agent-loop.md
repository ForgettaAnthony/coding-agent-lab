# Exercise 2 — Agent loop (65 minutes)

[Back to the lab guide](../../README.md)

## Goal

Implement the bounded repair harness: it gives task context to an LLM, executes one approved request, returns the observation, and repeats until the repair is verified or the step budget ends.

## Modify only

`core/repair_agent.py`

Read, but do not modify, `core/prompts.py`. It supplies the role names and prompt templates.

1. Use `build_system_prompt`, `build_case_request`, `SYSTEM_ROLE`, and `USER_ROLE` to build the initial system and user messages. Include the selected case and supplied project file list so the LLM does not invent paths.
2. Call `self.client.chat(messages)` and parse one JSON response.
3. Preserve an action's optional `summary` in the visible trace. It is a brief public action plan, such as “Read the failing test first,” not hidden reasoning; it never expands tool authority.
4. Follow the supplied evidence sequence: inspect a test, reproduce its failure with `run_tests`, make a focused edit, and verify it with `run_tests`. Dispatch only `read_file`, `edit_file`, `run_tests`, the supplied restricted `run_command`, and opt-in `search_github` on the injected `tools` object.
5. Append the response using `ASSISTANT_ROLE`, then a `USER_ROLE` message built with `build_tool_result(observation)` after every tool action.
6. Reject `search_github` with a visible tool error until a `read_file` action succeeds; do not rely on the prompt alone for this policy.
7. Emit `repair_started`, `model_response`, and `tool_result` through `self._record(...)`. Return every terminal `RepairResult` through `self._finish(...)`. The observer is optional: never import Langfuse in this file.
8. Stop when tests pass, a malformed model response arrives, or `max_steps` is reached. Return `RepairResult` in every outcome.

The harness controls are **context**, **state**, **capability boundary**, **observation loop**, **traceability**, and **termination policy**.

## JSON request format

The deterministic checkpoint returns bare JSON. A real model may surround its JSON with one outer Markdown code fence despite the prompt; accept that fence before calling `json.loads`, but do not attempt to extract JSON from arbitrary prose.

```json
{"summary":"Read the failing test first","tool":"read_file","path":"test_calculator.py"}
{"summary":"Reproduce the reported failure","tool":"run_tests"}
{"tool":"edit_file","path":"calculator.py","content":"def add(a, b):\n    return a + b\n"}
{"tool":"run_tests"}
{"tool":"run_command","command":"find . -maxdepth 2 -type f"}
{"tool":"search_github","query":"normalize_name language:Python"}
```

The first four requests show the normal repair sequence. `run_command` and `search_github` are optional capabilities with separate policies.

## One repair cycle

```text
Model:   {"summary":"Read the failing test first","tool":"read_file","path":"test_calculator.py"}
Harness: TOOL_RESULT
         from calculator import add
         ...
Model:   {"summary":"Reproduce the reported failure","tool":"run_tests"}
Harness: TOOL_RESULT
         {"passed": false, "output": "1 failed ...", "returncode": 1}
Model:   {"tool":"edit_file","path":"calculator.py","content":"..."}
Harness: TOOL_RESULT
         Wrote calculator.py
Model:   {"tool":"run_tests"}
Harness: TOOL_RESULT
         {"passed": true, "output": "2 passed ...", "returncode": 0}
```

## Checkpoint

Run these commands from the repository root. They make no Ollama call.

```bash
pytest -q tests/test_agent.py
pytest -q
```

Expected results: **5 passed**, then **14 passed**. `ScriptedClient` proves the agent loop without model non-determinism or generated-code execution on the host. `test_github_research.py`, `test_langfuse_observability.py`, and `test_project_selection.py` use fakes or workspace copies, so the checkpoint never needs a token, Langfuse account, or Internet access.
