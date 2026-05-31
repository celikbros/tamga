from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import argparse
import hashlib
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path
from typing import Any


TURKISH_STOPWORDS = {
    "ve",
    "bir",
    "bu",
    "da",
    "de",
    "ile",
    "için",
    "olarak",
    "olan",
    "daha",
    "çok",
    "sonra",
    "kadar",
    "gibi",
    "ise",
    "her",
    "en",
    "ama",
    "ya",
    "veya",
}

ENGLISH_STOPWORDS = {
    "the",
    "and",
    "of",
    "to",
    "in",
    "a",
    "is",
    "that",
    "for",
    "on",
    "with",
    "as",
    "by",
    "this",
    "from",
    "or",
    "an",
    "be",
    "are",
    "was",
}

TURKISH_SPECIFIC = set("çğıöşüÇĞİÖŞÜ")
MOJIBAKE_MARKERS = ("Ã", "Ä", "Å", "â€", "ðŸ", "\ufffd")
URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
HTML_RE = re.compile(r"<[A-Za-z][^>]{0,120}>")
WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)


@dataclass
class LengthStats:
    count: int = 0
    min_chars: int = 0
    max_chars: int = 0
    avg_chars: float = 0.0
    median_chars: float = 0.0
    avg_words: float = 0.0


@dataclass
class CorpusQualityStats:
    path: Path
    scanned_lines: int = 0
    valid_json: int = 0
    invalid_json: int = 0
    missing_text: int = 0
    empty_text: int = 0
    usable_texts: int = 0
    duplicate_exact: int = 0
    duplicate_normalized: int = 0
    very_short_texts: int = 0
    long_for_sentencepiece: int = 0
    very_long_texts: int = 0
    mojibake_suspects: int = 0
    replacement_char_texts: int = 0
    url_texts: int = 0
    html_texts: int = 0
    control_char_texts: int = 0
    source_counts: Counter[str] = field(default_factory=Counter)
    language_counts: Counter[str] = field(default_factory=Counter)
    script_counts: Counter[str] = field(default_factory=Counter)
    length_stats: LengthStats = field(default_factory=LengthStats)


def _stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_for_duplicate(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", normalized).strip()


def word_tokens(text: str) -> list[str]:
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def language_hint(text: str) -> str:
    words = word_tokens(text)
    if not words:
        return "unknown"
    tr_hits = sum(1 for word in words if word in TURKISH_STOPWORDS)
    en_hits = sum(1 for word in words if word in ENGLISH_STOPWORDS)
    tr_chars = sum(1 for char in text if char in TURKISH_SPECIFIC)

    if tr_hits >= 2 and en_hits >= 2:
        return "mixed_tr_en"
    if tr_hits >= 2 or tr_chars >= 3:
        return "tr_like"
    if en_hits >= 2:
        return "en_like"
    return "unknown"


def script_hint(text: str) -> str:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return "no_letters"

    latin = cyrillic = greek = arabic = other = 0
    for char in letters:
        name = unicodedata.name(char, "")
        if "LATIN" in name:
            latin += 1
        elif "CYRILLIC" in name:
            cyrillic += 1
        elif "GREEK" in name:
            greek += 1
        elif "ARABIC" in name:
            arabic += 1
        else:
            other += 1

    counts = {
        "latin": latin,
        "cyrillic": cyrillic,
        "greek": greek,
        "arabic": arabic,
        "other": other,
    }
    primary, value = max(counts.items(), key=lambda item: item[1])
    if value / max(1, len(letters)) < 0.80:
        return "mixed_script"
    return primary


def has_control_chars(text: str) -> bool:
    return any(
        unicodedata.category(char) in {"Cc", "Cf"} and char not in "\t\n\r"
        for char in text
    )


def audit_jsonl_corpus(
    path: str | Path,
    *,
    max_lines: int | None = None,
    text_field: str = "text",
    long_threshold: int = 4192,
    very_long_threshold: int = 20000,
) -> CorpusQualityStats:
    corpus_path = Path(path)
    stats = CorpusQualityStats(path=corpus_path)
    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    char_lengths: list[int] = []
    word_lengths: list[int] = []

    with corpus_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if max_lines is not None and stats.scanned_lines >= max_lines:
                break

            stats.scanned_lines += 1
            raw = line.strip()
            if not raw:
                stats.empty_text += 1
                continue

            try:
                item = json.loads(raw)
            except json.JSONDecodeError:
                stats.invalid_json += 1
                continue
            stats.valid_json += 1
            if not isinstance(item, dict) or not isinstance(item.get(text_field), str):
                stats.missing_text += 1
                continue

            text = item[text_field].strip()
            if not text:
                stats.empty_text += 1
                continue

            stats.usable_texts += 1
            source = item.get("source")
            stats.source_counts[str(source) if source is not None else "(missing)"] += 1

            exact_hash = _stable_hash(text)
            if exact_hash in exact_seen:
                stats.duplicate_exact += 1
            else:
                exact_seen.add(exact_hash)

            normalized = normalize_for_duplicate(text)
            normalized_hash = _stable_hash(normalized)
            if normalized_hash in normalized_seen:
                stats.duplicate_normalized += 1
            else:
                normalized_seen.add(normalized_hash)

            char_len = len(text)
            word_len = len(word_tokens(text))
            char_lengths.append(char_len)
            word_lengths.append(word_len)

            if word_len < 5 or char_len < 30:
                stats.very_short_texts += 1
            if char_len > long_threshold:
                stats.long_for_sentencepiece += 1
            if char_len > very_long_threshold:
                stats.very_long_texts += 1
            if any(marker in text for marker in MOJIBAKE_MARKERS):
                stats.mojibake_suspects += 1
            if "\ufffd" in text:
                stats.replacement_char_texts += 1
            if URL_RE.search(text):
                stats.url_texts += 1
            if HTML_RE.search(text):
                stats.html_texts += 1
            if has_control_chars(text):
                stats.control_char_texts += 1

            stats.language_counts[language_hint(text)] += 1
            stats.script_counts[script_hint(text)] += 1

    if char_lengths:
        stats.length_stats = LengthStats(
            count=len(char_lengths),
            min_chars=min(char_lengths),
            max_chars=max(char_lengths),
            avg_chars=sum(char_lengths) / len(char_lengths),
            median_chars=statistics.median(char_lengths),
            avg_words=sum(word_lengths) / len(word_lengths),
        )
    return stats


def _pct(value: int, denominator: int) -> str:
    if denominator <= 0:
        return "0.0000"
    return f"{value / denominator:.4f}"


def _top_table(counter: Counter[str], *, total: int, limit: int = 20) -> list[str]:
    lines = ["| Value | Count | Rate |", "| --- | ---: | ---: |"]
    for name, count in counter.most_common(limit):
        lines.append(f"| {name} | {count} | {_pct(count, total)} |")
    if not counter:
        lines.append("| (none) | 0 | 0.0000 |")
    return lines


def format_quality_report(
    stats: CorpusQualityStats,
    *,
    max_lines: int | None,
    text_field: str,
    long_threshold: int,
) -> str:
    usable = stats.usable_texts
    lines = [
        "# JSONL Corpus Quality Audit",
        "",
        f"Path: `{stats.path}`",
        f"Text field: `{text_field}`",
        f"Scan limit: `{max_lines if max_lines is not None else 'full file'}`",
        "",
        "This report is aggregate-only. It does not publish corpus text.",
        "",
        "## Structure",
        "",
        "| Metric | Count | Rate |",
        "| --- | ---: | ---: |",
        f"| scanned_lines | {stats.scanned_lines} | 1.0000 |",
        f"| valid_json | {stats.valid_json} | {_pct(stats.valid_json, stats.scanned_lines)} |",
        f"| invalid_json | {stats.invalid_json} | {_pct(stats.invalid_json, stats.scanned_lines)} |",
        f"| missing_text | {stats.missing_text} | {_pct(stats.missing_text, stats.scanned_lines)} |",
        f"| empty_text | {stats.empty_text} | {_pct(stats.empty_text, stats.scanned_lines)} |",
        f"| usable_texts | {stats.usable_texts} | {_pct(stats.usable_texts, stats.scanned_lines)} |",
        "",
        "## Quality Signals",
        "",
        "| Signal | Count | Rate over usable |",
        "| --- | ---: | ---: |",
        f"| exact_duplicates_in_scan | {stats.duplicate_exact} | {_pct(stats.duplicate_exact, usable)} |",
        f"| normalized_duplicates_in_scan | {stats.duplicate_normalized} | {_pct(stats.duplicate_normalized, usable)} |",
        f"| very_short_texts | {stats.very_short_texts} | {_pct(stats.very_short_texts, usable)} |",
        f"| chars_over_{long_threshold} | {stats.long_for_sentencepiece} | {_pct(stats.long_for_sentencepiece, usable)} |",
        f"| chars_over_20000 | {stats.very_long_texts} | {_pct(stats.very_long_texts, usable)} |",
        f"| mojibake_suspects | {stats.mojibake_suspects} | {_pct(stats.mojibake_suspects, usable)} |",
        f"| replacement_char_texts | {stats.replacement_char_texts} | {_pct(stats.replacement_char_texts, usable)} |",
        f"| url_texts | {stats.url_texts} | {_pct(stats.url_texts, usable)} |",
        f"| html_texts | {stats.html_texts} | {_pct(stats.html_texts, usable)} |",
        f"| control_char_texts | {stats.control_char_texts} | {_pct(stats.control_char_texts, usable)} |",
        "",
        "## Lengths",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| min_chars | {stats.length_stats.min_chars} |",
        f"| median_chars | {stats.length_stats.median_chars:.1f} |",
        f"| avg_chars | {stats.length_stats.avg_chars:.1f} |",
        f"| max_chars | {stats.length_stats.max_chars} |",
        f"| avg_words | {stats.length_stats.avg_words:.1f} |",
        "",
        "## Language Hints",
        "",
        *_top_table(stats.language_counts, total=usable),
        "",
        "## Script Hints",
        "",
        *_top_table(stats.script_counts, total=usable),
        "",
        "## Sources",
        "",
        *_top_table(stats.source_counts, total=usable),
        "",
        "## Interpretation Notes",
        "",
        "- Language hints are heuristic counts, not a certified language-ID model.",
        "- `mojibake_suspects` flags actual marker characters in parsed text; terminal",
        "  mojibake alone is not counted.",
        "- `chars_over_4192` matters because SentencePiece skipped longer lines in the",
        "  local pilot unless max sentence length is changed or pre-filtering is added.",
        "- Exact/normalized duplicate counts are only within the scanned slice.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Write aggregate quality metrics for a JSONL text corpus.",
    )
    parser.add_argument("path")
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--long-threshold", type=int, default=4192)
    parser.add_argument("--markdown-out", required=True)
    args = parser.parse_args(argv)

    stats = audit_jsonl_corpus(
        args.path,
        max_lines=args.max_lines,
        text_field=args.text_field,
        long_threshold=args.long_threshold,
    )
    report = format_quality_report(
        stats,
        max_lines=args.max_lines,
        text_field=args.text_field,
        long_threshold=args.long_threshold,
    )
    out_path = Path(args.markdown_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"wrote_quality_report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
