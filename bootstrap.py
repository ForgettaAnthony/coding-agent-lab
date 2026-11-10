"""Application assembly for the repair-agent command line."""

import json
from pathlib import Path
from typing import Any

from adapters.models.ollama import OllamaClient
from adapters.models.scripted import ScriptedClient
from adapters.sandbox import runner
from adapters.sandbox.repair_tools import RepairTools
from core.ports import TraceRecorder
from core.repair_agent import RepairAgent
from core.repair_service import RepairService


PROJECT_ROOT = Path(__file__).resolve().parent
SUPPORTED_PROVIDERS = ("scripted", "ollama")

SCRIPTED_REPAIRS: dict[str, dict[str, Any]] = {
    "arithmetic": {
        "path": "calculator.py",
        "content": '''def add(left, right):
    """Return the sum of two numbers."""
    return left + right
''',
    },
    "balanced_brackets": {
        "path": "brackets.py",
        "content": '''def is_balanced(text):
    """Return whether parentheses, brackets, and braces are properly nested."""
    opening = "([{"
    closing = ")]}"
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []

    for character in text:
        if character in opening:
            stack.append(character)
        elif character in closing:
            if not stack or stack[-1] != pairs[character]:
                return False
            stack.pop()

    return not stack
''',
    },
    "median": {
        "path": "statistics_tools.py",
        "content": '''def median(values):
    """Return the median value without changing the input sequence."""
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
''',
    },
    "multi_function": {
        "path": "text_tools.py",
        "content": '''def normalize_name(name):
    """Trim surrounding whitespace and lowercase a supplied name."""
    return name.strip().lower()


def greeting(name):
    """Create a greeting from a normalized name."""
    return f"Hello, {normalize_name(name).title()}!"


def initials(name):
    """Return uppercase initials for the whitespace-separated parts of a name."""
    return "".join(part[0].upper() for part in name.split())
''',
    },
    "unique_words": {
        "path": "word_tools.py",
        "content": '''def unique_words(text):
    """Return lowercase words once, in the order first seen."""
    return list(dict.fromkeys(text.lower().split()))
''',
    },
}


def _scripted_responses(case_name: str) -> list[str]:
    """Build the deterministic answer cards for one supplied case."""
    try:
        repair = SCRIPTED_REPAIRS[case_name]
    except KeyError as error:
        raise ValueError(f"No scripted repair for case: {case_name}") from error

    path = repair["path"]
    return [
        json.dumps(
            {"tool": "read_file", "path": path, "summary": "Inspect code"}
        ),
        json.dumps({"tool": "run_tests", "summary": "Reproduce failure"}),
        json.dumps(
            {
                "tool": "edit_file",
                "path": path,
                "content": repair["content"],
                "summary": "Apply focused fix",
            }
        ),
        json.dumps({"tool": "run_tests", "summary": "Verify repair"}),
    ]


def create_repair_service(
    provider: str = "scripted",
    model: str | None = None,
    temperature: float = 0.0,
    recorder: TraceRecorder | None = None,
) -> RepairService:
    """Connect the selected client, Docker tools, agent, and service."""
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}")

    def agent_factory(case_name: str, workspace: Path) -> RepairAgent:
        if provider == "scripted":
            client = ScriptedClient(_scripted_responses(case_name))
        else:
            client = OllamaClient(model=model, temperature=temperature)
        tools = RepairTools(workspace)
        return RepairAgent(client, tools, recorder=recorder)

    return RepairService(
        evals_root=PROJECT_ROOT / "evals",
        workspace_factory=runner.create_workspace,
        agent_factory=agent_factory,
    )
