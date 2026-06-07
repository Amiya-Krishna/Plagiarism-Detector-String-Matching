"""
Report Generator
================
Produces:
  1. Console-friendly colored text report
  2. Plain-text .txt report saved to outputs/
  3. HTML report with highlighted matched sentences
"""

import os
import json
from datetime import datetime


REPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')


def _ensure_output_dir():
    os.makedirs(REPORT_DIR, exist_ok=True)


# ──────────────────────────────────────────────────────────────
#  ANSI Colors for terminal
# ──────────────────────────────────────────────────────────────
class C:
    RESET  = '\033[0m'
    BOLD   = '\033[1m'
    RED    = '\033[91m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    CYAN   = '\033[96m'
    ORANGE = '\033[38;5;208m'
    GREY   = '\033[90m'


def _verdict_color(color: str) -> str:
    return {
        'green' : C.GREEN,
        'yellow': C.YELLOW,
        'orange': C.ORANGE,
        'red'   : C.RED,
    }.get(color, C.RESET)


# ──────────────────────────────────────────────────────────────
#  1. Console Report
# ──────────────────────────────────────────────────────────────

def print_console_report(result: dict, doc_a_path: str, doc_b_path: str):
    """Print a formatted, color-coded report to the terminal."""
    vc = _verdict_color(result['verdict_color'])
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{C.CYAN}{C.BOLD}{'═'*60}")
    print(f"   PLAGIARISM DETECTION REPORT")
    print(f"{'═'*60}{C.RESET}")
    print(f"{C.GREY}Generated : {now}{C.RESET}")
    print(f"  Original  : {os.path.basename(doc_a_path)}")
    print(f"  Submitted : {os.path.basename(doc_b_path)}")

    print(f"\n{C.CYAN}{'─'*60}{C.RESET}")
    print(f"  METRIC SCORES")
    print(f"{C.CYAN}{'─'*60}{C.RESET}")
    print(f"  Sentence Match   : {result['sentence_match_score']:>6.1f}%  (weight 40%)")
    print(f"  Jaccard Shingles : {result['jaccard_score']:>6.1f}%  (weight 25%)")
    print(f"  Cosine Similarity: {result['cosine_score']:>6.1f}%  (weight 20%)")
    print(f"  N-gram Overlap   : {result['ngram_overlap_score']:>6.1f}%  (weight 15%)")

    print(f"\n{C.CYAN}{'─'*60}{C.RESET}")
    pct = result['plagiarism_percentage']
    bar_filled = int(pct / 2)                      # 50 chars = 100%
    bar = '█' * bar_filled + '░' * (50 - bar_filled)
    print(f"  {vc}PLAGIARISM : {pct:.1f}%{C.RESET}")
    print(f"  [{vc}{bar}{C.RESET}]")
    print(f"  VERDICT    : {vc}{C.BOLD}{result['verdict']}{C.RESET}")

    print(f"\n{C.CYAN}{'─'*60}{C.RESET}")
    print(f"  MATCHED SENTENCES  ({result['matched_count']} / {result['total_sentences_b']})")
    print(f"{C.CYAN}{'─'*60}{C.RESET}")
    if result['matched_sentences']:
        for i, s in enumerate(result['matched_sentences'], 1):
            print(f"  {C.RED}[{i}] {s[:120]}{'...' if len(s)>120 else ''}{C.RESET}")
    else:
        print(f"  {C.GREEN}No verbatim sentence matches found.{C.RESET}")

    print(f"{C.CYAN}{'═'*60}{C.RESET}\n")


# ──────────────────────────────────────────────────────────────
#  2. Text File Report
# ──────────────────────────────────────────────────────────────

def save_text_report(result: dict, doc_a_path: str, doc_b_path: str) -> str:
    """Save a plain-text report and return the file path."""
    _ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"report_{timestamp}.txt"
    filepath  = os.path.join(REPORT_DIR, filename)

    lines = [
        "=" * 60,
        "  PLAGIARISM DETECTION REPORT",
        "=" * 60,
        f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Original  : {doc_a_path}",
        f"Submitted : {doc_b_path}",
        "",
        "METRIC SCORES",
        "-" * 40,
        f"  Sentence Match Score : {result['sentence_match_score']:.1f}%",
        f"  Jaccard Similarity   : {result['jaccard_score']:.1f}%",
        f"  Cosine Similarity    : {result['cosine_score']:.1f}%",
        f"  N-gram Overlap       : {result['ngram_overlap_score']:.1f}%",
        "",
        f"  PLAGIARISM PERCENTAGE : {result['plagiarism_percentage']:.1f}%",
        f"  VERDICT               : {result['verdict']}",
        "",
        f"MATCHED SENTENCES  ({result['matched_count']} / {result['total_sentences_b']})",
        "-" * 40,
    ]

    for i, s in enumerate(result['matched_sentences'], 1):
        lines.append(f"  [{i}] {s}")

    if not result['matched_sentences']:
        lines.append("  No verbatim matches found.")

    lines.append("=" * 60)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return filepath


# ──────────────────────────────────────────────────────────────
#  3. HTML Report  (opens in browser)
# ──────────────────────────────────────────────────────────────

def save_html_report(result: dict,
                      doc_a_raw: str,
                      doc_b_raw: str,
                      doc_a_path: str,
                      doc_b_path: str) -> str:
    """
    Generate an HTML report with matched sentences highlighted in red
    inside the submitted document text.
    """
    _ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"report_{timestamp}.html"
    filepath  = os.path.join(REPORT_DIR, filename)

    # Highlight matched sentences in the submitted doc
    highlighted_b = doc_b_raw
    for s in result['matched_sentences']:
        safe = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        orig = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        highlighted_b = highlighted_b.replace(
            s, f'<mark class="plagiarized">{orig}</mark>'
        )

    # Escape the rest for safe HTML rendering
    def safe_html(text: str) -> str:
        # Only escape if not already processed
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')

    pct   = result['plagiarism_percentage']
    color_map = {'green':'#22c55e','yellow':'#eab308','orange':'#f97316','red':'#ef4444'}
    badge_color = color_map.get(result['verdict_color'], '#6b7280')

    matched_html = ''.join(
        f'<li>{s}</li>' for s in result['matched_sentences']
    ) or '<li>No verbatim matches found.</li>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Plagiarism Report</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
  .container {{ max-width: 960px; margin: auto; padding: 2rem; }}
  h1 {{ color: #38bdf8; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }}
  .metric {{ display: flex; justify-content: space-between; padding: .4rem 0; border-bottom: 1px solid #334155; }}
  .verdict {{ font-size: 1.6rem; font-weight: 800; color: {badge_color}; }}
  .pct {{ font-size: 3rem; font-weight: 900; color: {badge_color}; }}
  progress {{ width: 100%; height: 18px; border-radius: 9px; accent-color: {badge_color}; }}
  mark.plagiarized {{ background: #7f1d1d; color: #fca5a5; padding: 2px 0; border-radius: 2px; }}
  pre {{ white-space: pre-wrap; word-wrap: break-word; font-size: .85rem; line-height: 1.6; }}
  li {{ margin: .5rem 0; color: #fca5a5; }}
  .tag {{ background: #334155; padding: .2rem .6rem; border-radius: 4px; font-size:.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>🔍 Plagiarism Detection Report</h1>
  <p class="tag">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

  <div class="card">
    <div class="pct">{pct:.1f}%</div>
    <div class="verdict">{result['verdict']}</div>
    <br>
    <progress value="{pct}" max="100"></progress>
  </div>

  <div class="card">
    <h2>📊 Metric Breakdown</h2>
    <div class="metric"><span>Sentence Match Score</span><span>{result['sentence_match_score']:.1f}%</span></div>
    <div class="metric"><span>Jaccard Similarity (Shingles)</span><span>{result['jaccard_score']:.1f}%</span></div>
    <div class="metric"><span>Cosine Similarity (TF vectors)</span><span>{result['cosine_score']:.1f}%</span></div>
    <div class="metric"><span>N-gram Overlap</span><span>{result['ngram_overlap_score']:.1f}%</span></div>
    <div class="metric"><span>Matched Sentences</span><span>{result['matched_count']} / {result['total_sentences_b']}</span></div>
  </div>

  <div class="card">
    <h2>🚨 Matched Sentences</h2>
    <ul>{matched_html}</ul>
  </div>

  <div class="card">
    <h2>📄 Submitted Document (highlighted)</h2>
    <pre>{highlighted_b}</pre>
  </div>
</div>
</body>
</html>"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return filepath


# ──────────────────────────────────────────────────────────────
#  4. JSON export (for API / frontend use)
# ──────────────────────────────────────────────────────────────

def save_json_report(result: dict, doc_a_path: str, doc_b_path: str) -> str:
    """Save result dict as JSON and return file path."""
    _ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath  = os.path.join(REPORT_DIR, f"report_{timestamp}.json")
    payload   = {
        'timestamp' : datetime.now().isoformat(),
        'original'  : doc_a_path,
        'submitted' : doc_b_path,
        **result,
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
    return filepath
