# Optional GitHub research: advanced extension

[Back to the lab guide](../README.md)

This extension lets students study how a coding agent can receive bounded Internet evidence. It is deliberately **off by default**. When enabled, `adapters/research/github_research.py` calls only GitHub's code-search API; it is not a browser and cannot fetch arbitrary URLs.

## Setup

```bash
export GITHUB_TOKEN="your-fine-grained-token"
python main.py repair evals/multi_function --research
```

For the Gradio interface, set `ENABLE_GITHUB_RESEARCH=true` before starting the UI:

```bash
export ENABLE_GITHUB_RESEARCH=true
python main.py ui
```

## Capability and policy

`--research` creates the adapter in `bootstrap.py`, sets `research_enabled=True` on the harness, and gives the model one extra request shape:

```json
{"tool":"search_github","query":"normalize_name language:Python"}
```

The adapter permits at most three requests per repair, three results per request, a one-line query of at most 180 characters, and one trusted API domain: `api.github.com`.

The harness rejects `search_github` until the model has successfully called `read_file` on a local file. Every `TOOL_RESULT` includes visible provenance: repository, path, GitHub URL, short matching snippet, retrieval time, and whether GitHub marked the response incomplete.

The model must still inspect the local project and use `run_tests`; Internet material is an untrusted hint, not a repair verdict.

## Token and privacy rules

GitHub code search has its own authentication and rate limits, so this lab requires `GITHUB_TOKEN` when research is enabled. Keep the token in an environment variable, not in the repository or model prompt. [GitHub Search API documentation](https://docs.github.com/en/rest/search/search#search-code)

Do not enable this option for a repository containing credentials, personal data, proprietary code, or other confidential material. The adapter itself cannot read project files, but an LLM that has read project context could place information into a research query. The supplied evaluation fixtures are safe for the demonstration.

For any repair, state the policy explicitly: **offline fixture evidence is sufficient**, or **external, cited documentation is needed**. The harness, not the model, enforces that policy.
