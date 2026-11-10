"""Safe file and test operations for a disposable repair workspace."""

from collections.abc import Callable
from pathlib import Path

from adapters.sandbox import runner
from core.models import TestResult


def safe_path(workspace: str | Path, requested_path: str | Path) -> Path:
    """Resolve a relative path and reject paths outside the workspace."""
    workspace_path = Path(workspace).expanduser().resolve()
    requested = Path(requested_path)
    if requested.is_absolute():
        raise ValueError("Absolute paths are not allowed")

    resolved = (workspace_path / requested).resolve()
    if resolved != workspace_path and workspace_path not in resolved.parents:
        raise ValueError("Path escapes the workspace")
    return resolved


class RepairTools:
    """Provide the three permitted operations within one workspace."""

    def __init__(
        self,
        workspace: str | Path,
        test_runner: Callable[[Path], TestResult] | None = None,
    ) -> None:
        self.workspace = Path(workspace).expanduser().resolve(strict=True)
        if not self.workspace.is_dir():
            raise ValueError(f"Workspace is not a directory: {self.workspace}")
        self.changed_files: list[str] = []
        self._test_runner = test_runner or runner.run_tests

    def read_file(self, path: str) -> str:
        """Read one UTF-8 file from the workspace."""
        return safe_path(self.workspace, path).read_text(encoding="utf-8")

    def edit_file(self, path: str, content: str) -> None:
        """Write one UTF-8 file and record its relative path once."""
        destination = safe_path(self.workspace, path)
        destination.write_text(content, encoding="utf-8")
        relative_path = destination.relative_to(self.workspace).as_posix()
        if relative_path not in self.changed_files:
            self.changed_files.append(relative_path)

    def run_tests(self) -> TestResult:
        """Delegate testing of this workspace to the Docker runner."""
        return self._test_runner(self.workspace)
