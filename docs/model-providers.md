# Model providers: choose one for the live demonstration

[Back to the lab guide](../README.md)

No model provider is needed for Exercises 1 and 2. Their checkpoints use `ScriptedClient`. After the checkpoints pass, choose one provider for the live repair demonstration.

The core depends on `ChatModelPort`, never on a specific vendor. `bootstrap.py` selects the concrete adapter using `MODEL_PROVIDER`.

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
