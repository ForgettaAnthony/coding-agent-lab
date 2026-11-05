# Model providers: choose one for the live demonstration

[Back to the lab guide](../README.md)

No model provider is needed for Exercises 1 and 2. Their checkpoints use `ScriptedClient`. You may configure one during [setup](setup.md), or wait until those checkpoints pass; a provider is required only for the live repair demonstration.

The core depends on `ChatModelPort`, never on a specific vendor. `bootstrap.py` selects the concrete adapter using `MODEL_PROVIDER`.

## JSON action mode

Each adapter requests JSON output from its provider: Ollama uses the chat API's `format: "json"`, Vertex Gemini uses `response_mime_type="application/json"`, and OpenAI uses the Responses API JSON mode. This helps the model produce a parseable object, but the core still checks the exact repair-action contract before dispatching any tool. Provider JSON mode is a formatting control, not a permission system.

For further reading, see the [Ollama chat API](https://docs.ollama.com/api/chat), [Vertex controlled JSON output](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-gemini-controlled-generation-response-schema-2), and [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

## Ollama: default local option

Use the default `qwen2.5-coder:7b` only when your computer has sufficient disk space and memory.

```bash
ollama pull qwen2.5-coder:7b
# In a separate terminal: ollama serve
MODEL_PROVIDER=ollama python main.py repair evals/arithmetic --model qwen2.5-coder:7b
```

## Vertex AI Gemini: cloud option

This option avoids a local model download.

```bash
pip install -r requirements-vertex.txt
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
MODEL_PROVIDER=vertex python main.py repair evals/arithmetic --model gemini-2.5-flash
```

The Vertex adapter uses the Google Gen AI SDK and Application Default Credentials. It is optional, so no cloud package or credential is needed for the deterministic checkpoint. Never store API keys or service-account JSON in this repository. See [Google Gen AI SDK for Vertex AI](https://googleapis.github.io/python-genai/genai.html) and [Google Cloud authentication guidance](https://docs.cloud.google.com/docs/authentication).

## OpenAI API: cloud option

Use a model identifier available to your API project, such as a low-cost Nano model when enabled.

```bash
pip install -r requirements-openai.txt
export OPENAI_API_KEY="your-key"
MODEL_PROVIDER=openai python main.py repair evals/arithmetic --model gpt-5-nano
```

The OpenAI adapter uses the Responses API and returns text through the same `ChatModelPort`; no OpenAI dependency is installed by default. [OpenAI’s current model guide](https://developers.openai.com/api/docs/guides/latest-model.md) describes how to choose a model based on quality, speed, and cost.

## After choosing a provider

Start Docker Desktop, build the sandbox image if necessary, then run the CLI repair or the UI:

```bash
docker build -t coding-agent-lab-runner adapters/sandbox
python main.py repair evals/arithmetic
python main.py ui
```

## Temperature setting for Exercise 4

The model loader in `bootstrap.py` reads a `MODEL_TEMPERATURE` value between `0` and `2` before it constructs the selected provider adapter. This setting is useful for the Gradio interface and other entry points that do not expose a command-line flag:

```bash
export MODEL_TEMPERATURE=0.8
python main.py ui
```

The terminal repair command accepts `--temperature` for the optional [temperature experiment](exercises/04-temperature-experiment.md). An explicit command-line value takes precedence over `MODEL_TEMPERATURE`. The repair policy in `core/` does not change.

Provider support is model-specific. If a provider rejects the parameter, record that result and use a supported provider for the comparison. Do not change `top_p` during the temperature experiment.
