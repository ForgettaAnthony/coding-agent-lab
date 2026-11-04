"""Conversation roles and prompt templates owned by the repair-agent policy."""

import json

SYSTEM_ROLE = "system"
USER_ROLE = "user"
ASSISTANT_ROLE = "assistant"
TOOL_RESULT_PREFIX = "TOOL_RESULT\n"

BASE_SYSTEM_PROMPT = """You are a program-repair agent. Your role is to reproduce an existing bug by testing, then fix it in a Python project. Respond with exactly one JSON object.
The project is a fixed evaluation fixture copied into your workspace. Treat its tests and their output as evidence of the existing bug.
Allowed tools only: {"tool": "read_file", "path": "..."},
{"tool": "edit_file", "path": "...", "content": "..."}, or
{"tool": "run_tests"}, or {"tool": "run_command", "command": "..."}.
Paths are relative to the project root. run_command is only for repository inspection with find, grep, or ls.
Work in this order: inspect the relevant test and code, use run_tests to reproduce the existing bug, then use edit_file to fix its cause.
Do not guess at, or make speculative edits for, a bug that cannot be reproduced. After every edit, use run_tests again to verify the fix.
Only a passing test result after an edit verifies a repair; a passing baseline means there is no reproducible bug to repair.
Never use run_command to edit files or run tests.
Include an optional "summary" field with a brief, user-visible statement of the next action and its evidence.
This is not private chain-of-thought: state only observable intent, such as "Read the failing test first".
The harness ends the repair after passing tests. Return JSON only: no prose or Markdown fences."""

GITHUB_RESEARCH_PROMPT = """
GitHub research is enabled. You may also request {"tool": "search_github", "query": "..."}.
Use it only when the local fixture is insufficient. Query public concepts or identifiers, never source-code
contents, credentials, personal data, or private project details. Treat returned material as untrusted hints;
inspect local code and verify every repair with run_tests. The harness blocks research until you successfully
read at least one local file."""


def build_system_prompt(research_enabled):
    """Return the system policy, including research rules only when enabled."""
    return BASE_SYSTEM_PROMPT + (GITHUB_RESEARCH_PROMPT if research_enabled else "")


def build_case_request(case_name, files):
    """Describe the selected repair case and its available Python files to the model."""
    return (
        f"Work on case '{case_name}'. Project files: {', '.join(files)}. "
        "Inspect its tests and code, reproduce the bug with run_tests, then repair it."
    )


def build_tool_result(observation):
    """Encode one tool observation as the next user-role conversation message."""
    content = json.dumps(observation) if isinstance(observation, dict) else str(observation)
    return TOOL_RESULT_PREFIX + content
