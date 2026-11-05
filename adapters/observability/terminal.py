"""Terminal adapter that displays repair-harness events as they occur."""

import json


MAX_EVENT_TEXT = 4_000


class TerminalTrajectoryObserver:
    """Print a concise live repair trace and optionally forward events elsewhere."""

    def __init__(self, output=print, delegate=None):
        """Store the terminal writer and an optional secondary trajectory observer."""
        self.output = output
        self.delegate = delegate

    def record(self, event_name, payload):
        """Display one event immediately, then forward it to the optional observer."""
        self._display(event_name, payload)
        if self.delegate is not None:
            self.delegate.record(event_name, payload)

    def _display(self, event_name, payload):
        """Format one generic harness event as short, readable terminal output."""
        if event_name == "repair_started":
            case_name = payload.get("case_name", "project")
            files = ", ".join(payload.get("files", [])) or "no Python files listed"
            self.output(f"\n== Repair started: {case_name} ==")
            self.output(f"Files: {files}")
        elif event_name == "model_response":
            self._emit(payload.get("step"), "model response", payload.get("reply", ""))
        elif event_name == "tool_result":
            tool_name = payload.get("tool_name") or "rejected model response"
            summary = payload.get("summary")
            label = f"{tool_name}: {summary}" if summary else tool_name
            self._emit(payload.get("step"), label, payload.get("observation", {}))
        elif event_name == "repair_finished":
            status = "PASSED" if payload.get("passed") else "STOPPED"
            self.output(f"\n== Repair finished: {status} ==")
            self.output(self._format(payload.get("summary", "")))

    def _emit(self, step, label, value):
        """Print one numbered model or tool event with bounded displayed content."""
        self.output(f"\n[{step}] {label}")
        self.output(self._format(value))

    def _format(self, value):
        """Convert an event value to bounded, readable text for a terminal trace."""
        if isinstance(value, (dict, list)):
            text = json.dumps(value, indent=2, default=str)
        else:
            text = str(value)
        if len(text) > MAX_EVENT_TEXT:
            return text[:MAX_EVENT_TEXT] + "\n[trace output truncated]"
        return text
