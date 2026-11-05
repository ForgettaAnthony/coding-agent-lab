# Exercise 4: Temperature experiment (20 minutes, optional)

[Back to the lab guide](../../README.md)

## Goal

Conduct a small, controlled experiment on how an LLM sampling setting can affect a coding-agent trajectory. You will keep the repair fixture and harness fixed, change only temperature, and compare the visible traces and test outcomes.

This is an empirical exercise. You do not modify any source files. It requires a configured live provider and is not part of the required 2.5-hour implementation path.

## What temperature changes

Temperature is a sampling setting for the model response. Lower values usually make sampling more focused; higher values usually allow more variation. It does not guarantee repeatable output, and it does not make the repair more correct.

In this lab, temperature changes only model generation. It does not change the project copy, system prompt, available tools, Docker sandbox, test runner, or the agent's fixed step budget. The harness still decides whether a repair passes by running tests.

## Architecture boundary

```text
main.py --temperature 0.8 or MODEL_TEMPERATURE=0.8
        ↓
bootstrap.py model loader
        ↓
adapters/models/<provider>.py
        ↓
provider request

core/ remains unchanged
```

Temperature is provider configuration, so it belongs at the outer edge of the architecture. `RepairAgent` receives a `ChatModelPort` and does not need to know which model setting produced a response.

## Before you begin

1. Complete Exercises 1 and 2.
2. Configure one provider using the [model-provider guide](../model-providers.md).
3. Confirm the temperature configuration code without calling a model:

   ```bash
   pytest -q tests/test_model_temperature.py
   ```

   Expected result: **5 passed**.

4. Use the same provider and model for every run in this exercise. Choose a provider that you have already configured for the final demonstration.

### Vibe-coding handoff: controlled experiment

If you use a coding assistant to help conduct the experiment, give it this task:

```text
Do not modify source code, prompts, tests, Docker settings, or model-provider
configuration files.

First run pytest -q tests/test_model_temperature.py. Then run the supplied
repair command for temperature 0.0 and 0.8 using the same fixture, provider,
model identifier, repository revision, and step budget. Save each terminal
trace. Summarize only observed differences in the traces and final test
results. Do not claim that one temperature is better from these few runs.
```

## Research question and controls

Use this question:

> With the same model, prompt, fixture, and harness settings, how do repair traces and outcomes differ between temperature `0.0` and `0.8`?

Keep these controls fixed:

- evaluation fixture: `evals/arithmetic`;
- model provider and model identifier;
- repository revision, prompts, and repair-agent step budget;
- GitHub research: disabled; and
- Docker image and test command.

The independent variable is temperature. The observations are the tool sequence, malformed or rejected requests, number of model decisions, changed files, and final sandboxed test result.

## Run the comparison

Create a local folder for terminal logs, then run one repair at each setting. The command prints the requested temperature before the agent trace.

```bash
mkdir -p temperature-study

python main.py repair evals/arithmetic --provider ollama --model qwen2.5-coder:7b --temperature 0.0 \
  | tee temperature-study/temperature-0.0-run-1.txt

python main.py repair evals/arithmetic --provider ollama --model qwen2.5-coder:7b --temperature 0.8 \
  | tee temperature-study/temperature-0.8-run-1.txt
```

If time and model access allow, repeat each condition once or twice. A second run uses a fresh disposable workspace because the repair service always copies the original fixture before the agent edits it.

Use the equivalent command for Vertex or OpenAI after changing `--provider` and `--model`. Individual models can support a narrower range or reject sampling controls. Record that provider response rather than changing the harness. For OpenAI, consult the model's current parameter support; the [Responses API reference](https://developers.openai.com/api/reference/resources/responses/methods/create) documents temperature and notes that model support can vary.

## Record your observations

Complete a table such as this from the saved terminal logs:

| Temperature | Run | Tests passed? | Tool sequence or notable trace difference | Provider or parsing error? |
| --- | --- | --- | --- | --- |
| 0.0 | 1 |  |  |  |
| 0.8 | 1 |  |  |  |
| 0.0 | 2, if run |  |  |  |
| 0.8 | 2, if run |  |  |  |

## Interpret the result carefully

All of these outcomes are useful observations:

- Both settings may follow the same trace and pass the tests.
- The tool order, summaries, edit content, or JSON validity may differ.
- One setting may exhaust the step budget or produce a malformed request.
- A provider may reject the parameter for a particular model configuration.

Do not claim that one setting is better from two runs of one tiny fixture. State what you observed, note the controls, and identify the limitation. A stronger study would repeat each setting several times and use several evaluation fixtures.

## What to demonstrate

Show the two saved terminal logs, your observation table, and a brief conclusion. Explain why different model behaviour does not weaken the safety boundary: every run still edits a disposable copy and tests generated project code only inside Docker.
