# Task 7: Add and run an optional live Ollama repair, 15 minutes

[Back to the activity overview](../README.md)

This optional task comes after the scripted repair is working. It needs Docker
Desktop running and an available Ollama installation. It is not needed for
deterministic unit tests or the required demonstration.

## Prompt for your coding assistant

Copy this prompt into your coding assistant only if you want to use a local
model for the live demonstration.

```text
Implement adapters/models/ollama.py and make only the small changes needed in
bootstrap.py and main.py to select it with --provider ollama. OllamaClient must
satisfy the existing ChatClient protocol: it accepts the same prepared messages
as ScriptedClient and returns the model's reply text. Use qwen2.5-coder:7b as
the default model; allow --model or OLLAMA_MODEL to replace it; and allow
--temperature to configure temperature. Request JSON output from the local
Ollama server, but do not change the repair loop's independent validation.
Keep Docker execution, file tools, and repair policy unchanged. Do not add a
shell tool, Internet search, uploads, or new Python packages. Add concise
docstrings.
```

```bash
ollama pull qwen2.5-coder:7b
ollama list
python main.py repair evals/arithmetic --provider ollama --model qwen2.5-coder:7b --temperature 0.0
```

You may use another installed coding model by changing `--model`. Record the
provider, model identifier, temperature, fixture, Git revision, final test
result, and visible trace. A live model is not deterministic, so do not expect
its wording or sequence to match another group's run.

If Ollama, Docker, or the model is unavailable, show the scripted end-to-end repair and state the missing dependency. Do not report an unperformed live run as successful.

## Where to go next

Open [Task 8: Final demonstration](08-final-demonstration.md).
