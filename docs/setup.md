# Setup and reproducibility

[Back to the lab guide](../README.md)

Use this guide before Exercise 1. It creates a repeatable starting point: your own fork, a local Python environment, a recorded repository revision, deterministic checkpoints, and a separately prepared Docker sandbox.

## 1. Fork and clone the student repository

On GitHub, click **Fork** on `MahiBegoug/coding-agent-lab`. Clone **your fork**, replacing `YOUR-USERNAME` below:

```bash
git clone https://github.com/YOUR-USERNAME/coding-agent-lab.git
cd coding-agent-lab
git remote -v
git rev-parse --short HEAD
```

Your `origin` remote should point to your fork. Record the displayed commit identifier in your lab notes; it identifies the exact starting revision you used.

## 2. Create the Python environment and install base dependencies

You need Python 3.10 or later. Python 3.11 is recommended.

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The base requirements install the exercise checkpoints and Gradio. Do not install every optional cloud integration. Install only the provider package that you plan to use for the live demonstration.

## 3. Configure one model provider for the live demonstration

The deterministic checkpoint in Step 4 does not call a model, and neither does Docker preparation in Step 5. Configure a provider now if you want to confirm your live setup early, or defer it until Exercises 1 and 2 pass.

For the default local Ollama option, first [install Ollama](https://ollama.com/download) for your operating system. Then download the model only if your computer has enough disk space and memory. If it does not, use a cloud option from the model-provider guide instead:

```bash
ollama pull qwen2.5-coder:7b
# In a separate terminal:
ollama serve
```

For Vertex AI Gemini or the OpenAI API, follow [Model providers: choose one for the live demonstration](model-providers.md). It lists the exact optional dependency and credential commands. Do not put API keys in repository files.

## 4. Run the starting unit-test checkpoint

```bash
pytest -q
```

Expected starting point: **18 passed, 10 failed**. The 10 failures are clear `NotImplementedError` messages from the student TODOs. This is expected. Exercises 1 and 2 use `ScriptedClient`, so this checkpoint needs no model, API key, Internet connection, or Docker daemon.

## 5. Prepare Docker for real sandboxed repairs

Docker Desktop is needed for a live repair, but not for the deterministic checkpoint above. Start Docker Desktop, then run:

```bash
docker info
docker build -t coding-agent-lab-runner adapters/sandbox
```

`docker info` must succeed before a live repair or UI repair. Docker is the execution boundary: it runs evaluation-project tests, while the host runs only the harness and user interface.

## 6. Record enough context to reproduce a live run

For a live repair, record the repository commit, evaluation fixture, provider, model identifier, temperature, and final test result. The fixed fixture, sandbox-image build, and recorded configuration make the conditions repeatable. A model trajectory can still vary, so compare the visible trace and the sandboxed test result rather than expecting identical model text on every run.

Example lab-note record:

```text
commit: <git rev-parse --short HEAD>
fixture: evals/arithmetic
provider: ollama
model: qwen2.5-coder:7b
temperature: 0.0
result: tests passed or tests failed
```
