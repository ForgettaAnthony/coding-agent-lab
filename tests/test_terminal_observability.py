"""Checks for live terminal rendering of generic repair-harness events."""

from adapters.observability.terminal import TerminalTrajectoryObserver


class RecordingDelegate:
    """Capture forwarded events without relying on another observability service."""

    def __init__(self):
        """Start with no forwarded events."""
        self.events = []

    def record(self, event_name, payload):
        """Store one forwarded event exactly as the terminal observer received it."""
        self.events.append((event_name, payload))


def test_terminal_observer_prints_live_events_and_forwards_them():
    """Verify a live trace remains readable while a secondary observer receives every event."""
    lines = []
    delegate = RecordingDelegate()
    observer = TerminalTrajectoryObserver(output=lines.append, delegate=delegate)
    events = [
        ("repair_started", {"case_name": "arithmetic", "files": ["calculator.py"]}),
        ("model_response", {"step": 1, "reply": '{"tool": "read_file", "path": "calculator.py"}'}),
        ("tool_result", {
            "step": 1, "tool_name": "read_file", "summary": "Inspect the implementation",
            "observation": "def add(left, right): ...",
        }),
        ("repair_finished", {"passed": True, "summary": "All tests passed."}),
    ]
    for event_name, payload in events:
        observer.record(event_name, payload)
    rendered = "\n".join(lines)
    assert "Repair started: arithmetic" in rendered
    assert "[1] model response" in rendered
    assert "[1] read_file: Inspect the implementation" in rendered
    assert "Repair finished: PASSED" in rendered
    assert delegate.events == events
