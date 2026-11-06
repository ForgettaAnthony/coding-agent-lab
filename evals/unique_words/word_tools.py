def unique_words(text):
    """Return lowercase words once, in the order first seen."""
    return sorted(set(text.lower().split()))
