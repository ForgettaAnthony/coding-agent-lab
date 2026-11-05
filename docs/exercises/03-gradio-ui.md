# Exercise 3: Gradio UI adapter (20 minutes)

[Back to the lab guide](../../README.md)

## Goal

Connect the presentation adapter to the existing repair use case. The interface must show the real execution trace, changed code, final test result, and a downloadable repaired project.

## Modify only

`adapters/gradio_ui.py`, function `repair(project_path)`.

1. Call `build_repair_service().repair(project_path)`.
2. Format and return four values, in this order:
   - trace text;
   - changed-code text;
   - test-output text; and
   - a path to a ZIP archive of `result.workspace`.

The CLI and UI must not create Docker commands, build prompts, or dispatch tools. Those responsibilities remain in lower layers.

### Vibe-coding handoff: Gradio adapter

If you use Codex, Claude, Cursor, or another coding assistant, give it this task after it has read `adapters/gradio_ui.py`, `core/models.py`, and `core/repair_service.py`:

```text
Modify only the repair(project_path) function in adapters/gradio_ui.py.

Call build_repair_service().repair(project_path). Format the returned
RepairResult for the existing Gradio components and return exactly four values
in this order:
1. the execution trace as text;
2. the changed source files as readable text, or "No files changed.";
3. the sandboxed test output as text; and
4. a path to a ZIP archive of result.workspace.

Do not modify create_demo, add Docker commands, build prompts, dispatch tools,
or change any tests or other files. Reuse the imports already provided in this
file.

Verification is part of the task:
1. Run pytest -q and report the result.
2. Build the interface without starting a server:
   python -c "from adapters.gradio_ui import create_demo; create_demo(); print('Gradio UI built')"
3. If Docker and one model provider are configured, launch python main.py ui,
   run arithmetic, and report whether the trace, changed code, test output, and
   ZIP are visible. If that live check cannot run, state the missing dependency
   instead of claiming that it passed.
```

## Checkpoint

Run from the repository root:

```bash
python main.py ui
```

Select `arithmetic`. After configuring a model provider and starting Docker, run one repair and confirm that the page displays the trace, modified code, sandboxed pytest result, and repaired-project ZIP. The command below runs the same workflow in the terminal:

```bash
python main.py repair evals/arithmetic
```

## Expected outcome

The UI is a thin adapter: it presents `RepairResult` data but does not contain repair policy or sandbox logic.
