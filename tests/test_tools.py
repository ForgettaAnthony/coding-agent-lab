"""Focused tests for safe workspace repair tools."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from adapters.sandbox.repair_tools import RepairTools, safe_path
from core.models import TestResult


def test_read_file_reads_workspace_file(tmp_path: Path) -> None:
    project_file = tmp_path / "calculator.py"
    project_file.write_text("answer = 42\n", encoding="utf-8")

    tools = RepairTools(tmp_path)

    assert tools.read_file("calculator.py") == "answer = 42\n"


@pytest.mark.parametrize("requested_path", ["../outside.py", "../../outside.py"])
def test_safe_path_rejects_parent_traversal(
    tmp_path: Path, requested_path: str
) -> None:
    with pytest.raises(ValueError, match="escapes"):
        safe_path(tmp_path, requested_path)


def test_safe_path_rejects_absolute_path(tmp_path: Path) -> None:
    absolute_path = (tmp_path.parent / "outside.py").resolve()

    with pytest.raises(ValueError, match="Absolute"):
        safe_path(tmp_path, absolute_path)


def test_edit_file_saves_content_and_records_path_once(tmp_path: Path) -> None:
    project_file = tmp_path / "calculator.py"
    project_file.write_text("answer = 0\n", encoding="utf-8")
    tools = RepairTools(tmp_path)

    tools.edit_file("calculator.py", "answer = 41\n")
    tools.edit_file("./calculator.py", "answer = 42\n")

    assert project_file.read_text(encoding="utf-8") == "answer = 42\n"
    assert tools.changed_files == ["calculator.py"]


def test_run_tests_delegates_to_runner(tmp_path: Path) -> None:
    expected = TestResult(passed=False, output="one failed", returncode=1)
    test_runner = Mock(return_value=expected)
    tools = RepairTools(tmp_path, test_runner=test_runner)

    result = tools.run_tests()

    assert result is expected
    test_runner.assert_called_once_with(tmp_path.resolve())
