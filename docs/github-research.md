# Optional GitHub research: advanced extension

[Back to the lab guide](../README.md)

This extension lets students study how a coding agent can receive bounded Internet evidence. It is deliberately **off by default**. When enabled, `adapters/research/github_research.py` calls only GitHub's code-search API; it is not a browser and cannot fetch arbitrary URLs.

## Setup

### 1. Create a short-lived, least-privilege GitHub token

This lab searches **public GitHub code only**. Create a fine-grained personal access token; do not use a personal access token (classic).

1. Sign in to GitHub and open the [fine-grained token creation page](https://github.com/settings/personal-access-tokens/new). You can also reach it through **Profile picture → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Set **Token name** to `coding-agent-lab-research` and choose a short **Expiration**, such as the end of the lab week.
3. Under **Resource owner**, select your personal GitHub account. Do not choose an organization unless course staff has specifically arranged it.
4. Under **Repository access**, select **Public Repositories**. Do not give the token access to a private repository.
5. Leave all repository, organization, and account permissions unselected. The adapter only calls the read-only code-search endpoint; it never writes to GitHub.
6. Click **Generate token**, then copy the token immediately. GitHub shows the token value only once. Treat it like a password.

GitHub requires authentication for code search, and fine-grained tokens have read-only access to public repositories without extra permissions. See GitHub's [fine-grained token guide](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) and [code-search API documentation](https://docs.github.com/en/rest/search/search#search-code).

### 2. Enable research for one terminal session

**macOS/Linux**

```bash
export GITHUB_TOKEN="paste-the-token-here"
python main.py repair evals/multi_function --research
```

**Windows PowerShell**

```powershell
$env:GITHUB_TOKEN = "paste-the-token-here"
python main.py repair evals/multi_function --research
```

The variable lasts only for the current terminal session. Never place the token in source code, a notebook, a prompt, or a file committed to Git.

For the Gradio interface, set `ENABLE_GITHUB_RESEARCH=true` before starting the UI:

**macOS/Linux**

```bash
export GITHUB_TOKEN="paste-the-token-here"
export ENABLE_GITHUB_RESEARCH=true
python main.py ui
```

**Windows PowerShell**

```powershell
$env:GITHUB_TOKEN = "paste-the-token-here"
$env:ENABLE_GITHUB_RESEARCH = "true"
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
