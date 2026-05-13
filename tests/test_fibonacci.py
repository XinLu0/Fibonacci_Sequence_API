import pytest
from app.fibonacci import fibonacci_iterative, fibonacci_cached


@pytest.mark.parametrize(
    "n, expected",
    [
        (0, 0),
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 3),
        (5, 5),
        (6, 8),
        (7, 13),
        (8, 21),
        (9, 34),
        (10, 55),
        (20, 6765),
        (30, 832040),
        (50, 12586269025),
    ],
)
def test_known_values(n, expected):
    assert fibonacci_iterative(n) == expected


def test_negative_input_raises():
    with pytest.raises(ValueError, match="non-negative"):
        fibonacci_iterative(-1)


def test_large_value():
    result = fibonacci_iterative(1000)
    assert isinstance(result, int)
    assert result > 0


@pytest.mark.parametrize(
    "n, expected",
    [
        (0, 0),
        (1, 1),
        (10, 55),
        (20, 6765),
    ],
)
def test_cached_matches_iterative(n, expected):
    assert fibonacci_cached(n) == expected


def test_cache_returns_same_result():
    first = fibonacci_cached(15)
    second = fibonacci_cached(15)
    assert first == second
