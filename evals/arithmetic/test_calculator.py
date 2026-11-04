from calculator import add


def test_adds_positive_numbers():
    """Specify addition for two positive operands."""
    assert add(2, 3) == 5


def test_adds_negative_numbers():
    """Specify addition when one operand is negative."""
    assert add(-4, 1) == -3
