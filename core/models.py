from dataclasses import dataclass


@dataclass
class RepairResult:
    """The stable result returned to both CLI and UI adapters."""
    passed: bool
    summary: str
    workspace: str
    trace: list[str]
    changed_files: list[str]
    test_result: dict
