"""Tests for the optional Langfuse observability adapter without credentials or a network call."""

from adapters.observability.langfuse import LangfuseTrajectoryObserver


class FakeObservation:
    """Minimal in-memory representation of one Langfuse observation."""

    def __init__(self, **attributes):
        """Store the observation attributes, child observations, and lifecycle state."""
        self.attributes = attributes
        self.children = []
        self.output = None
        self.ended = False

    def start_observation(self, **attributes):
        """Create and retain a child observation for this in-memory tree."""
        child = FakeObservation(**attributes)
        self.children.append(child)
        return child

    def update(self, **attributes):
        """Store terminal output as the real SDK observation would."""
        self.output = attributes["output"]

    def end(self):
        """Mark this observation as completed."""
        self.ended = True


class FakeLangfuseClient:
    """Provide the small subset of Langfuse used by this adapter."""

    def __init__(self):
        """Start with no root observation and no flush requests."""
        self.root = None
        self.flushes = 0

    def start_observation(self, **attributes):
        """Create the root observation for a repair trajectory."""
        self.root = FakeObservation(**attributes)
        return self.root

    def flush(self):
        """Record that terminal observations were delivered."""
        self.flushes += 1


def test_langfuse_adapter_records_a_harness_trajectory():
    """Verify generic lifecycle events become one root and child observation tree."""
    client = FakeLangfuseClient()
    observer = LangfuseTrajectoryObserver(client)
    observer.record("repair_started", {"case_name": "arithmetic", "files": ["calculator.py"]})
    observer.record("model_response", {"step": 1, "reply": '{"tool": "read_file"}'})
    observer.record("tool_result", {
        "step": 1, "tool_name": "read_file", "action": {"path": "calculator.py"}, "observation": "...",
    })
    observer.record("repair_finished", {"passed": True, "summary": "All tests passed."})
    assert client.root.attributes["as_type"] == "agent"
    assert [child.attributes["as_type"] for child in client.root.children] == ["generation", "tool"]
    assert client.root.output["passed"] is True
    assert client.root.ended is True
    assert client.flushes == 1
