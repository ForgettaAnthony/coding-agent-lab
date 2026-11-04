"""Port contracts owned by the repair-agent policy (Ports & Adapters terminology)."""

from collections.abc import Callable
from pathlib import Path
from typing import Protocol



class ChatModelPort(Protocol):
    """Driven port: any LLM adapter may satisfy this contract."""
    def chat(self, messages: list[dict]) -> str:
        """Return the model's next text response for a conversation."""
        ...


class RepairToolsPort(Protocol):
    """Bounded capabilities that the repair harness may request."""
    changed_files: list[str]

    def read_file(self, path: str) -> str:
        """Return text from one workspace-relative file."""
        ...

    def edit_file(self, path: str, content: str) -> str:
        """Write one workspace-relative file and report the change."""
        ...

    def run_tests(self) -> dict:
        """Run the supplied project tests inside the sandbox."""
        ...

    def run_command(self, command: str) -> dict:
        """Run one policy-approved repository-inspection command."""
        ...

    def search_github(self, query: str) -> dict:
        """Return bounded, citable GitHub research evidence when enabled."""
        ...


class TrajectoryObserverPort(Protocol):
    """Optional, best-effort sink for the harness's observable lifecycle events."""

    def record(self, event_name: str, payload: dict) -> None:
        """Record one named, JSON-serializable repair-trajectory event."""
        ...


WorkspaceFactory = Callable[[str], Path]
ToolsFactory = Callable[[Path], RepairToolsPort]
