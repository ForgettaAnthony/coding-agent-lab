# Task 6: Add the Gradio interface, 20 minutes

[Back to the activity overview](../README.md)

Create `adapters/gradio_ui.py`. It is a presentation layer, not another repair agent.

The page must:

- offer only the five supplied evaluation projects as project choices;
- start the same repair service used by the terminal;
- show the execution trace, changed file content, and final test output; and
- provide a ZIP file containing the repaired disposable workspace.

Do not add a file-upload component. Do not build prompts, call Docker directly, or make policy decisions in the UI.

Add a `ui` command to `main.py`:

```bash
python main.py ui
```

## Checkpoint

```bash
python -c "from adapters.gradio_ui import create_demo; create_demo(); print('Gradio UI built')"
python main.py ui
```

Expected outcome: the first command builds the interface. In the browser, selecting `arithmetic` produces the same kind of trace and result as the terminal command.
