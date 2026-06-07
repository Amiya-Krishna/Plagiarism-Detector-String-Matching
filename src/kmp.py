"""
KMP (Knuth-Morris-Pratt) String Matching Algorithm
===================================================
Time Complexity  : O(n + m)  where n = text length, m = pattern length
Space Complexity : O(m)      for the failure function array

How it works:
1. Build a "failure function" (LPS array) from the pattern
2. Use it to skip re-comparisons after a mismatch
"""


def build_lps(pattern: str) -> list[int]:
    """
    Build the Longest Proper Prefix which is also Suffix (LPS) array.
    
    Example: pattern = "ABABC"
      lps = [0, 0, 1, 2, 0]
      - "A"     → no proper prefix = suffix → 0
      - "AB"    → no match → 0
      - "ABA"   → "A" is both prefix and suffix → 1
      - "ABAB"  → "AB" is both → 2
      - "ABABC" → no match → 0
    """
    m = len(pattern)
    lps = [0] * m
    length = 0   # length of previous longest prefix-suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                # Fall back — don't increment i
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str) -> list[int]:
    """
    Search for all occurrences of `pattern` in `text`.
    
    Returns a list of starting indices (0-based) where pattern is found.
    
    Parameters
    ----------
    text    : The document / corpus to search in
    pattern : The phrase / sentence to look for
    
    Returns
    -------
    List of start positions; empty list if no match found.
    """
    if not pattern or not text:
        return []

    n, m = len(text), len(pattern)
    lps = build_lps(pattern)
    matches = []

    i = 0   # index for text
    j = 0   # index for pattern

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1

        if j == m:
            # Full pattern matched — record start position
            matches.append(i - j)
            j = lps[j - 1]   # look for next match
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return matches


def kmp_find_all_phrases(text: str, phrases: list[str]) -> dict:
    """
    Run KMP for each phrase in `phrases` against `text`.
    
    Returns
    -------
    dict: { phrase -> [list of start positions] }
         Only phrases that actually match are included.
    """
    results = {}
    for phrase in phrases:
        positions = kmp_search(text.lower(), phrase.lower())
        if positions:
            results[phrase] = positions
    return results


# ──────────────────────────────────────────────────────────────
#  Quick self-test
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    text    = "the quick brown fox jumps over the lazy dog"
    pattern = "the"
    hits    = kmp_search(text, pattern)
    print(f"Pattern '{pattern}' found at positions: {hits}")
    # Expected: [0, 31]

    phrases = ["quick brown", "lazy dog", "hello world"]
    all_hits = kmp_find_all_phrases(text, phrases)
    print("Phrase search results:", all_hits)
