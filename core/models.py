"""Shared data models for the repair workflow."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TestResult:
    """Result of one sandboxed test run."""

    passed: bool
    output: str
    returncode: int

    __test__ = False


@dataclass
class ModelAction:
    """One validated tool action requested by a model."""

    tool: str
    arguments: dict[str, Any]
    summary: str | None = None


@dataclass
class RepairResult:
    """Final outcome and public artifacts from a repair attempt."""

    passed: bool
    trace: list[dict[str, Any]]
    changed_files: list[str]
    workspace: Path
    last_test: TestResult | None
