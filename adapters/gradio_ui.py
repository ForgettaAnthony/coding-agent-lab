"""Small Gradio presentation layer for scripted repair demonstrations."""

import shutil
import tempfile
from pathlib import Path
from typing import Any

import gradio as gr

from bootstrap import create_repair_service


CASES = [
    "arithmetic",
    "balanced_brackets",
    "median",
    "multi_function",
    "unique_words",
]


def _format_trace(trace: list[dict[str, Any]]) -> str:
    """Format the agent's public events for display."""
    lines: list[str] = []
    for entry in trace:
        event = entry.get("event")
        if event == "repair_started":
            lines.append(f"Repair started: {entry.get('case')}")
        elif event == "model_response":
            decision = entry.get("decision")
            if entry.get("status") == "accepted":
                detail = str(entry.get("tool", "unknown"))
                if entry.get("path"):
                    detail += f" {entry['path']}"
                if entry.get("summary"):
                    detail += f" - {entry['summary']}"
                lines.append(f"Decision {decision}: {detail}")
            else:
                lines.append(f"Decision {decision}: {entry.get('error', 'error')}")
        elif event == "tool_result":
            decision = entry.get("decision")
            tool = entry.get("tool", "unknown")
            if entry.get("status") != "ok":
                lines.append(f"Decision {decision} {tool}: {entry.get('error')}")
            elif tool == "run_tests":
                outcome = "passed" if entry.get("passed") else "failed"
                lines.append(
                    f"Decision {decision} run_tests: {outcome} "
                    f"(return code {entry.get('returncode')})"
                )
            elif entry.get("path"):
                lines.append(f"Decision {decision} {tool}: {entry['path']}")
            else:
                lines.append(f"Decision {decision} {tool}: complete")
        elif event == "repair_finished":
            outcome = "PASSED" if entry.get("passed") else "FAILED"
            lines.append(f"Repair {outcome}: {entry.get('reason')}")
    return "\n".join(lines)


def _read_changed_files(workspace: Path, changed_files: list[str]) -> str:
    """Read changed UTF-8 files while preserving workspace containment."""
    sections: list[str] = []
    workspace = workspace.resolve(strict=True)
    for relative_path in changed_files:
        target = (workspace / relative_path).resolve(strict=True)
        if target != workspace and workspace not in target.parents:
            raise ValueError("Changed file escaped the disposable workspace")
        sections.append(
            f"===== {relative_path} =====\n{target.read_text(encoding='utf-8')}"
        )
    return "\n\n".join(sections) or "No files were changed."


def _archive_workspace(workspace: Path) -> str:
    """Create a Gradio-downloadable ZIP of the disposable workspace."""
    workspace = workspace.resolve(strict=True)
    download_dir = Path(tempfile.mkdtemp(prefix="coding-agent-lab-download-"))
    archive_base = download_dir / f"{workspace.name}-repaired"
    return shutil.make_archive(str(archive_base), "zip", root_dir=workspace)


def _format_test_result(result: Any) -> str:
    """Format the final sandboxed test result."""
    if result is None:
        return "No sandboxed test result was produced."
    outcome = "PASSED" if result.passed else "FAILED"
    return (
        f"{outcome} (return code {result.returncode})\n\n"
        f"{result.output}"
    )


def _run_repair(service: Any, case_name: str) -> tuple[str, str, str, str, str | None]:
    """Run the existing service and prepare its public UI outputs."""
    if case_name not in CASES:
        return (
            "Repair could not start: unknown case.",
            "",
            "No files were changed.",
            "No sandboxed test result was produced.",
            None,
        )

    try:
        result = service.repair(case_name)
        changed_text = _read_changed_files(result.workspace, result.changed_files)
        archive = _archive_workspace(result.workspace)
    except (OSError, RuntimeError, ValueError) as error:
        return (
            f"Repair could not complete: {type(error).__name__}: {error}",
            "",
            "No changed-file output is available.",
            "No sandboxed test result is available.",
            None,
        )

    status = "Repair PASSED" if result.passed else "Repair FAILED"
    return (
        status,
        _format_trace(result.trace),
        changed_text,
        _format_test_result(result.last_test),
        archive,
    )


def create_demo(service: Any | None = None) -> gr.Blocks:
    """Build the local scripted-repair Gradio page."""
    repair_service = service or create_repair_service("scripted")

    theme = gr.themes.Default(
        font=("ui-sans-serif", "system-ui", "sans-serif"),
        font_mono=("ui-monospace", "Consolas", "monospace"),
    )
    with gr.Blocks(
        title="Python Repair Agent Lab",
        theme=theme,
        analytics_enabled=False,
    ) as demo:
        gr.Markdown(
            "# Python Repair Agent Lab\n"
            "Choose one supplied case. The agent repairs a disposable copy and "
            "runs evaluation tests only in the Docker sandbox."
        )
        case_name = gr.Dropdown(
            choices=CASES,
            value="arithmetic",
            label="Evaluation case",
            allow_custom_value=False,
        )
        start = gr.Button("Start repair", variant="primary")
        status = gr.Textbox(label="Result", interactive=False)
        trace = gr.Textbox(label="Public trace", lines=12, interactive=False)
        changed = gr.Textbox(
            label="Changed files and contents", lines=16, interactive=False
        )
        tests = gr.Textbox(label="Final sandboxed test output", lines=12, interactive=False)
        download = gr.File(label="Repaired workspace ZIP", interactive=False)

        start.click(
            fn=lambda selected: _run_repair(repair_service, selected),
            inputs=case_name,
            outputs=[status, trace, changed, tests, download],
        )

    return demo
