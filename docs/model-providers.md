# Model providers: choose one for the live demonstration

[Back to the lab guide](../README.md)

No model provider is needed for Exercises 1 and 2. Their checkpoints use `ScriptedClient`. You may configure one during [setup](setup.md), or wait until those checkpoints pass; a provider is required only for the live repair demonstration.

## Command conventions for every operating system

The commands below assume that you completed the platform-specific virtual-environment step in [Setup and reproducibility](setup.md) and that the environment is active. Once it is active, use `python` and `python -m pip` on macOS, Linux, and Windows PowerShell.

For a terminal repair, use the portable `--provider` and `--model` options shown below. They avoid the POSIX-only `NAME=value command` syntax. Windows instructions in this guide use **PowerShell**. If you use Git Bash or WSL on Windows, use the macOS/Linux environment-variable form instead.

The Gradio UI has no provider flag, so it reads configuration from environment variables. Where an environment variable is required, this guide shows both forms. Run only the block for your shell:

| Shell | Set `NAME` to `value` for the current terminal |
| --- | --- |
| macOS/Linux (`zsh` or `bash`) | `export NAME="value"` |
| Windows PowerShell | `$env:NAME = "value"` |

Environment variables set this way disappear when that terminal closes. This is deliberate for API keys. Do not commit credentials to `.env` files, source files, or Git history.

The core depends on `ChatModelPort`, never on a specific vendor. `bootstrap.py` selects the concrete adapter using `MODEL_PROVIDER`.

## JSON action mode

Each adapter requests JSON output from its provider: Ollama uses the chat API's `format: "json"`, Vertex Gemini uses `response_mime_type="application/json"`, and OpenAI uses the Responses API JSON mode. This helps the model produce a parseable object, but the core still checks the exact repair-action contract before dispatching any tool. Provider JSON mode is a formatting control, not a permission system.

For further reading, see the [Ollama chat API](https://docs.ollama.com/api/chat), [Vertex controlled JSON output](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-gemini-controlled-generation-response-schema-2), and [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

## Ollama: default local option

Use the default `qwen2.5-coder:7b` only when your computer has sufficient disk space and memory. Install Ollama using its [official installer for your operating system](https://ollama.com/download), then download the model:

```bash
ollama pull qwen2.5-coder:7b
ollama list
python main.py repair evals/arithmetic --provider ollama --model qwen2.5-coder:7b
```

`ollama list` verifies that the local Ollama service is reachable. On macOS and Windows, open the Ollama application if it is not running. On Linux, start it in another terminal with `ollama serve`. Then rerun `ollama list` before starting the repair.

To select a different default for the UI, set `OLLAMA_MODEL` in the terminal that will run the UI.

**macOS/Linux**

```bash
export MODEL_PROVIDER="ollama"
export OLLAMA_MODEL="qwen2.5-coder:7b"
python main.py ui
```

**Windows PowerShell**

```powershell
$env:MODEL_PROVIDER = "ollama"
$env:OLLAMA_MODEL = "qwen2.5-coder:7b"
python main.py ui
```

## Vertex AI Gemini: cloud option

This option avoids a local model download. Install the [Google Cloud CLI](https://docs.cloud.google.com/sdk/docs/install) for your operating system before the first two commands. `gcloud init` is needed once per workstation or when you need to select a different account or project.

```bash
python -m pip install -r requirements-vertex.txt
gcloud init
gcloud auth application-default login
```

Set the Google Cloud project before a Vertex repair or UI session:

**macOS/Linux**

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
python main.py repair evals/arithmetic --provider vertex --model gemini-2.5-flash
```

**Windows PowerShell**

```powershell
$env:GOOGLE_CLOUD_PROJECT = "your-project-id"
$env:GOOGLE_CLOUD_LOCATION = "us-central1"
python main.py repair evals/arithmetic --provider vertex --model gemini-2.5-flash
```

For the UI, also set the provider and, if desired, choose a different default model:

**macOS/Linux**

```bash
export MODEL_PROVIDER="vertex"
export VERTEX_MODEL="gemini-2.5-flash"
python main.py ui
```

**Windows PowerShell**

```powershell
$env:MODEL_PROVIDER = "vertex"
$env:VERTEX_MODEL = "gemini-2.5-flash"
python main.py ui
```

The Vertex adapter uses the Google Gen AI SDK and Application Default Credentials. It is optional, so no cloud package or credential is needed for the deterministic checkpoint. Never store API keys or service-account JSON in this repository. See [Google Gen AI SDK for Vertex AI](https://googleapis.github.io/python-genai/genai.html) and [Google Cloud authentication guidance](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc).

## OpenAI API: cloud option

Use a model identifier available to your API project, such as a low-cost Nano model when enabled.

```bash
python -m pip install -r requirements-openai.txt
```

Set the API key before the repair or UI command:

**macOS/Linux**

```bash
export OPENAI_API_KEY="your-key"
python main.py repair evals/arithmetic --provider openai --model gpt-5-nano
```

**Windows PowerShell**

```powershell
$env:OPENAI_API_KEY = "your-key"
python main.py repair evals/arithmetic --provider openai --model gpt-5-nano
```

For the UI, also set the provider and, if desired, choose a different default model:

**macOS/Linux**

```bash
export MODEL_PROVIDER="openai"
export OPENAI_MODEL="gpt-5-nano"
python main.py ui
```

**Windows PowerShell**

```powershell
$env:MODEL_PROVIDER = "openai"
$env:OPENAI_MODEL = "gpt-5-nano"
python main.py ui
```

The OpenAI adapter uses the Responses API and returns text through the same `ChatModelPort`; no OpenAI dependency is installed by default. [OpenAI’s current model guide](https://developers.openai.com/api/docs/guides/latest-model.md) describes how to choose a model based on quality, speed, and cost.

## After choosing a provider

Start Docker Desktop on macOS or Windows, or start Docker Engine on Linux. Build the sandbox image if necessary, then run the CLI repair or the UI:

```bash
docker build -t coding-agent-lab-runner adapters/sandbox
```

Run a CLI repair with the provider options from the relevant section. For the UI, set `MODEL_PROVIDER` as shown in that section and then run `python main.py ui`.

## Temperature setting for Exercise 4

The model loader in `bootstrap.py` reads a `MODEL_TEMPERATURE` value between `0` and `2` before it constructs the selected provider adapter. This setting is useful for the Gradio interface and other entry points that do not expose a command-line flag:

**macOS/Linux**

```bash
export MODEL_TEMPERATURE=0.8
python main.py ui
```

**Windows PowerShell**

```powershell
$env:MODEL_TEMPERATURE = "0.8"
python main.py ui
```

The terminal repair command accepts `--temperature` for the optional [temperature experiment](exercises/04-temperature-experiment.md). An explicit command-line value takes precedence over `MODEL_TEMPERATURE`. The repair policy in `core/` does not change.

Provider support is model-specific. If a provider rejects the parameter, record that result and use a supported provider for the comparison. Do not change `top_p` during the temperature experiment.
