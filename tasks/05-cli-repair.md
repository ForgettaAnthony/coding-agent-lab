# Task 5: Assemble the command-line repair, 15 minutes

[Back to the activity overview](../README.md)

Create `core/repair_service.py`, `bootstrap.py`, and `main.py`.

`repair_service.py` selects an allowed evaluation case, creates its disposable copy, gives the agent the case's relative file list, and returns the final repair result. It must reject paths outside `evals/`.

`bootstrap.py` creates the real tools, model client, and repair service. It is the only file that imports both `core/` and `adapters/` to connect the pieces.

`main.py` provides this command:

```bash
python main.py repair evals/arithmetic --provider scripted
```

Print each visible trace event as it occurs, then print the changed files and final sandboxed test result. Configure the scripted client with a known valid sequence that repairs the arithmetic fixture. This makes a complete end-to-end check possible without an LLM.

## Checkpoint

```bash
python main.py repair evals/arithmetic --provider scripted
python main.py repair evals/multi_function --provider scripted
```

Expected outcome: each command prints a trace that shows local inspection, a failing test, an edit, and a passing test. The original files under `evals/` remain unchanged.

## Where to go next

Open [Task 6: Add the Gradio interface](06-gradio-ui.md).
