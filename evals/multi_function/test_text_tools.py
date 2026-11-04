from text_tools import greeting, initials, normalize_name


def test_normalize_name():
    """Specify trimming and lowercasing behavior for names."""
    assert normalize_name("  Ada Lovelace ") == "ada lovelace"


def test_greeting_uses_normalized_name():
    """Specify the expected greeting capitalization."""
    assert greeting("  Ada ") == "Hello, Ada!"


def test_initials():
    """Specify initials for a two-word name."""
    assert initials("ada lovelace") == "AL"
