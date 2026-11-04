def normalize_name(name):
    """Trim surrounding whitespace and lowercase a supplied name."""
    return name.strip().lower()


def greeting(name):
    """Create a greeting from a normalized name."""
    return f"Hello, {normalize_name(name).upper()}!"


def initials(name):
    """Return uppercase initials for the whitespace-separated parts of a name."""
    return "".join(part[0].upper() for part in name.split())
