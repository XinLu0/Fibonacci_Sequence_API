from functools import lru_cache


def fibonacci_iterative(n: int) -> int:
    """Compute the nth Fibonacci number using an iterative approach.
    F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2)
    """
    if n < 0:
        raise ValueError(f"n must be a non-negative integer, got {n}")
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


@lru_cache(maxsize=1024)
def fibonacci_cached(n: int) -> int:
    """Cached wrapper around fibonacci_iterative."""
    return fibonacci_iterative(n)
