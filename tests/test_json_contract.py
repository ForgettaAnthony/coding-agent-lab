"""Public checks for the model-response contract enforced before tool dispatch."""

import json

import pytest

from core.prompts import build_system_prompt, parse_model_action


def test_json_contract_accepts_one_allowed_action():
    """Verify a valid action with an optional public summary is accepted."""
    action = parse_model_action(json.dumps({
        "tool": "read_file", "path": "test_calculator.py", "summary": "Read the failing test first",
    }))
    assert action["tool"] == "read_file"


@pytest.mark.parametrize("reply", [
    "```json\n{\"tool\": \"run_tests\"}\n```",
    json.dumps({"tool": "run_tests", "path": "not allowed"}),
    json.dumps({"tool": ["run_tests"]}),
    json.dumps([{"tool": "run_tests"}]),
    '{"tool": "run_tests", "tool": "read_file", "path": "test.py"}',
])
def test_json_contract_rejects_non_exact_responses(reply):
    """Verify prose wrappers, extra fields, and non-object JSON are rejected."""
    with pytest.raises(ValueError):
        parse_model_action(reply)


def test_system_prompt_states_the_strict_json_requirement():
    """Verify the model receives an explicit instruction not to wrap its action."""
    prompt = build_system_prompt(False)
    assert "exactly one JSON object" in prompt
    assert "Do not return an array, Markdown fence" in prompt
