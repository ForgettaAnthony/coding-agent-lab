# Exercise 3 — Gradio UI adapter (20 minutes)

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
