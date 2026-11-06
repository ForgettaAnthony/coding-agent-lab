from word_tools import unique_words


def test_unique_words_preserve_first_appearance_order():
    """Specify deterministic first-appearance order, not alphabetical order."""
    assert unique_words("Red blue red green blue") == ["red", "blue", "green"]


def test_unique_words_normalize_case():
    """Specify case-insensitive duplicate detection."""
    assert unique_words("Ada ada ADA") == ["ada"]


def test_unique_words_allow_empty_text():
    """Specify the boundary case of no words."""
    assert unique_words("") == []
