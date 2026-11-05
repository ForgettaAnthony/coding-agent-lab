# Exercise 2: Agent loop (65 minutes)

[Back to the lab guide](../../README.md)

## Goal

Implement the bounded repair harness: it gives task context to an LLM, executes one approved request, returns the observation, and repeats until the repair is verified or the step budget ends.

## Modify only

`core/repair_agent.py`

Read, but do not modify, `core/prompts.py`. It already provides the role constants, prompt builders, JSON validator, and tool-result formatter. The imports and the `_record` / `_finish` helper methods are already present in `repair_agent.py`.

### Build the first two messages

Implement `build_initial_messages(case_name, files)` first. Return a list with exactly two dictionaries:

1. A system message built with `SYSTEM_ROLE` and `build_system_prompt(self.research_enabled)`.
2. A user message built with `USER_ROLE` and `build_case_request(case_name, files)`.

The case name and file list give the LLM the project context it needs. Do not let it invent file paths.

### Implement one repair-loop step

Then implement `run`. Start with the initial messages and repeat for at most `max_steps` decisions. In each step:

1. Call `self.client.chat(messages)` to get the model response.
2. Add that response to `messages` with `ASSISTANT_ROLE`.
3. Call `parse_model_action(reply)`. If validation fails, return a failed `RepairResult` immediately. Do not attempt to extract JSON from prose and do not call a tool.
4. Dispatch the validated request through the provided `tools` object. The only tool names are `read_file`, `edit_file`, `run_tests`, `run_command`, and opt-in `search_github`.
5. Add the tool observation back to `messages` as a `USER_ROLE` message made with `build_tool_result(observation)`. This is how the next model decision sees what happened.

The normal repair evidence sequence is: read the relevant test and code, run tests to reproduce the failure, make one focused edit, then run tests again to verify the repair.

### Enforce the harness rules in code

- `run_command` is already a restricted inspection capability. Do not add a shell or another tool.
- Allow `search_github` only after a successful `read_file`. Before that, return a visible tool-error observation. The prompt asks for this order, but your Python code must enforce it.
- Keep the optional action `summary` in the visible trace. It is a short public statement such as “Read the failing test first,” not hidden reasoning and not a new permission.
- Keep the latest test result. Return success only when `run_tests` reports that tests passed.

### Record the visible trajectory and stop cleanly

Call `self._record(...)` for `repair_started`, each `model_response`, and each `tool_result`. These calls work whether or not optional observability is configured. Do not import Langfuse here.

For every terminal outcome, call `self._finish(result)` before returning the `RepairResult`:

- tests pass;
- the model response fails the JSON contract; or
- the decision budget is exhausted.

This loop is the **agent harness**: it supplies context, keeps conversation state, limits capabilities, records observations, and decides when to stop.

## JSON request format

The model must return exactly one complete JSON object. The harness rejects Markdown fences, prose, arrays, repeated keys, unknown tools, missing arguments, and extra fields before it dispatches a tool. Do not strip wrappers or attempt to extract JSON from prose.

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

Expected results: **6 passed**, then **27 passed**. `ScriptedClient` proves the agent loop without model non-determinism or generated-code execution on the host. `test_github_research.py`, `test_json_contract.py`, `test_langfuse_observability.py`, `test_model_temperature.py`, and `test_project_selection.py` use fakes or workspace copies, so the checkpoint never needs a token, Langfuse account, or Internet access.
