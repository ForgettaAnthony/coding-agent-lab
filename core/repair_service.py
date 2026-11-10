"""Validate evaluation selections and run repairs on disposable copies."""

from collections.abc import Callable
from pathlib import Path

from core.models import RepairResult
from core.repair_agent import RepairAgent


ALLOWED_CASES = frozenset(
    {
        "arithmetic",
        "balanced_brackets",
        "median",
        "multi_function",
        "unique_words",
    }
)

WorkspaceFactory = Callable[[Path], Path]
AgentFactory = Callable[[str, Path], RepairAgent]


class RepairService:
    """Run a repair only for a supplied project beneath the evaluation root."""

    def __init__(
        self,
        evals_root: str | Path,
        workspace_factory: WorkspaceFactory,
        agent_factory: AgentFactory,
    ) -> None:
        self.evals_root = Path(evals_root).resolve(strict=True)
        if not self.evals_root.is_dir():
            raise ValueError(f"Evaluation root is not a directory: {self.evals_root}")
        self._workspace_factory = workspace_factory
        self._agent_factory = agent_factory

    def repair(self, selected_project: str | Path) -> RepairResult:
        """Validate, copy, and repair one known evaluation project."""
        selection = Path(selected_project)
        if selection.is_absolute():
            raise ValueError("Evaluation project path must be relative")

        parts = selection.parts
        if parts and parts[0] == self.evals_root.name:
            parts = parts[1:]
        if len(parts) != 1:
            raise ValueError("Expected one project as evals/<case>")

        case_name = parts[0]
        if case_name not in ALLOWED_CASES:
            raise ValueError(f"Unknown evaluation project: {case_name}")

        source = (self.evals_root / case_name).resolve(strict=True)
        if source.parent != self.evals_root or not source.is_dir():
            raise ValueError("Evaluation project must stay directly under evals")

        workspace = Path(self._workspace_factory(source)).resolve(strict=True)
        relative_files = sorted(
            path.relative_to(workspace).as_posix()
            for path in workspace.rglob("*")
            if path.is_file()
        )
        agent = self._agent_factory(case_name, workspace)
        return agent.repair(case_name, relative_files, workspace)
