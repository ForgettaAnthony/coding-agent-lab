from statistics_tools import median


def test_median_of_odd_number_of_values():
    """Specify the central value for an odd-length sequence."""
    assert median([9, 3, 5]) == 5


def test_median_of_even_number_of_values():
    """Specify the mean of the two central values for an even-length sequence."""
    assert median([7, 1, 3, 9]) == 5


def test_median_does_not_mutate_input():
    """Specify that callers retain their original order."""
    values = [4, 1, 9]
    assert median(values) == 4
    assert values == [4, 1, 9]
