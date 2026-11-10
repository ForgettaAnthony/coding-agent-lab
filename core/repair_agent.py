"""Bounded repair loop that mediates model and tool interactions."""

import json
from pathlib import Path
from typing import Any

from core.models import ModelAction, RepairResult, TestResult
from core.ports import ChatClient, RepairToolsPort, TraceRecorder
from core.prompts import case_request, system_instruction, tool_result_message


MAX_DECISIONS = 8


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object while rejecting duplicate keys."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate field: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    """Reject non-standard JSON constants such as NaN."""
    raise ValueError(f"Invalid JSON constant: {value}")


def _parse_action(raw_response: str) -> ModelAction:
    """Parse and validate exactly one permitted model action."""
    try:
        payload = json.loads(
            raw_response,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid JSON response: {error}") from error

    if not isinstance(payload, dict):
        raise ValueError("The response must be one JSON object")

    tool = payload.get("tool")
    if not isinstance(tool, str):
        raise ValueError("Field 'tool' must be a string")

    schemas = {
        "read_file": ({"tool", "path"}, {"tool", "path", "summary"}),
        "run_tests": ({"tool"}, {"tool", "summary"}),
        "edit_file": (
            {"tool", "path", "content"},
            {"tool", "path", "content", "summary"},
        ),
    }
    if tool not in schemas:
        raise ValueError(f"Unknown tool: {tool}")

    required, allowed = schemas[tool]
    fields = set(payload)
    missing = required - fields
    extra = fields - allowed
    if missing:
        raise ValueError(f"Missing field(s): {', '.join(sorted(missing))}")
    if extra:
        raise ValueError(f"Unexpected field(s): {', '.join(sorted(extra))}")

    summary = payload.get("summary")
    if summary is not None and not isinstance(summary, str):
        raise ValueError("Field 'summary' must be a string when present")

    arguments: dict[str, Any] = {}
    if tool in {"read_file", "edit_file"}:
        path = payload["path"]
        if not isinstance(path, str) or not path:
            raise ValueError("Field 'path' must be a non-empty string")
        arguments["path"] = path
    if tool == "edit_file":
        content = payload["content"]
        if not isinstance(content, str):
            raise ValueError("Field 'content' must be a string")
        arguments["content"] = content

    return ModelAction(tool=tool, arguments=arguments, summary=summary)


class RepairAgent:
    """Run a bounded, policy-checked repair attempt."""

    def __init__(
        self,
        client: ChatClient,
        tools: RepairToolsPort,
        recorder: TraceRecorder | None = None,
    ) -> None:
        self.client = client
        self.tools = tools
        self.recorder = recorder

    def repair(
        self,
        case_name: str,
        relative_files: list[str],
        workspace: str | Path,
    ) -> RepairResult:
        """Attempt one repair and return its complete public result."""
        workspace_path = Path(workspace)
        messages = [
            {"role": "system", "content": system_instruction()},
            {"role": "user", "content": case_request(case_name, relative_files)},
        ]
        trace: list[dict[str, Any]] = []
        self._emit(trace, {"event": "repair_started", "case": case_name})
        changed_files: list[str] = []
        last_test: TestResult | None = None
        read_observed = False
        failing_test_observed = False
        edit_completed = False

        for decision in range(1, MAX_DECISIONS + 1):
            try:
                raw_response = self.client.chat(messages)
            except Exception as error:
                message = f"Client error: {type(error).__name__}: {error}"
                self._emit(
                    trace,
                    {
                        "event": "model_response",
                        "decision": decision,
                        "status": "error",
                        "error": message,
                    },
                )
                return self._finish(
                    False,
                    message,
                    trace,
                    changed_files,
                    workspace_path,
                    last_test,
                )

            try:
                action = _parse_action(raw_response)
            except ValueError as error:
                message = str(error)
                self._emit(
                    trace,
                    {
                        "event": "model_response",
                        "decision": decision,
                        "status": "invalid",
                        "error": message,
                    },
                )
                return self._finish(
                    False,
                    message,
                    trace,
                    changed_files,
                    workspace_path,
                    last_test,
                )

            messages.append({"role": "assistant", "content": raw_response})
            response_event: dict[str, Any] = {
                "event": "model_response",
                "decision": decision,
                "status": "accepted",
                "tool": action.tool,
            }
            if action.summary is not None:
                response_event["summary"] = action.summary
            if "path" in action.arguments:
                response_event["path"] = action.arguments["path"]
            self._emit(trace, response_event)

            if action.tool == "edit_file" and not (
                read_observed and failing_test_observed
            ):
                observation = (
                    "Policy error: edit_file requires a successful read_file "
                    "followed by a failing run_tests observation."
                )
                messages.append(
                    {
                        "role": "user",
                        "content": tool_result_message(action.tool, observation),
                    }
                )
                self._emit(
                    trace,
                    {
                        "event": "tool_result",
                        "decision": decision,
                        "tool": action.tool,
                        "status": "policy_error",
                        "error": observation,
                    },
                )
                continue

            try:
                if action.tool == "read_file":
                    path = action.arguments["path"]
                    content = self.tools.read_file(path)
                    read_observed = True
                    observation = content
                    tool_event: dict[str, Any] = {
                        "event": "tool_result",
                        "decision": decision,
                        "tool": action.tool,
                        "status": "ok",
                        "path": path,
                    }
                elif action.tool == "run_tests":
                    test_result = self.tools.run_tests()
                    if not isinstance(test_result, TestResult):
                        raise TypeError("run_tests must return TestResult")
                    last_test = test_result
                    if not test_result.passed and read_observed:
                        failing_test_observed = True
                    observation = self._format_test_result(test_result)
                    tool_event = {
                        "event": "tool_result",
                        "decision": decision,
                        "tool": action.tool,
                        "status": "ok",
                        "passed": test_result.passed,
                        "returncode": test_result.returncode,
                        "output": test_result.output,
                    }
                else:
                    path = action.arguments["path"]
                    self.tools.edit_file(path, action.arguments["content"])
                    edit_completed = True
                    normalized_path = Path(path).as_posix()
                    if normalized_path not in changed_files:
                        changed_files.append(normalized_path)
                    observation = f"Edited {path} successfully."
                    tool_event = {
                        "event": "tool_result",
                        "decision": decision,
                        "tool": action.tool,
                        "status": "ok",
                        "path": path,
                    }
            except Exception as error:
                observation = f"Tool error: {type(error).__name__}: {error}"
                messages.append(
                    {
                        "role": "user",
                        "content": tool_result_message(action.tool, observation),
                    }
                )
                self._emit(
                    trace,
                    {
                        "event": "tool_result",
                        "decision": decision,
                        "tool": action.tool,
                        "status": "error",
                        "error": observation,
                    },
                )
                continue

            messages.append(
                {
                    "role": "user",
                    "content": tool_result_message(action.tool, observation),
                }
            )
            self._emit(trace, tool_event)

            if action.tool == "run_tests" and last_test is not None:
                if last_test.passed and edit_completed:
                    return self._finish(
                        True,
                        "Repair verified by a passing post-edit test run.",
                        trace,
                        changed_files,
                        workspace_path,
                        last_test,
                    )
                if last_test.passed:
                    return self._finish(
                        False,
                        "Tests passed before any edit; no reproducible bug.",
                        trace,
                        changed_files,
                        workspace_path,
                        last_test,
                    )

        return self._finish(
            False,
            f"Decision budget exhausted after {MAX_DECISIONS} decisions.",
            trace,
            changed_files,
            workspace_path,
            last_test,
        )

    @staticmethod
    def _format_test_result(result: TestResult) -> str:
        """Format a test result for model-visible conversation history."""
        return (
            f"passed={result.passed}\n"
            f"returncode={result.returncode}\n"
            f"output:\n{result.output}"
        )

    def _emit(
        self,
        trace: list[dict[str, Any]],
        entry: dict[str, Any],
    ) -> None:
        """Store and best-effort publish one public trace entry."""
        trace.append(entry)
        if self.recorder is None:
            return
        event = str(entry["event"])
        payload = {key: value for key, value in entry.items() if key != "event"}
        try:
            self.recorder.record(event, payload)
        except Exception:
            pass

    def _finish(
        self,
        passed: bool,
        reason: str,
        trace: list[dict[str, Any]],
        changed_files: list[str],
        workspace: Path,
        last_test: TestResult | None,
    ) -> RepairResult:
        """Append the final event and build a repair result."""
        self._emit(
            trace,
            {"event": "repair_finished", "passed": passed, "reason": reason},
        )
        return RepairResult(
            passed=passed,
            trace=trace,
            changed_files=list(changed_files),
            workspace=workspace,
            last_test=last_test,
        )
