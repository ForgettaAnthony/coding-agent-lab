"""Tests for selecting only instructor-provided projects from evals/."""

from pathlib import Path

import pytest

from adapters.sandbox.repair_tools import RepairTools
from adapters.sandbox.runner import create_workspace, list_eval_projects
from core.models import RepairResult
from core.repair_service import RepairService


class CapturingAgent:
    """Deterministic agent double that records the project passed by the use case."""

    def __init__(self):
        """Start without an observed project or file list."""
        self.project_name = None
        self.files = None

    def run(self, project_name, files, tools):
        """Capture repair inputs and return a safe result without running generated code."""
        self.project_name = project_name
        self.files = files
        return RepairResult(False, "Captured project.", "", [], tools.changed_files, {
            "passed": False, "output": "Tests were not run.", "returncode": None,
        })


def test_repair_service_accepts_one_evals_project_path():
    """Verify an evals-relative path becomes one isolated repair workspace."""
    agent = CapturingAgent()
    service = RepairService(agent, create_workspace, RepairTools)
    result = service.repair("evals/arithmetic")
    workspace = Path(result.workspace)
    assert agent.project_name == "arithmetic"
    assert agent.files == ["calculator.py", "test_calculator.py"]
    assert workspace.is_dir()
    assert workspace != Path("evals/arithmetic").resolve()


def test_workspace_rejects_any_project_outside_evals():
    """Verify traversal and the evals root itself cannot become repair projects."""
    assert list_eval_projects() == ["arithmetic", "multi_function"]
    with pytest.raises(ValueError, match="direct directory under evals"):
        create_workspace("../")
    with pytest.raises(ValueError, match="direct directory under evals"):
        create_workspace("evals")
