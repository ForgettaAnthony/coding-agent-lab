"""Unit tests for the bounded repair loop using only fake tools."""

import json
from pathlib import Path

import pytest

from adapters.models.scripted import ScriptedClient
from core.models import RepairResult, TestResult
from core.repair_agent import MAX_DECISIONS, RepairAgent


WORKSPACE = Path.home() / ".cache" / "coding-agent-lab" / "fake-workspace"


class RecordingScriptedClient(ScriptedClient):
    """Scripted client that snapshots each supplied message history."""

    def __init__(self, responses: list[str]) -> None:
        super().__init__(responses)
        self.histories: list[list[dict[str, str]]] = []

    def chat(self, messages: list[dict[str, str]]) -> str:
        self.histories.append([message.copy() for message in messages])
        return super().chat(messages)


class FakeTools:
    """Small in-memory implementation of the repair tools protocol."""

    def __init__(
        self,
        test_results: list[TestResult] | None = None,
        read_failures: int = 0,
    ) -> None:
        self.test_results = list(test_results or [])
        self.read_failures = read_failures
        self.calls: list[tuple[str, ...]] = []

    def read_file(self, path: str) -> str:
        self.calls.append(("read_file", path))
        if self.read_failures:
            self.read_failures -= 1
            raise FileNotFoundError(path)
        return "value = 0\n"

    def edit_file(self, path: str, content: str) -> None:
        self.calls.append(("edit_file", path, content))

    def run_tests(self) -> TestResult:
        self.calls.append(("run_tests",))
        if not self.test_results:
            raise RuntimeError("No fake test result remains")
        return self.test_results.pop(0)


def run_agent(
    responses: list[str],
    tools: FakeTools,
    client_type: type[ScriptedClient] = ScriptedClient,
) -> tuple[RepairResult, ScriptedClient]:
    """Run one agent attempt with the standard fake case."""
    client = client_type(responses)
    result = RepairAgent(client, tools).repair(
        "sample", ["test_sample.py", "sample.py"], WORKSPACE
    )
    return result, client


def test_successful_read_fail_edit_pass_sequence() -> None:
    failing = TestResult(False, "one failed", 1)
    passing = TestResult(True, "one passed", 0)
    tools = FakeTools([failing, passing])
    responses = [
        '{"tool":"read_file","path":"sample.py","summary":"Inspect code"}',
        '{"tool":"run_tests","summary":"Reproduce failure"}',
        json.dumps(
            {
                "tool": "edit_file",
                "path": "sample.py",
                "content": "value = 1\n",
                "summary": "Apply fix",
            }
        ),
        '{"tool":"run_tests","summary":"Verify fix"}',
    ]

    result, _ = run_agent(responses, tools)

    assert result.passed is True
    assert result.last_test == passing
    assert result.changed_files == ["sample.py"]
    assert tools.calls == [
        ("read_file", "sample.py"),
        ("run_tests",),
        ("edit_file", "sample.py", "value = 1\n"),
        ("run_tests",),
    ]
    assert [entry["event"] for entry in result.trace] == [
        "repair_started",
        "model_response",
        "tool_result",
        "model_response",
        "tool_result",
        "model_response",
        "tool_result",
        "model_response",
        "tool_result",
        "repair_finished",
    ]
    assert "value = 1" not in repr(result.trace)


@pytest.mark.parametrize(
    "response",
    [
        "not json",
        '```json\n{"tool":"run_tests"}\n```',
        "[]",
        '{"tool":"run_tests"} trailing prose',
        '{"tool":"run_tests","tool":"read_file","path":"sample.py"}',
        '{"tool":"delete_file","path":"sample.py"}',
        '{"tool":"read_file"}',
        '{"tool":"run_tests","path":"sample.py"}',
    ],
)
def test_invalid_response_fails_without_calling_tools(response: str) -> None:
    tools = FakeTools()

    result, _ = run_agent([response], tools)

    assert result.passed is False
    assert tools.calls == []
    assert result.trace[-2]["event"] == "model_response"
    assert result.trace[-2]["status"] == "invalid"
    assert result.trace[-1]["event"] == "repair_finished"


def test_edit_is_rejected_until_read_and_failing_test() -> None:
    failing = TestResult(False, "one failed", 1)
    passing = TestResult(True, "one passed", 0)
    tools = FakeTools([failing, passing])
    responses = [
        '{"tool":"edit_file","path":"sample.py","content":"too early"}',
        '{"tool":"read_file","path":"sample.py"}',
        '{"tool":"run_tests"}',
        '{"tool":"edit_file","path":"sample.py","content":"fixed"}',
        '{"tool":"run_tests"}',
    ]

    result, client = run_agent(responses, tools, RecordingScriptedClient)

    assert result.passed is True
    assert [call for call in tools.calls if call[0] == "edit_file"] == [
        ("edit_file", "sample.py", "fixed")
    ]
    assert result.changed_files == ["sample.py"]
    assert isinstance(client, RecordingScriptedClient)
    assert "Policy error" in client.histories[1][-1]["content"]
    assert any(entry.get("status") == "policy_error" for entry in result.trace)


def test_decision_budget_stops_after_eight_model_calls() -> None:
    tools = FakeTools()
    responses = ['{"tool":"read_file","path":"sample.py"}'] * MAX_DECISIONS

    result, _ = run_agent(responses, tools)

    assert result.passed is False
    assert len(tools.calls) == MAX_DECISIONS
    assert result.trace[-1]["reason"] == (
        f"Decision budget exhausted after {MAX_DECISIONS} decisions."
    )


def test_passing_baseline_is_not_reported_as_a_repair() -> None:
    passing = TestResult(True, "one passed", 0)
    tools = FakeTools([passing])
    responses = [
        '{"tool":"read_file","path":"sample.py"}',
        '{"tool":"run_tests"}',
    ]

    result, _ = run_agent(responses, tools)

    assert result.passed is False
    assert result.last_test == passing
    assert result.changed_files == []
    assert "no reproducible bug" in result.trace[-1]["reason"]


def test_exhausted_script_returns_failed_repair_result() -> None:
    tools = FakeTools()

    result, _ = run_agent([], tools)

    assert isinstance(result, RepairResult)
    assert result.passed is False
    assert result.trace[-2]["status"] == "error"
    assert "Client error" in result.trace[-1]["reason"]


def test_tool_error_is_visible_and_model_can_continue() -> None:
    failing = TestResult(False, "one failed", 1)
    passing = TestResult(True, "one passed", 0)
    tools = FakeTools([failing, passing], read_failures=1)
    responses = [
        '{"tool":"read_file","path":"missing.py"}',
        '{"tool":"read_file","path":"sample.py"}',
        '{"tool":"run_tests"}',
        '{"tool":"edit_file","path":"sample.py","content":"fixed"}',
        '{"tool":"run_tests"}',
    ]

    result, client = run_agent(responses, tools, RecordingScriptedClient)

    assert result.passed is True
    assert isinstance(client, RecordingScriptedClient)
    assert "Tool error" in client.histories[1][-1]["content"]
    assert any(entry.get("status") == "error" for entry in result.trace)
