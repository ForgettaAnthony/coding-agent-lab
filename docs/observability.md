# Optional Langfuse observability: trajectory analysis extension

[Back to the lab guide](../README.md)

The local `RepairResult.trace` is the basic trajectory. The CLI displays it live as the agent runs; Gradio displays it after a repair completes. Langfuse is an optional external **observability adapter** for analyzing the same repair trajectory across runs.

The three views have different roles:

- The CLI prints each model response, tool observation, and final result immediately.
- Gradio presents one repair run to a student.
- Langfuse records repair runs for later analysis.

`adapters/observability/terminal.py` is enabled only for `python main.py repair ...`. It prints locally and forwards the same events to Langfuse when `--langfuse` is enabled. Langfuse does not replace `adapters/gradio_ui.py` and is not required for any core exercise checkpoint.

## Connect Langfuse

Langfuse is a trajectory recorder, not a model provider. First configure one model provider as described in [Model providers](model-providers.md). Then complete the following one-time Langfuse setup. The optional Langfuse Python SDK requires Python 3.11 or later.

### 1. Create or open a Langfuse project

1. Create an account or sign in at [Langfuse Cloud](https://cloud.langfuse.com), or use the self-hosted Langfuse address supplied by your institution.
2. Create a project, for example `coding-agent-lab`, or open the course project provided by your instructor.
3. In that project, open **Settings → API Keys** and create a project API-key pair.
4. Copy the public key (`pk-lf-...`) and secret key (`sk-lf-...`). Treat the secret key like a password; do not put either key in the repository.

If your class uses a shared or self-hosted Langfuse project, use the project and connection details supplied by course staff rather than creating a new one.

### 2. Choose the correct Langfuse base URL

Set `LANGFUSE_BASE_URL` to the same Langfuse region or self-hosted server where you created the keys. Use the base URL only, without an `/api` suffix.

| Langfuse destination | `LANGFUSE_BASE_URL` |
| --- | --- |
| Cloud EU | `https://cloud.langfuse.com` |
| Cloud US | `https://us.cloud.langfuse.com` |
| Cloud Japan | `https://jp.cloud.langfuse.com` |
| Institution/self-hosted | The URL supplied by course staff |

### 3. Connect from the terminal and record one repair

Install the optional dependency, set the three Langfuse variables in the same terminal, then start a repair with `--langfuse`.

**macOS/Linux**

```bash
python -m pip install -r requirements-langfuse.txt
export LANGFUSE_PUBLIC_KEY="pk-lf-paste-your-public-key"
export LANGFUSE_SECRET_KEY="sk-lf-paste-your-secret-key"
export LANGFUSE_BASE_URL="https://cloud.langfuse.com"
python main.py repair evals/arithmetic --langfuse
```

**Windows PowerShell**

```powershell
python -m pip install -r requirements-langfuse.txt
$env:LANGFUSE_PUBLIC_KEY = "pk-lf-paste-your-public-key"
$env:LANGFUSE_SECRET_KEY = "sk-lf-paste-your-secret-key"
$env:LANGFUSE_BASE_URL = "https://cloud.langfuse.com"
python main.py repair evals/arithmetic --langfuse
```

Replace the base URL if you use another region or a self-hosted server. The `--langfuse` flag records the CLI run; it does not change the repair policy or the test result.

### 4. Find the recorded trajectory

After the repair completes, open the same Langfuse project. A run is recorded as `python-repair-agent`, with `model-response` children for model replies and tool children such as `read_file`, `edit_file`, or `run_tests`. Langfuse sends data in the background, so wait briefly and refresh if the run is not visible immediately.

### Connect Gradio

Keep the three Langfuse variables set in the terminal, then add `ENABLE_LANGFUSE=true` before starting the UI:

**macOS/Linux**

```bash
export ENABLE_LANGFUSE=true
python main.py ui
```

**Windows PowerShell**

```powershell
$env:ENABLE_LANGFUSE = "true"
python main.py ui
```

The variables disappear when the terminal closes. Do not place Langfuse keys in source code, notebooks, prompts, or files committed to Git.

## What the adapter records

`bootstrap.py` injects `LangfuseTrajectoryObserver` only when this option is enabled. The harness emits four generic events:

1. `repair_started`
2. `model_response`
3. `tool_result`
4. `repair_finished`

`adapters/observability/langfuse.py` converts them into one Langfuse agent observation with generation and tool children. It is best-effort: a telemetry failure is logged and never changes the repair decision or test result. For the provider's own setup details, see [Get Started with LLM Tracing](https://langfuse.com/docs/observability/get-started), [Python SDK configuration](https://langfuse.com/docs/observability/sdk/overview), and [data regions](https://langfuse.com/security/data-regions).

## Data boundary

A Langfuse trajectory can include prompts, model JSON, file contents returned by `read_file`, edit content, and test output. Do not enable it for confidential projects, credentials, personal data, or proprietary code unless your institution has approved the Langfuse deployment and retention policy. The supplied evaluation fixtures are safe examples.
