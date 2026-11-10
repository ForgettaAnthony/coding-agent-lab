"""Tests for human-friendly live terminal output."""

from pathlib import Path
from types import SimpleNamespace

from core.models import TestResult
from main import TerminalTraceRecorder, _print_result


def test_terminal_output_is_labeled_and_indents_tool_output(capsys) -> None:
    recorder = TerminalTraceRecorder()
    recorder.record("repair_started", {"case": "sample"})
    recorder.record(
        "model_response",
        {
            "decision": 1,
            "status": "accepted",
            "tool": "run_tests",
            "summary": "Reproduce failure",
        },
    )
    recorder.record(
        "tool_result",
        {
            "decision": 1,
            "tool": "run_tests",
            "status": "ok",
            "passed": False,
            "returncode": 1,
            "output": "line one\nline two",
        },
    )
    recorder.record(
        "repair_finished",
        {"passed": False, "reason": "Repair was not verified."},
    )
    result = SimpleNamespace(
        workspace=Path("workspace"),
        changed_files=["sample.py"],
        last_test=TestResult(False, "line one\nline two", 1),
    )
    _print_result(result)

    output = capsys.readouterr().out
    assert "START    repair sample" in output
    assert "ACTION   #1 run_tests - Reproduce failure" in output
    assert "RESULT   #1 run_tests FAILED (return code 1)" in output
    assert "           line one\n           line two" in output
    assert "FINISHED FAILED" in output
    assert output.index("FINISHED") < output.index("Changed files:")
    assert "  - sample.py" in output
    assert output.rstrip().endswith(
        "Final sandboxed test status: FAILED (return code 1)"
    )
    assert '"event"' not in output
