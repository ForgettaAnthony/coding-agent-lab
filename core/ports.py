"""Protocols for services used by the core repair workflow."""

from typing import Any, Protocol

from core.models import TestResult


class ChatClient(Protocol):
    """Provide model responses for a message history."""

    def chat(self, messages: list[dict[str, str]]) -> str:
        """Return the next response for the supplied messages."""
        ...


class RepairToolsPort(Protocol):
    """Expose the permitted workspace repair operations."""

    def read_file(self, path: str) -> str:
        """Read a workspace-relative UTF-8 file."""
        ...

    def edit_file(self, path: str, content: str) -> None:
        """Replace a workspace-relative UTF-8 file."""
        ...

    def run_tests(self) -> TestResult:
        """Run the sandboxed project tests."""
        ...


class TraceRecorder(Protocol):
    """Record a public repair event for optional observability."""

    def record(self, event: str, payload: dict[str, Any]) -> None:
        """Record one named event and its public payload."""
        ...
