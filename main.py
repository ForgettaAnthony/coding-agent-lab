"""Command-line entry point for deterministic repair demonstrations."""

import argparse
import json
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
    subparsers.add_parser("ui", help="start the local scripted-repair page")
    return parser


def _print_trace_entry(entry: dict[str, Any]) -> None:
    """Print one public trace event in a readable form."""
    event = entry.get("event")
    if event == "repair_started":
        print(f"- repair started: {entry.get('case')}")
    elif event == "model_response":
        decision = entry.get("decision")
        if entry.get("status") == "accepted":
            details = entry.get("tool", "unknown")
            if entry.get("path"):
                details += f" {entry['path']}"
            if entry.get("summary"):
                details += f" - {entry['summary']}"
            print(f"- decision {decision}: {details}")
        else:
            print(f"- decision {decision}: {entry.get('error', 'model error')}")
    elif event == "tool_result":
        tool = entry.get("tool", "unknown")
        if entry.get("status") != "ok":
            print(f"- {tool}: {entry.get('error', 'tool error')}")
        elif tool == "run_tests":
            outcome = "passed" if entry.get("passed") else "failed"
            print(f"- run_tests: {outcome} (return code {entry.get('returncode')})")
            if entry.get("output"):
                for line in str(entry["output"]).splitlines():
                    print(f"    {line}")
        elif entry.get("path"):
            print(f"- {tool}: {entry['path']}")
        else:
            print(f"- {tool}: complete")
    elif event == "repair_finished":
        outcome = "passed" if entry.get("passed") else "failed"
        print(f"- repair {outcome}: {entry.get('reason')}")
    else:
        print(f"- {json.dumps(entry, sort_keys=True)}")


def _print_result(result: Any) -> None:
    """Print the public trace and final repair artifacts."""
    print("Public trace:")
    for entry in result.trace:
        _print_trace_entry(entry)

    print("Changed files:")
    if result.changed_files:
        for path in result.changed_files:
            print(f"- {path}")
    else:
        print("- (none)")

    print(f"Workspace: {result.workspace}")
    print("Final sandboxed test result:")
    if result.last_test is None:
        print("- no test result")
    else:
        outcome = "passed" if result.last_test.passed else "failed"
        print(f"- {outcome} (return code {result.last_test.returncode})")
        if result.last_test.output:
            print(result.last_test.output)

    print(f"Final repair result: {'PASSED' if result.passed else 'FAILED'}")


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
        service = create_repair_service(args.provider)
        result = service.repair(args.project)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Repair could not start: {error}", file=sys.stderr)
        return 2

    _print_result(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
