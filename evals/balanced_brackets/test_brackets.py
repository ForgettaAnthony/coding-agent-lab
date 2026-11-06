from brackets import is_balanced


def test_accepts_nested_matching_brackets():
    """Specify a valid mixed, nested expression."""
    assert is_balanced("function([value, {key: (other)}])")


def test_rejects_mismatched_bracket_types():
    """Specify that closing a different bracket type is invalid."""
    assert not is_balanced("([)]")


def test_rejects_unmatched_opening_or_closing_brackets():
    """Specify both unmatched boundary cases."""
    assert not is_balanced("(()")
    assert not is_balanced("())")
