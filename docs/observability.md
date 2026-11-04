# Optional Langfuse observability: trajectory analysis extension

[Back to the lab guide](../README.md)

The local `RepairResult.trace` is the basic trajectory visible in the CLI and Gradio UI. Langfuse is an optional external **observability adapter** for analyzing the same repair trajectory across runs.

Gradio and Langfuse have different roles:

- Gradio presents one repair run to a student.
- Langfuse records repair runs for later analysis.

Langfuse does not replace `adapters/gradio_ui.py` and is not required for any core exercise checkpoint.

## Setup

Install this extension only when you need it. The current Langfuse Python SDK requires Python 3.11 or later.

```bash
pip install -r requirements-langfuse.txt
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
python main.py repair evals/arithmetic --langfuse
```

For Gradio, set `ENABLE_LANGFUSE=true` before starting the UI:

```bash
export ENABLE_LANGFUSE=true
python main.py ui
```

Set `LANGFUSE_BASE_URL` only when using a non-default Langfuse region or a self-hosted instance.

## What the adapter records

`bootstrap.py` injects `LangfuseTrajectoryObserver` only when this option is enabled. The harness emits four generic events:

1. `repair_started`
2. `model_response`
3. `tool_result`
4. `repair_finished`

`adapters/observability/langfuse.py` converts them into one Langfuse agent observation with generation and tool children. It is best-effort: a telemetry failure is logged and never changes the repair decision or test result. [Langfuse Python observability documentation](https://langfuse.com/docs/observability/sdk/overview)

## Data boundary

A Langfuse trajectory can include prompts, model JSON, file contents returned by `read_file`, edit content, and test output. Do not enable it for confidential projects, credentials, personal data, or proprietary code unless your institution has approved the Langfuse deployment and retention policy. The supplied evaluation fixtures are safe examples.
