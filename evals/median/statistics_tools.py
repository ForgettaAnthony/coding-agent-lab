def median(values):
    """Return the median value without changing the input sequence."""
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle]
