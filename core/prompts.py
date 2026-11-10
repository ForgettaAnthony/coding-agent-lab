"""Prompt text helpers for the repair agent."""


def system_instruction() -> str:
    """Return the repair policy and allowed action format."""
    return """You are a Python repair agent. Inspect the local code before changing it. Reproduce a failing test before editing, make one focused edit, and verify the repair by running the tests again.

Reply with exactly one JSON object. Do not include Markdown, code fences, prose, or additional objects. Use one of these allowed action shapes:
{"tool":"read_file","path":"test_calculator.py","summary":"Read the test"}
{"tool":"run_tests","summary":"Reproduce the failure"}
{"tool":"edit_file","path":"calculator.py","content":"..."}

The optional summary is a short public label shown in the trace, not private reasoning."""


def case_request(case_name: str, relative_files: list[str]) -> str:
    """Return a request containing the selected case and available files."""
    files = "\n".join(f"- {path}" for path in relative_files) or "- (none)"
    return (
        f"Repair case: {case_name}\n"
        f"Available relative files:\n{files}\n"
        "Choose the next allowed action."
    )


def tool_result_message(tool: str, result: str) -> str:
    """Return a model-visible observation from one tool call."""
    return f"Tool result for {tool}:\n{result}\nChoose the next allowed action."
