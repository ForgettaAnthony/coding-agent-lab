<h1 align="center">Build Your Own Python Repair Agent</h1>

<p align="center">
  <img src="docs/assets/python-repair-agent-icon.png" width="180" alt="A repair agent fixes a code bug and verifies the repair">
</p>

## A guided, from-scratch activity

In this activity, you will build a small Python repair agent with a vibe-coding assistant such as Codex, Claude Code, or Cursor. The agent receives one buggy Python project and its tests. It must inspect the project, reproduce the failure by testing it, make a focused edit, and verify the repair in a Docker sandbox.

The final output is a visible action trace, a disposable repaired copy of the project, and the final test result. You are not given agent source code to complete. You will create the folders, files, tests, and implementation yourself. Your coding assistant may write code, but you are responsible for directing it, reviewing its changes, and running every checkpoint.

## Objective

Build a repair agent that:

- works only on one instructor-provided project selected from `evals/`;
- reproduces a failing test before it edits code;
- runs project code only inside Docker;
- accepts only a small, explicit set of model actions;
- stops when tests pass, the model response is invalid, or its decision budget ends; and
- can run from a terminal and a small web interface.

## Repair workflow at a glance

The agent works on a copy, never directly on `evals/`. The model proposes one action at a time; the surrounding Python program supplies the case context, limits the available actions, records the observations, and decides when to stop.

```mermaid
flowchart LR
    select["1. Select an eval project"] --> copy["2. Copy it to a workspace"]
    copy --> inspect["3. Read the test and source code"]
    inspect --> reproduce["4. Run tests in Docker"]
    reproduce -->|Tests fail| edit["5. Edit the workspace copy"]
    edit --> verify["6. Run tests in Docker again"]
    verify -->|Tests still fail| inspect
    verify -->|Tests pass| result["7. Return trace, changed files, and result"]
```

Follow this evidence order:

1. 🟦 **Inspect local code.** Read the relevant test and source files in the copied workspace.
2. 🟨 **Reproduce the bug.** Run a sandboxed test and observe a failing result before editing.
3. 🟧 **Make one focused edit.** Change only the copied workspace file needed to address the observed failure.
4. 🟩 **Verify the repair.** Run a later sandboxed test and accept the repair only if it passes.

**Sandboxed test** means `pytest` runs inside a short-lived Docker container with networking disabled. It receives only the disposable workspace copy, not the original `evals/` project or the rest of the host computer.

If the model sends an invalid action or the decision budget ends, the agent stops and reports the failure instead of guessing.

## Before you begin

Have the following ready before the activity:

- A GitHub account, Git, and permission to fork and push to your own repository.
- Python 3.11 or newer.
- Docker Desktop installed. Start it before the sandbox task; `docker info` must succeed.
- A code editor and one vibe-coding assistant, such as Codex, Claude Code, or Cursor.
- A browser and Internet connection to fork the repository and install Python packages.

Check your local tools before class:

```bash
git --version
python3 --version       # macOS or Linux
docker info
```

In Windows PowerShell, use `py --version` instead of `python3 --version`.

You do **not** need Ollama, a large local model, a cloud-model account, or an API key for the required build and scripted checkpoints. They are needed only for the optional live-model task.

## Optional providers and observability

The supplied `requirements.txt` installs the Python libraries for the required activity, OpenAI, Vertex AI, and Langfuse. Installing a library does not enable its service. Choose at most one model provider for a live demonstration; Langfuse is optional trace recording.

| Optional capability | Additional setup |
| --- | --- |
| OpenAI model adapter | Create an API key and set `OPENAI_API_KEY` in your terminal. Follow the [official Python SDK guide](https://developers.openai.com/api/docs/libraries?language=python). |
| Google Vertex AI model adapter | Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install), run `gcloud init`, then run `gcloud auth application-default login`. Use a Google Cloud project with Vertex AI enabled. |
| Langfuse Cloud trace recording | Create your own Langfuse Cloud project and set its public and secret keys in your terminal. See the [Langfuse Python SDK guide](https://langfuse.com/docs/observability/sdk/overview). |

Keep credentials out of the repository. These additions do not change the sandbox rule: the model client and observability code run on the host, while evaluation-project code runs only in Docker.

## Current repository structure

The starter provides this guide, task handouts, `LICENSE`, `.gitignore`, the repair-agent icon, `requirements.txt`, and five fixed evaluation projects. It must not contain an implemented agent, hidden tests, model keys, or a completed Docker runner. Keep the working implementation in the instructor repository only.

The supplied evaluation projects are:

```text
evals/
├── arithmetic/          # small calculator bug
├── balanced_brackets/   # matching-type boundary bug
├── median/              # even-length boundary bug
├── multi_function/      # several text utility functions
└── unique_words/        # order-preservation bug
```

Do not edit files in `evals/`. Your repair agent must copy the selected project into a disposable workspace before it changes anything. The cases are teaching-sized fixtures, not HumanEval+ tasks. They follow the same useful evaluation habit: test ordinary behavior and a boundary or semantic case that a superficial repair can miss.

## How to use a vibe-coding assistant

Work in short tasks. For each task:

1. Give the assistant only the stated task and files.
2. Ask it to run the stated checkpoint.
3. Read the diff before accepting it.
4. Run the checkpoint yourself.
5. Commit the working task.

Use this prompt pattern whenever you ask for help:

```text
You are helping me build a teaching-sized Python repair agent.

Read the named files before changing anything. Work only on the files listed
in this task. Keep the repair decision code separate from Docker, model HTTP,
and Gradio code. Do not add a host shell, arbitrary project upload, Internet
search, API keys, or packages beyond those requested.

Task: <paste the task for this stage>

Verification: run <paste the command>. Report the actual result and every
file changed. Do not claim success if the command fails.
```

Treat the assistant's output as a proposed change, not proof that the code is correct.

## Safety rules

These rules are requirements, not suggestions.

- The agent may work only on a copied project selected from `evals/`.
- Never execute evaluation-project Python with host Python.
- The host may start Docker, but Docker alone runs `pytest` and generated project code.
- Do not give the model a free-form shell tool.
- Do not provide arbitrary file paths, public uploads, or Internet access in the required activity.
- Reject absolute paths and paths that escape the workspace, such as `../secret.txt`.
- Do not put model or service secrets in source files, commits, or traces.
- Require a failing sandboxed test result before allowing an edit.
- Keep a short public action summary, not private model reasoning.

## A map of the files you will build

Do not try to understand or implement this whole tree now. It is a map for the activity. Each task tells you which small group of files to create next and what to check before moving on. The small `__init__.py` files simply tell Python that a folder can be imported as a package.

```text
coding-agent-lab/
├── README.md                          # this guide
├── requirements.txt                   # supplied Python dependencies
├── tasks/                             # supplied task handouts
│   ├── 00-setup.md
│   ├── 01-core-vocabulary.md
│   ├── 02-sandbox-tools.md
│   ├── 03-prompts-and-clients.md
│   ├── 04-repair-loop.md
│   ├── 05-cli-repair.md
│   ├── 06-gradio-ui.md
│   ├── 07-live-ollama.md
│   └── 08-final-demonstration.md
├── pytest.ini                         # you create this
├── main.py                            # you create this
├── bootstrap.py                       # you create this
├── core/                              # you create this folder
│   ├── __init__.py
│   ├── models.py
│   ├── ports.py
│   ├── prompts.py
│   ├── repair_agent.py
│   └── repair_service.py
├── adapters/                          # you create this folder
│   ├── __init__.py
│   ├── gradio_ui.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ollama.py
│   │   └── scripted.py
│   └── sandbox/
│       ├── __init__.py
│       ├── Dockerfile
│       ├── runner.py
│       └── repair_tools.py
├── evals/                             # supplied, never modified
│   ├── arithmetic/
│   ├── balanced_brackets/
│   ├── median/
│   ├── multi_function/
│   └── unique_words/
└── tests/                             # you create this folder
    ├── test_tools.py
    └── test_agent.py
```

### What each file will do

| File | Concrete responsibility |
| --- | --- |
| `README.md` | Gives you the overview, workflow, safety rules, and task links. |
| `requirements.txt` | Installs the Python libraries used by the lab. It is supplied. |
| `tasks/*.md` | Gives the exact instructions, prompt, and checkpoint for one task. They are supplied. |
| `pytest.ini` | Restricts host `pytest` to your `tests/` folder, so host Python never runs files in `evals/`. |
| `main.py` | Accepts `repair` and `ui` commands, starts the selected workflow, and prints the visible trace. |
| `bootstrap.py` | Creates the real model client, Docker-backed tools, and repair service, then connects them. |
| `core/__init__.py` | Marks `core/` as an importable package. |
| `core/models.py` | Defines small result objects, including test results, model actions, and the final repair result. |
| `core/ports.py` | Describes the small capabilities the repair agent needs: chat, file tools, tests, and optional trace recording. |
| `core/prompts.py` | Holds the system and user messages, JSON action rules, and tool-result formatting. |
| `core/repair_agent.py` | Runs the bounded repair loop: ask the model, validate one action, call one permitted tool, store the observation, and stop safely. |
| `core/repair_service.py` | Selects an allowed evaluation project, creates its disposable workspace, and returns the agent result. |

| File | Concrete responsibility |
| --- | --- |
| `adapters/__init__.py` | Marks `adapters/` as an importable package. |
| `adapters/gradio_ui.py` | Presents the existing repair service in a page with project selection, trace, changed code, test output, and a ZIP download. |
| `adapters/models/__init__.py` | Marks the model-adapter folder as importable. |
| `adapters/models/ollama.py` | Sends messages to local Ollama and returns the model's text response. |
| `adapters/models/scripted.py` | Returns predetermined model replies so your repair-loop tests are repeatable without an LLM. |
| `adapters/sandbox/__init__.py` | Marks the sandbox folder as importable. |
| `adapters/sandbox/Dockerfile` | Defines the small non-root Docker image that can run pytest. |
| `adapters/sandbox/runner.py` | Copies a chosen evaluation project and starts the restricted Docker test command against that copy. |
| `adapters/sandbox/repair_tools.py` | Implements safe `read_file`, `edit_file`, and `run_tests` operations inside the copied workspace. |

| File or folder | Concrete responsibility |
| --- | --- |
| `evals/<case>/` | Supplied buggy source file and pytest file. The agent can read a copied case but must never modify the original. |
| `tests/test_tools.py` | Proves safe path handling, file edits, and test-runner delegation. |
| `tests/test_agent.py` | Proves the repair loop with `ScriptedClient`, including invalid JSON and stopping rules. |

One practical rule will keep the project understandable: files in `core/` must not import files from `adapters/`. `bootstrap.py` is the one place that selects the real model, sandbox, and UI pieces and connects them to the repair service.

## Build tasks

Complete the tasks in this order. Task 7 is optional; Task 8 can use the scripted repair if a live model is unavailable.

1. [Task 0: Set up the repository and environment, 10 minutes](tasks/00-setup.md)
2. [Task 1: Define the agent's small vocabulary, 15 minutes](tasks/01-core-vocabulary.md)
3. [Task 2: Build the safe workspace and tools, 25 minutes](tasks/02-sandbox-tools.md)
4. [Task 3: Prepare prompts and a test model, 15 minutes](tasks/03-prompts-and-clients.md)
5. [Task 4: Build the repair loop, 40 minutes](tasks/04-repair-loop.md)
6. [Task 5: Assemble the command-line repair, 15 minutes](tasks/05-cli-repair.md)
7. [Task 6: Add the Gradio interface, 20 minutes](tasks/06-gradio-ui.md)
8. [Task 7: Run a live Ollama repair, 10 minutes, optional](tasks/07-live-ollama.md)
9. [Task 8: Final demonstration](tasks/08-final-demonstration.md)
