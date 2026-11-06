# Task 7: Run a live Ollama repair, 10 minutes

[Back to the activity overview](../README.md)

This optional task needs Docker Desktop running and an available Ollama installation. It is not needed for deterministic unit tests.

```bash
ollama pull qwen2.5-coder:7b
ollama list
python main.py repair evals/arithmetic --provider ollama --model qwen2.5-coder:7b --temperature 0.0
```

You may use another installed coding model by changing `--model`. Record the provider, model identifier, temperature, fixture, Git revision, final test result, and visible trace. A live model is not deterministic, so do not expect its wording or sequence to match another group's run.

If Ollama, Docker, or the model is unavailable, show the scripted end-to-end repair and state the missing dependency. Do not report an unperformed live run as successful.

## Where to go next

Open [Task 8: Final demonstration](08-final-demonstration.md).
