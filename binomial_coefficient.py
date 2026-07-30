def binomial_coefficient(n, k):
    """
    Compute the binomial coefficient C(n, k) = n! / (k! * (n-k)!).
    Uses the multiplicative formula for efficiency and to avoid large intermediate factorials.
    """
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    # Take advantage of symmetry: C(n, k) == C(n, n-k)
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        # Multiply by (n - k + i) then divide by i.
        # The division is exact at each step because the intermediate result is a binomial coefficient.
        result = result * (n - k + i) // i
    return result


if __name__ == "__main__":
    import sys
    data = sys.stdin.read().strip().split()
    if not data:
        sys.exit(0)
    n = int(data[0])
    k = int(data[1])
    print(binomial_coefficient(n, k))
