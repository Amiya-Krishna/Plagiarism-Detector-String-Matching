"""
Rabin-Karp Rolling Hash Algorithm
===================================
Time Complexity  : O(n + m) average,  O(n*m) worst-case (hash collisions)
Space Complexity : O(1)

How it works:
1. Hash the pattern window of length m
2. Slide a window of size m across the text
3. Compare hashes first (cheap); only do character comparison on a hash hit
4. Use rolling hash so each slide is O(1) instead of O(m)

This is especially powerful for multi-pattern search (used in winnowing / fingerprinting).
"""

BASE  = 256          # Number of characters in alphabet (extended ASCII)
PRIME = 101          # A prime modulus to reduce collisions


def _hash(string: str, length: int) -> int:
    """Compute polynomial rolling hash for string[:length]."""
    h = 0
    for i in range(length):
        h = (h * BASE + ord(string[i])) % PRIME
    return h


def rabin_karp_search(text: str, pattern: str) -> list[int]:
    """
    Find all occurrences of `pattern` in `text` using Rabin-Karp.

    Parameters
    ----------
    text    : The source document
    pattern : The phrase to search for

    Returns
    -------
    List of 0-based start positions.
    """
    n, m = len(text), len(pattern)
    if m > n or not pattern:
        return []

    # Precompute h = BASE^(m-1) % PRIME (the highest-order coefficient)
    h = 1
    for _ in range(m - 1):
        h = (h * BASE) % PRIME

    pattern_hash = _hash(pattern, m)
    window_hash  = _hash(text, m)
    matches = []

    for i in range(n - m + 1):
        # Hash match → verify character by character (avoid false positives)
        if window_hash == pattern_hash:
            if text[i:i + m] == pattern:
                matches.append(i)

        # Roll the hash: remove leading char, add trailing char
        if i < n - m:
            window_hash = (BASE * (window_hash - ord(text[i]) * h) + ord(text[i + m])) % PRIME
            if window_hash < 0:
                window_hash += PRIME

    return matches


def rabin_karp_multi_pattern(text: str, patterns: list[str]) -> dict:
    """
    Search for multiple patterns simultaneously using Rabin-Karp.

    Builds a hash-set of pattern hashes for O(1) lookup per window.

    Returns
    -------
    dict: { pattern -> [start positions] }
    """
    if not patterns or not text:
        return {}

    # Group patterns by length (only same-length patterns can share a window scan)
    from collections import defaultdict
    by_length: dict[int, list[str]] = defaultdict(list)
    for p in patterns:
        by_length[len(p)].append(p)

    results = {p: [] for p in patterns}

    for m, group in by_length.items():
        n = len(text)
        if m > n:
            continue

        # Build hash → [patterns] mapping for this length bucket
        hash_to_patterns: dict[int, list[str]] = defaultdict(list)
        for p in group:
            hash_to_patterns[_hash(p, m)].append(p)

        h = 1
        for _ in range(m - 1):
            h = (h * BASE) % PRIME

        window_hash = _hash(text, m)

        for i in range(n - m + 1):
            if window_hash in hash_to_patterns:
                window_text = text[i:i + m]
                for p in hash_to_patterns[window_hash]:
                    if window_text == p:
                        results[p].append(i)

            if i < n - m:
                window_hash = (BASE * (window_hash - ord(text[i]) * h) + ord(text[i + m])) % PRIME
                if window_hash < 0:
                    window_hash += PRIME

    # Remove empty entries
    return {p: v for p, v in results.items() if v}


# ──────────────────────────────────────────────────────────────
#  Quick self-test
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    text    = "the quick brown fox jumps over the lazy dog"
    pattern = "the"
    hits    = rabin_karp_search(text, pattern)
    print(f"[Rabin-Karp] Pattern '{pattern}' found at: {hits}")

    patterns = ["quick brown", "lazy dog", "hello world"]
    multi    = rabin_karp_multi_pattern(text, patterns)
    print("[Rabin-Karp] Multi-pattern results:", multi)
