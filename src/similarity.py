"""
Similarity Calculator
======================
Computes multiple similarity metrics between two documents:

  1. Jaccard Similarity    — set overlap of shingles
  2. Cosine Similarity     — TF-IDF-like vector comparison
  3. Sentence Match Score  — KMP-based exact sentence matching
  4. N-gram Overlap        — word n-gram intersection

Final plagiarism percentage is a weighted combination of all metrics.
"""

import math
from collections import Counter


# ──────────────────────────────────────────────────────────────
#  1. Jaccard Similarity  (Shingle-based)
# ──────────────────────────────────────────────────────────────

def jaccard_similarity(set_a: set, set_b: set) -> float:
    """
    Jaccard(A, B) = |A ∩ B| / |A ∪ B|

    Used with character k-shingles to detect near-duplicate text.
    Value: 0.0 (no overlap) → 1.0 (identical sets)
    """
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union        = len(set_a | set_b)
    return intersection / union


# ──────────────────────────────────────────────────────────────
#  2. Cosine Similarity  (Term Frequency Vectors)
# ──────────────────────────────────────────────────────────────

def _term_frequency(tokens: list[str]) -> Counter:
    """Build a word-frequency counter from a token list."""
    return Counter(tokens)


def cosine_similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
    """
    Cosine(A, B) = (A · B) / (||A|| × ||B||)

    Measures the angle between TF vectors in word-space.
    Robust to document length differences.
    """
    if not tokens_a or not tokens_b:
        return 0.0

    tf_a = _term_frequency(tokens_a)
    tf_b = _term_frequency(tokens_b)

    # Dot product over shared vocabulary
    all_words = set(tf_a) | set(tf_b)
    dot       = sum(tf_a[w] * tf_b[w] for w in all_words)

    mag_a = math.sqrt(sum(v ** 2 for v in tf_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in tf_b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ──────────────────────────────────────────────────────────────
#  3. Sentence Match Score  (KMP-based exact matching)
# ──────────────────────────────────────────────────────────────

def sentence_match_score(sentences_a: list[str],
                          sentences_b: list[str],
                          clean_fn) -> tuple[float, list[str]]:
    """
    For each sentence in document B, check if it (or a cleaned form)
    appears verbatim in document A's full text.

    Parameters
    ----------
    sentences_a : Sentence list from original document
    sentences_b : Sentence list from submitted document
    clean_fn    : callable — preprocessor.clean_text

    Returns
    -------
    (score, matched_sentences)
      score              : fraction of B's sentences found in A  [0.0–1.0]
      matched_sentences  : list of copied sentences
    """
    # Import here to avoid circular imports
    from src.kmp import kmp_search

    full_text_a = ' '.join(clean_fn(s) for s in sentences_a)
    matched     = []

    for sentence in sentences_b:
        clean_s = clean_fn(sentence)
        if len(clean_s) < 10:          # Skip very short fragments
            continue
        hits = kmp_search(full_text_a, clean_s)
        if hits:
            matched.append(sentence)

    if not sentences_b:
        return 0.0, []

    score = len(matched) / len(sentences_b)
    return score, matched


# ──────────────────────────────────────────────────────────────
#  4. N-gram Overlap
# ──────────────────────────────────────────────────────────────

def ngram_overlap(ngrams_a: list[str], ngrams_b: list[str]) -> float:
    """
    Compute what fraction of B's n-grams also appear in A.

    This catches paraphrasing where word order is mostly preserved
    but some words are substituted.
    """
    if not ngrams_b:
        return 0.0
    set_a = set(ngrams_a)
    set_b = set(ngrams_b)
    overlap = len(set_a & set_b)
    return overlap / len(set_b)


# ──────────────────────────────────────────────────────────────
#  5. Combined Plagiarism Score
# ──────────────────────────────────────────────────────────────

WEIGHTS = {
    'sentence_match': 0.40,   # Strongest signal — verbatim copy
    'jaccard'       : 0.25,   # Shingle overlap
    'cosine'        : 0.20,   # Vocabulary distribution
    'ngram_overlap' : 0.15,   # Phrase overlap
}


def compute_plagiarism_score(doc_a: dict, doc_b: dict) -> dict:
    """
    Run all similarity metrics and return a comprehensive report dict.

    Parameters
    ----------
    doc_a / doc_b : preprocessed document dicts from preprocessor.preprocess_document()

    Returns
    -------
    dict with individual scores, weighted total, percentage, verdict,
    and list of matched sentences.
    """
    from src.preprocessor import clean_text   # lazy import

    j_score, _ = jaccard_similarity(doc_a['shingles'], doc_b['shingles']), None
    j_score    = jaccard_similarity(doc_a['shingles'], doc_b['shingles'])
    c_score    = cosine_similarity(doc_a['tokens'], doc_b['tokens'])
    s_score, matched = sentence_match_score(
        doc_a['sentences'], doc_b['sentences'], clean_text
    )
    ng_score   = ngram_overlap(doc_a['ngrams'], doc_b['ngrams'])

    weighted = (
        WEIGHTS['sentence_match'] * s_score   +
        WEIGHTS['jaccard']        * j_score   +
        WEIGHTS['cosine']         * c_score   +
        WEIGHTS['ngram_overlap']  * ng_score
    )
    pct = round(weighted * 100, 2)

    # Verdict thresholds
    if pct < 15:
        verdict = "✅ ORIGINAL"
        color   = "green"
    elif pct < 40:
        verdict = "⚠️  SUSPICIOUS"
        color   = "yellow"
    elif pct < 70:
        verdict = "🔶 LIKELY PLAGIARIZED"
        color   = "orange"
    else:
        verdict = "🚨 PLAGIARIZED"
        color   = "red"

    return {
        'jaccard_score'        : round(j_score  * 100, 2),
        'cosine_score'         : round(c_score  * 100, 2),
        'sentence_match_score' : round(s_score  * 100, 2),
        'ngram_overlap_score'  : round(ng_score * 100, 2),
        'plagiarism_percentage': pct,
        'verdict'              : verdict,
        'verdict_color'        : color,
        'matched_sentences'    : matched,
        'total_sentences_b'    : len(doc_b['sentences']),
        'matched_count'        : len(matched),
    }


# ──────────────────────────────────────────────────────────────
#  Quick self-test
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    a = {"hello", "world", "foo", "bar"}
    b = {"hello", "world", "baz", "qux"}
    print("Jaccard:", jaccard_similarity(a, b))

    ta = ["the", "quick", "brown", "fox"]
    tb = ["the", "quick", "brown", "dog"]
    print("Cosine :", cosine_similarity(ta, tb))
