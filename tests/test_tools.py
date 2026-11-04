from pathlib import Path
import pytest

from adapters.sandbox.repair_tools import RepairTools


def test_read_file_returns_workspace_text(tmp_path):
    """Verify the read tool returns text from its own workspace."""
    (tmp_path / "answer.py").write_text("answer = 42\n")
    assert RepairTools(tmp_path).read_file("answer.py") == "answer = 42\n"


def test_edit_file_writes_and_tracks_changed_file(tmp_path):
    """Verify edits persist and duplicate change entries are avoided."""
    tools = RepairTools(tmp_path)
    tools.edit_file("answer.py", "answer = 43\n")
    tools.edit_file("answer.py", "answer = 44\n")
    assert (tmp_path / "answer.py").read_text() == "answer = 44\n"
    assert tools.changed_files == ["answer.py"]


def test_tools_reject_paths_outside_workspace(tmp_path):
    """Verify path traversal is rejected before a workspace file is read."""
    with pytest.raises(ValueError):
        RepairTools(tmp_path).read_file("../outside.txt")


def test_run_tests_delegates_to_secure_runner(tmp_path, monkeypatch):
    """Verify the tool delegates test execution to the sandbox runner."""
    expected = {"passed": True, "output": "1 passed", "returncode": 0}
    monkeypatch.setattr("adapters.sandbox.repair_tools.run_pytest", lambda workspace: expected)
    assert RepairTools(tmp_path).run_tests() == expected
