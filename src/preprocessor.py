"""
Text Preprocessing Module
==========================
Cleans, tokenizes, and extracts n-gram shingles from raw document text.

Pipeline:
  raw text
    → lowercase
    → remove punctuation / special chars
    → collapse whitespace
    → tokenize into words
    → split into sentences
    → generate k-shingles (overlapping n-gram windows)
"""

import re
import string
from typing import Generator


# ──────────────────────────────────────────────────────────────
#  Basic Cleaning
# ──────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Normalize raw text:
      1. Lowercase
      2. Remove punctuation (keep spaces)
      3. Collapse multiple spaces into one
      4. Strip leading/trailing whitespace
    """
    text = text.lower()
    # Replace punctuation with space so words don't run together
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    # Collapse runs of whitespace (spaces, tabs, newlines)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    """Split cleaned text into individual words (tokens)."""
    return text.split()


def split_sentences(raw_text: str) -> list[str]:
    """
    Split raw text into sentences on  .  !  ?  followed by whitespace.
    Returns cleaned, non-empty sentences.
    """
    sentences = re.split(r'(?<=[.!?])\s+', raw_text.strip())
    return [s.strip() for s in sentences if s.strip()]


# ──────────────────────────────────────────────────────────────
#  Shingling  (k-gram fingerprinting)
# ──────────────────────────────────────────────────────────────

def generate_shingles(text: str, k: int = 5) -> set[str]:
    """
    Generate character-level k-shingles (sliding window of k chars).

    Shingles are used in MinHash / Jaccard similarity estimation.

    Parameters
    ----------
    text : Cleaned text string
    k    : Shingle size (default 5 characters)

    Returns
    -------
    Set of unique k-shingles.

    Example
    -------
    >>> generate_shingles("hello world", k=5)
    {'hello', 'ello ', 'llo w', 'lo wo', 'o wor', ' worl', 'world'}
    """
    return {text[i:i + k] for i in range(len(text) - k + 1)}


def generate_word_ngrams(tokens: list[str], n: int = 3) -> list[str]:
    """
    Generate word-level n-grams from a token list.

    Parameters
    ----------
    tokens : List of words
    n      : Window size (default trigrams)

    Returns
    -------
    List of space-joined n-gram strings.

    Example
    -------
    tokens = ['the', 'quick', 'brown', 'fox']
    n = 2  →  ['the quick', 'quick brown', 'brown fox']
    """
    return [' '.join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


# ──────────────────────────────────────────────────────────────
#  Document Loading
# ──────────────────────────────────────────────────────────────

def load_document(filepath: str) -> str:
    """Read a plain-text (.txt) file and return its content as a string."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Document not found: {filepath}")
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin-1') as f:
            return f.read()


def preprocess_document(filepath: str, shingle_k: int = 5, ngram_n: int = 3) -> dict:
    """
    Full preprocessing pipeline for a document file.

    Returns
    -------
    dict with keys:
      raw        : original text
      clean      : lowercased, punctuation-removed text
      tokens     : list of words
      sentences  : list of sentences (from raw text)
      shingles   : set of char k-shingles
      ngrams     : list of word n-grams
    """
    raw       = load_document(filepath)
    clean     = clean_text(raw)
    tokens    = tokenize(clean)
    sentences = split_sentences(raw)
    shingles  = generate_shingles(clean, k=shingle_k)
    ngrams    = generate_word_ngrams(tokens, n=ngram_n)

    return {
        'raw'      : raw,
        'clean'    : clean,
        'tokens'   : tokens,
        'sentences': sentences,
        'shingles' : shingles,
        'ngrams'   : ngrams,
    }


# ──────────────────────────────────────────────────────────────
#  Quick self-test
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = "Hello, World! This is a TEST. Python is great."
    print("Clean  :", clean_text(sample))
    print("Tokens :", tokenize(clean_text(sample)))
    print("Sents  :", split_sentences(sample))
    print("Shingls:", list(generate_shingles(clean_text(sample), k=4))[:5])
    toks = tokenize(clean_text(sample))
    print("Ngrams :", generate_word_ngrams(toks, n=2)[:5])
