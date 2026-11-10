"""Command-line entry point for repair demonstrations and the local UI."""

import argparse
import sys
from typing import Any

from bootstrap import SUPPORTED_PROVIDERS, create_repair_service


def _build_parser() -> argparse.ArgumentParser:
    """Create the supported command-line interface."""
    parser = argparse.ArgumentParser(description="Run the Python repair agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    repair_parser = subparsers.add_parser(
        "repair", help="repair one supplied evaluation case"
    )
    repair_parser.add_argument("project", help="relative path such as evals/arithmetic")
    repair_parser.add_argument(
        "--provider",
        choices=SUPPORTED_PROVIDERS,
        default="scripted",
        help="chat provider (default: scripted)",
    )
    repair_parser.add_argument(
        "--model",
        default=None,
        help="Ollama model (default: OLLAMA_MODEL or qwen2.5-coder:7b)",
    )
    repair_parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Ollama sampling temperature (default: 0.0)",
    )
    subparsers.add_parser("ui", help="start the local scripted-repair page")
    return parser


def _print_labeled_step(label: str, headline: str, detail: str | None = None) -> None:
    """Print one flushed terminal step with optional indented detail."""
    print(f"{label:<9}{headline}", flush=True)
    if detail:
        for line in detail.splitlines():
            print(f"{'':9}  {line}", flush=True)


class TerminalTraceRecorder:
    """Render public repair events as live, human-friendly terminal steps."""

    def record(self, event: str, payload: dict[str, Any]) -> None:
        """Print one labeled public event without changing stored trace data."""
        decision = payload.get("decision")
        step = f"#{decision} " if decision is not None else ""

        if event == "repair_started":
            _print_labeled_step("START", f"repair {payload.get('case')}")
            return

        if event == "model_response":
            if payload.get("status") == "accepted":
                detail = str(payload.get("tool", "unknown"))
                if payload.get("path"):
                    detail += f" {payload['path']}"
                if payload.get("summary"):
                    detail += f" - {payload['summary']}"
                _print_labeled_step("ACTION", f"{step}{detail}")
            else:
                status = str(payload.get("status", "error")).upper()
                _print_labeled_step(
                    "ACTION",
                    f"{step}{status}",
                    str(payload.get("error", "model error")),
                )
            return

        if event == "tool_result":
            tool = str(payload.get("tool", "unknown"))
            status = str(payload.get("status", "error"))
            if status != "ok":
                _print_labeled_step(
                    "RESULT",
                    f"{step}{tool} {status.upper()}",
                    str(payload.get("error", "tool error")),
                )
            elif tool == "run_tests":
                outcome = "PASSED" if payload.get("passed") else "FAILED"
                _print_labeled_step(
                    "RESULT",
                    f"{step}run_tests {outcome} "
                    f"(return code {payload.get('returncode')})",
                    str(payload.get("output", "")),
                )
            elif payload.get("path"):
                _print_labeled_step(
                    "RESULT", f"{step}{tool} OK - {payload['path']}"
                )
            else:
                _print_labeled_step("RESULT", f"{step}{tool} OK")
            return

        if event == "repair_finished":
            outcome = "PASSED" if payload.get("passed") else "FAILED"
            _print_labeled_step(
                "FINISHED", outcome, str(payload.get("reason", ""))
            )


def _print_result(result: Any) -> None:
    """Print changed files and the final sandboxed test status."""
    print(f"\nWorkspace: {result.workspace}")
    print("Changed files:")
    if result.changed_files:
        for path in result.changed_files:
            print(f"  - {path}")
    else:
        print("  - (none)")

    if result.last_test is None:
        print("Final sandboxed test status: NOT RUN")
    else:
        outcome = "PASSED" if result.last_test.passed else "FAILED"
        print(
            "Final sandboxed test status: "
            f"{outcome} (return code {result.last_test.returncode})"
        )


def main(argv: list[str] | None = None) -> int:
    """Run the selected command and return a process exit status."""
    args = _build_parser().parse_args(argv)
    if args.command == "ui":
        from adapters.gradio_ui import create_demo

        try:
            create_demo().launch()
        except (OSError, RuntimeError, ValueError) as error:
            print(f"UI could not start: {error}", file=sys.stderr)
            return 2
        return 0

    try:
        service = create_repair_service(
            args.provider,
            model=args.model,
            temperature=args.temperature,
            recorder=TerminalTraceRecorder(),
        )
        result = service.repair(args.project)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Repair could not start: {error}", file=sys.stderr)
        return 2

    _print_result(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
