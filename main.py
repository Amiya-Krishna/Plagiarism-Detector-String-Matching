#!/usr/bin/env python3
"""
Plagiarism Detector — Main Entry Point
========================================
Usage:
  python main.py                                    # uses default sample docs
  python main.py original.txt submitted.txt         # custom docs
  python main.py -a docs/a.txt -b docs/b.txt        # named flags
  python main.py --demo                             # interactive demo mode
  python main.py --algorithm kmp                    # force a specific algorithm
  python main.py --no-html                          # skip HTML report
"""

import argparse
import sys
import os
import time

# ── Make sure project root is on sys.path ─────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.preprocessor import preprocess_document
from src.similarity    import compute_plagiarism_score
from src.reporter      import (print_console_report,
                                save_text_report,
                                save_html_report,
                                save_json_report)
from src.kmp           import kmp_find_all_phrases
from src.rabin_karp    import rabin_karp_multi_pattern


# ──────────────────────────────────────────────────────────────
#  Defaults
# ──────────────────────────────────────────────────────────────
DEFAULT_A = os.path.join(ROOT, 'documents', 'original.txt')
DEFAULT_B = os.path.join(ROOT, 'documents', 'submitted.txt')


# ──────────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────────

def _banner():
    print("""
\033[96m╔══════════════════════════════════════════════════════╗
║        PLAGIARISM DETECTOR  v1.0                     ║
║        KMP · Rabin-Karp · Jaccard · Cosine           ║
╚══════════════════════════════════════════════════════╝\033[0m
""")


def _spinner(message: str):
    """Minimal progress indicator."""
    print(f"  \033[93m⟳\033[0m  {message} ...", end='\r')
    time.sleep(0.2)
    print(f"  \033[92m✓\033[0m  {message}    ")


def run_detection(path_a: str,
                  path_b: str,
                  algorithm: str = 'both',
                  save_html: bool = True,
                  save_json: bool = True,
                  verbose: bool = True) -> dict:
    """
    Full pipeline: preprocess → match → score → report.

    Parameters
    ----------
    path_a    : Path to original / reference document
    path_b    : Path to submitted / suspect document
    algorithm : 'kmp' | 'rabin_karp' | 'both'
    save_html : Whether to save HTML report
    save_json : Whether to save JSON report
    verbose   : Whether to print console report

    Returns
    -------
    result dict from compute_plagiarism_score
    """

    if not os.path.exists(path_a):
        sys.exit(f"\033[91m✗  File not found: {path_a}\033[0m")
    if not os.path.exists(path_b):
        sys.exit(f"\033[91m✗  File not found: {path_b}\033[0m")

    # ── Step 1: Preprocess ────────────────────────────────────
    _spinner("Reading and preprocessing documents")
    doc_a = preprocess_document(path_a)
    doc_b = preprocess_document(path_b)

    # ── Step 2: String matching demo (KMP / Rabin-Karp) ───────
    # Extract sentences from B to search for in A
    phrases = [s.strip() for s in doc_b['sentences'] if len(s.strip()) > 20][:20]
    text_a  = doc_a['clean']

    if algorithm in ('kmp', 'both'):
        _spinner("Running KMP string matching")
        kmp_hits = kmp_find_all_phrases(text_a, [p.lower() for p in phrases])

    if algorithm in ('rabin_karp', 'both'):
        _spinner("Running Rabin-Karp rolling hash")
        rk_hits  = rabin_karp_multi_pattern(text_a.lower(),
                                            [p.lower() for p in phrases])

    # ── Step 3: Similarity scoring ────────────────────────────
    _spinner("Computing similarity metrics")
    result = compute_plagiarism_score(doc_a, doc_b)

    # ── Step 4: Reports ───────────────────────────────────────
    _spinner("Generating reports")

    txt_path  = save_text_report(result, path_a, path_b)
    html_path = save_html_report(result, doc_a['raw'], doc_b['raw'],
                                  path_a, path_b) if save_html else None
    json_path = save_json_report(result, path_a, path_b) if save_json else None

    # ── Step 5: Console output ────────────────────────────────
    if verbose:
        print_console_report(result, path_a, path_b)
        print(f"  📄 Text report : {txt_path}")
        if html_path:
            print(f"  🌐 HTML report : {html_path}")
        if json_path:
            print(f"  📦 JSON report : {json_path}")
        print()

    return result


# ──────────────────────────────────────────────────────────────
#  CLI
# ──────────────────────────────────────────────────────────────

def main():
    _banner()

    parser = argparse.ArgumentParser(
        description='Plagiarism Detector using KMP, Rabin-Karp, Jaccard & Cosine Similarity'
    )
    parser.add_argument('-a', '--original',  default=DEFAULT_A,
                        help='Path to original (reference) document')
    parser.add_argument('-b', '--submitted', default=DEFAULT_B,
                        help='Path to submitted (suspect) document')
    parser.add_argument('--algorithm', choices=['kmp', 'rabin_karp', 'both'],
                        default='both', help='String matching algorithm to use')
    parser.add_argument('--no-html',   action='store_true',
                        help='Skip HTML report generation')
    parser.add_argument('--no-json',   action='store_true',
                        help='Skip JSON report generation')
    parser.add_argument('--demo',      action='store_true',
                        help='Run with built-in sample documents')

    # Also allow positional: main.py original.txt submitted.txt
    parser.add_argument('positional', nargs='*')

    args = parser.parse_args()

    if args.demo or (not args.positional and
                     args.original == DEFAULT_A and
                     args.submitted == DEFAULT_B):
        path_a, path_b = DEFAULT_A, DEFAULT_B
        print(f"  Running demo with sample documents...\n")
    elif len(args.positional) == 2:
        path_a, path_b = args.positional
    else:
        path_a = args.original
        path_b = args.submitted

    run_detection(
        path_a     = path_a,
        path_b     = path_b,
        algorithm  = args.algorithm,
        save_html  = not args.no_html,
        save_json  = not args.no_json,
        verbose    = True,
    )


if __name__ == '__main__':
    main()
