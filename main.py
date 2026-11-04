"""Single application entry point: terminal repair command or Gradio UI."""

import argparse
from pathlib import Path

from adapters.gradio_ui import create_demo
from adapters.sandbox.runner import resolve_eval_project, safe_path
from bootstrap import build_repair_service


def eval_project_argument(value):
    """Validate a CLI project path before the repair service creates a workspace."""
    try:
        resolve_eval_project(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error
    return value


def main():
    """Parse the selected interface command and start the requested workflow."""
    parser = argparse.ArgumentParser(description="Python Repair Agent Lab")
    commands = parser.add_subparsers(dest="command", required=True)
    repair = commands.add_parser("repair", help="Repair one instructor-provided evals project from the terminal")
    repair.add_argument("project_path", metavar="EVAL_PROJECT", type=eval_project_argument,
                        help="Direct evals project, for example evals/arithmetic")
    repair.add_argument("--provider", choices=["ollama", "vertex", "openai"],
                        help="Model provider (default: MODEL_PROVIDER or ollama)")
    repair.add_argument("--model", help="Provider model identifier")
    repair.add_argument("--research", action="store_true", default=None,
                        help="Enable bounded GitHub research (requires GITHUB_TOKEN)")
    repair.add_argument("--langfuse", action="store_true", default=None,
                        help="Record the repair trajectory in Langfuse (requires optional setup)")
    commands.add_parser("ui", help="Launch the Gradio interface")
    args = parser.parse_args()
    if args.command == "ui":
        create_demo().launch()
        return
    result = build_repair_service(model=args.model, provider=args.provider,
                                  enable_github_research=args.research,
                                  enable_langfuse=args.langfuse).repair(args.project_path)
    print(result.summary)
    print("passed:", result.passed)
    print("workspace:", result.workspace)
    print("trace:")
    for line in result.trace:
        print("-", line)
    print("changed code:")
    if not result.changed_files:
        print("- No files changed.")
    for relative_path in result.changed_files:
        print(f"\n--- {relative_path} ---")
        print(safe_path(Path(result.workspace), relative_path).read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
