import json
from pathlib import Path

from core.repair_agent import RepairAgent
from adapters.sandbox.runner import create_workspace
from adapters.sandbox.repair_tools import RepairTools


class ScriptedClient:
    """Deterministic stand-in for Ollama: one response per chat call."""
    def __init__(self, responses):
        """Store deterministic model replies and an observable message history."""
        self.responses = iter(responses)
        self.messages_seen = []

    def chat(self, messages):
        """Record one conversation state and return the next scripted reply."""
        self.messages_seen.append(list(messages))
        return next(self.responses)


class FakeGitHubResearch:
    """Deterministic replacement for the external GitHub research adapter."""

    def search_code(self, query):
        """Return one citable source without making a network request."""
        return {"ok": True, "query": query, "sources": [{"url": "https://github.com/example/project"}]}


class RecordingObserver:
    """Capture generic trajectory events without using an external observability service."""

    def __init__(self):
        """Start with no captured lifecycle events."""
        self.events = []

    def record(self, event_name, payload):
        """Store one event exactly as the harness supplied it."""
        self.events.append((event_name, payload))


def test_agent_repairs_arithmetic_case_with_scripted_client(monkeypatch):
    """Verify the harness repairs a fixture through its model/tool loop."""
    # The agent loop is deterministic and does not execute generated project code on the host.
    test_results = iter([
        {"passed": False, "output": "1 failed: add returns subtraction", "returncode": 1},
        {"passed": True, "output": "2 passed (sandbox runner mocked in unit test)", "returncode": 0},
    ])
    monkeypatch.setattr("adapters.sandbox.repair_tools.run_pytest", lambda workspace: next(test_results))
    client = ScriptedClient([
        json.dumps({"summary": "Read the failing test first", "tool": "read_file", "path": "test_calculator.py"}),
        json.dumps({"summary": "Reproduce the reported failure", "tool": "run_tests"}),
        json.dumps({"tool": "edit_file", "path": "calculator.py", "content": "def add(left, right):\n    return left + right\n"}),
        json.dumps({"tool": "run_tests"}),
    ])
    workspace = create_workspace("arithmetic")
    observer = RecordingObserver()
    agent = RepairAgent(client=client, max_steps=5, observer=observer)
    result = agent.run("arithmetic", ["calculator.py", "test_calculator.py"], RepairTools(workspace))
    assert result.passed is True
    assert result.changed_files == ["calculator.py"]
    assert "2 passed" in result.test_result["output"]
    assert len(client.messages_seen) == 4
    assert any("TOOL_RESULT" in message["content"] for message in client.messages_seen[-1] if message["role"] == "user")
    assert "Read the failing test first" in result.trace[0]
    assert "1 failed" in result.trace[1]
    assert [event[0] for event in observer.events] == [
        "repair_started", "model_response", "tool_result", "model_response", "tool_result",
        "model_response", "tool_result", "model_response", "tool_result", "repair_finished",
    ]


def test_agent_can_use_the_restricted_inspection_command(monkeypatch, tmp_path):
    """Verify the harness dispatches the supplied sandbox inspection capability."""
    monkeypatch.setattr("adapters.sandbox.repair_tools.run_command", lambda workspace, command: {
        "ok": True, "output": "./package/module.py", "returncode": 0
    })
    monkeypatch.setattr("adapters.sandbox.repair_tools.run_pytest", lambda workspace: {
        "passed": True, "output": "1 passed", "returncode": 0
    })
    client = ScriptedClient([
        json.dumps({"tool": "run_command", "command": "find . -maxdepth 2 -type f"}),
        json.dumps({"tool": "run_tests"}),
    ])
    result = RepairAgent(client=client, max_steps=3).run("anything", [], RepairTools(tmp_path))
    assert result.passed is True
    assert any("run_command" in line for line in result.trace)


def test_agent_can_request_opt_in_github_research(monkeypatch, tmp_path):
    """Verify opt-in research reaches the harness as an observable tool result."""
    (tmp_path / "context.py").write_text("def normalize_name(value):\n    return value\n")
    monkeypatch.setattr("adapters.sandbox.repair_tools.run_pytest", lambda workspace: {
        "passed": True, "output": "1 passed", "returncode": 0
    })
    client = ScriptedClient([
        json.dumps({"tool": "read_file", "path": "context.py"}),
        json.dumps({"tool": "search_github", "query": "normalize_name language:Python"}),
        json.dumps({"tool": "run_tests"}),
    ])
    result = RepairAgent(client=client, max_steps=4, research_enabled=True).run(
        "anything", [], RepairTools(tmp_path, FakeGitHubResearch())
    )
    assert result.passed is True
    assert any("github.com/example/project" in line for line in result.trace)
    assert "GitHub research is enabled" in client.messages_seen[0][0]["content"]


def test_agent_blocks_github_research_before_local_read(monkeypatch, tmp_path):
    """Verify the harness returns a policy observation before premature research."""
    monkeypatch.setattr("adapters.sandbox.repair_tools.run_pytest", lambda workspace: {
        "passed": True, "output": "1 passed", "returncode": 0
    })
    client = ScriptedClient([
        json.dumps({"tool": "search_github", "query": "normalize_name language:Python"}),
        json.dumps({"tool": "run_tests"}),
    ])
    result = RepairAgent(client=client, max_steps=3, research_enabled=True).run(
        "anything", [], RepairTools(tmp_path)
    )
    assert result.passed is True
    assert "Read a local file before using GitHub research." in result.trace[0]


def test_agent_stops_at_budget_without_running_host_code(monkeypatch, tmp_path):
    """Verify an unfinished loop stops at its fixed decision budget."""
    client = ScriptedClient([json.dumps({"tool": "read_file", "path": "x.py"})] * 4)
    (tmp_path / "x.py").write_text("x = 1\n")
    result = RepairAgent(client=client, max_steps=2).run("anything", ["x.py"], RepairTools(tmp_path))
    assert result.passed is False
    assert "budget" in result.summary.lower()


def test_agent_rejects_an_action_outside_the_json_contract(tmp_path):
    """Verify an invalid action cannot reach a repair tool or continue the loop."""
    client = ScriptedClient([json.dumps({"tool": "run_tests", "unexpected": True})])
    result = RepairAgent(client=client).run("anything", [], RepairTools(tmp_path))
    assert result.passed is False
    assert "JSON action contract" in result.summary
    assert "rejected_model_response" in result.trace[0]
