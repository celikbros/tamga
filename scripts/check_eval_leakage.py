from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402


WORD_RE = re.compile(r"\w+", re.UNICODE)
KNOWN_EVAL_CATEGORIES = {
    "ambiguity",
    "code_mixed",
    "default",
    "informal",
    "negative_word",
    "numbers_dates",
    "proper_name",
    "punctuation",
    "question",
    "softening",
    "suffix_chain",
    "verb_future",
    "verb_past",
}


@dataclass
class LeakageCase:
    set_name: str
    row: int
    text: str
    category: str
    words: tuple[str, ...]
    shingle_size: int
    shingles: set[tuple[str, ...]]
    found_shingles: set[tuple[str, ...]] = field(default_factory=set)
    raw_exact: bool = False
    normalized_full: bool = False
    snippet: str | None = None

    @property
    def overlap_ratio(self) -> float:
        if not self.shingles:
            return 0.0
        return len(self.found_shingles) / len(self.shingles)

    @property
    def partial_overlap(self) -> bool:
        return 0.0 < self.overlap_ratio < 1.0


def turkish_lower(text: str) -> str:
    chars: list[str] = []
    for char in text:
        if char == "I":
            chars.append("ı")
        elif char == "İ":
            chars.append("i")
        else:
            chars.append(char.lower())
    return "".join(chars)


def turkish_upper(text: str) -> str:
    chars: list[str] = []
    for char in text:
        if char == "i":
            chars.append("İ")
        elif char == "ı":
            chars.append("I")
        else:
            chars.append(char.upper())
    return "".join(chars)


def normalize_for_leakage(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text)
    normalized = turkish_lower(normalized)
    words = WORD_RE.findall(normalized)
    return " ".join(words)


def word_shingles(words: tuple[str, ...], *, ngram_size: int) -> set[tuple[str, ...]]:
    if not words:
        return set()
    size = min(ngram_size, len(words))
    return {
        tuple(words[index : index + size])
        for index in range(0, len(words) - size + 1)
    }


def find_exact_leakage(train_lines: list[str], eval_texts: list[str]) -> list[str]:
    train_set = {line.strip() for line in train_lines if line.strip()}
    return sorted({text for text in eval_texts if text in train_set})


def make_leakage_case(
    *,
    set_name: str,
    row: int,
    text: str,
    category: str,
    ngram_size: int,
) -> LeakageCase | None:
    words = tuple(normalize_for_leakage(text).split())
    if not words:
        return None
    shingles = word_shingles(words, ngram_size=ngram_size)
    return LeakageCase(
        set_name=set_name,
        row=row,
        text=text,
        category=category,
        words=words,
        shingle_size=min(ngram_size, len(words)),
        shingles=shingles,
    )


def load_eval_set(
    path: str | Path,
    *,
    set_name: str,
    ngram_size: int,
    text_col: int | None = None,
    has_header: bool = False,
) -> list[LeakageCase]:
    source = Path(path)
    cases: list[LeakageCase] = []

    if text_col is None:
        eval_cases = load_cases(source)
        for row, case in enumerate(eval_cases, start=1):
            leakage_case = make_leakage_case(
                set_name=set_name,
                row=row,
                text=case.text,
                category=case.category,
                ngram_size=ngram_size,
            )
            if leakage_case is not None:
                cases.append(leakage_case)
        return cases

    with source.open("r", encoding="utf-8") as handle:
        for row, raw_line in enumerate(handle, start=1):
            if row == 1 and has_header:
                continue
            line = raw_line.rstrip("\n")
            if not line:
                continue
            fields = line.split("\t")
            if text_col >= len(fields):
                raise ValueError(f"{source}:{row}: text_col {text_col} is out of range")
            if (
                text_col == 0
                and len(fields) == 3
                and fields[0] in KNOWN_EVAL_CATEGORIES
                and fields[2].lstrip().startswith("[")
            ):
                raise ValueError(
                    f"{source}:{row}: --text-col 0 selects the category column "
                    f"({fields[0]!r}), not the eval text. Omit --text-col for "
                    "repo eval TSV files, or use --text-col 1 for raw TSV mode."
                )
            if text_col == len(fields) - 1 and fields[text_col].lstrip().startswith("["):
                raise ValueError(
                    f"{source}:{row}: --text-col {text_col} appears to select "
                    "the expected-token JSON column, not the eval text."
                )
            leakage_case = make_leakage_case(
                set_name=set_name,
                row=row,
                text=fields[text_col],
                category="default",
                ngram_size=ngram_size,
            )
            if leakage_case is not None:
                cases.append(leakage_case)
    return cases


def _snippet(words: list[str], start: int, length: int, *, window: int = 6) -> str:
    begin = max(0, start - window)
    end = min(len(words), start + length + window)
    return " ".join(words[begin:end])


def _iter_jsonl_texts(path: Path, *, text_field: str) -> Iterator[str]:
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = item.get(text_field)
            if isinstance(text, str) and text:
                yield text


def _iter_text_lines(path: Path) -> Iterator[str]:
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            text = raw_line.strip()
            if text:
                yield text


def iter_corpus_texts(
    path: str | Path,
    *,
    corpus_format: str,
    text_field: str,
    parse_jsonl: bool,
) -> Iterator[str]:
    source = Path(path)
    if corpus_format == "jsonl":
        if parse_jsonl:
            yield from _iter_jsonl_texts(source, text_field=text_field)
        else:
            yield from _iter_text_lines(source)
    elif corpus_format == "text":
        yield from _iter_text_lines(source)
    else:
        raise ValueError(f"unsupported corpus format: {corpus_format}")


def build_indexes(
    cases: list[LeakageCase],
) -> tuple[
    dict[str, list[LeakageCase]],
    dict[str, list[LeakageCase]],
    dict[str, list[tuple[tuple[str, ...], LeakageCase]]],
    re.Pattern[str] | None,
]:
    raw_prefix_index: dict[str, list[LeakageCase]] = defaultdict(list)
    full_first_index: dict[str, list[LeakageCase]] = defaultdict(list)
    shingle_first_index: dict[str, list[tuple[tuple[str, ...], LeakageCase]]] = (
        defaultdict(list)
    )
    prefilter_words: set[str] = set()

    for case in cases:
        prefix = case.text[: min(16, len(case.text))]
        if prefix:
            raw_prefix_index[prefix].append(case)
        full_first_index[case.words[0]].append(case)
        for shingle in case.shingles:
            shingle_first_index[shingle[0]].append((shingle, case))
        markers = [word for word in case.words if len(word) >= 4] or list(case.words)
        for word in markers:
            prefilter_words.add(word)
            prefilter_words.add(turkish_upper(word))
            prefilter_words.add(word.capitalize())

    prefilter_re = None
    if prefilter_words:
        pattern = "|".join(
            re.escape(word)
            for word in sorted(prefilter_words, key=lambda item: (-len(item), item))
        )
        prefilter_re = re.compile(pattern, re.IGNORECASE | re.UNICODE)

    return raw_prefix_index, full_first_index, shingle_first_index, prefilter_re


def scan_corpus_text(
    text: str,
    *,
    raw_prefix_index: dict[str, list[LeakageCase]],
    full_first_index: dict[str, list[LeakageCase]],
    shingle_first_index: dict[str, list[tuple[tuple[str, ...], LeakageCase]]],
    prefilter_re: re.Pattern[str] | None = None,
) -> None:
    if prefilter_re is not None and not prefilter_re.search(text):
        return

    for prefix, matching_cases in raw_prefix_index.items():
        if prefix not in text:
            continue
        for case in matching_cases:
            if not case.raw_exact and case.text in text:
                case.raw_exact = True
                case.snippet = text[:240]

    words = normalize_for_leakage(text).split()
    if not words:
        return

    for index, word in enumerate(words):
        for case in full_first_index.get(word, []):
            size = len(case.words)
            if index + size <= len(words) and tuple(words[index : index + size]) == case.words:
                case.normalized_full = True
                if case.snippet is None:
                    case.snippet = _snippet(words, index, size)

        for shingle, case in shingle_first_index.get(word, []):
            size = len(shingle)
            if index + size > len(words):
                continue
            if tuple(words[index : index + size]) != shingle:
                continue
            case.found_shingles.add(shingle)
            if case.snippet is None:
                case.snippet = _snippet(words, index, size)


def scan_corpus(
    corpus_path: str | Path,
    *,
    cases: list[LeakageCase],
    corpus_format: str,
    text_field: str,
    parse_jsonl: bool,
    progress: int,
    max_docs: int | None = None,
) -> int:
    raw_prefix_index, full_first_index, shingle_first_index, prefilter_re = build_indexes(
        cases
    )
    scanned = 0
    for text in iter_corpus_texts(
        corpus_path,
        corpus_format=corpus_format,
        text_field=text_field,
        parse_jsonl=parse_jsonl,
    ):
        scanned += 1
        scan_corpus_text(
            text,
            raw_prefix_index=raw_prefix_index,
            full_first_index=full_first_index,
            shingle_first_index=shingle_first_index,
            prefilter_re=prefilter_re,
        )
        if progress > 0 and scanned % progress == 0:
            print(f"scanned {scanned:,} corpus records...", file=sys.stderr)
        if max_docs is not None and scanned >= max_docs:
            break
    return scanned


def summarize_cases(
    cases: list[LeakageCase],
    *,
    min_full_words: int = 3,
) -> dict[str, dict[str, int]]:
    by_set: dict[str, list[LeakageCase]] = defaultdict(list)
    for case in cases:
        by_set[case.set_name].append(case)

    summary: dict[str, dict[str, int]] = {}
    for set_name, set_cases in sorted(by_set.items()):
        raw_exact = sum(case.raw_exact for case in set_cases)
        normalized_full = sum(
            case.normalized_full and len(case.words) >= min_full_words
            for case in set_cases
        )
        short_full = sum(
            case.normalized_full and len(case.words) < min_full_words
            for case in set_cases
        )
        partial = sum(
            case.partial_overlap and not case.normalized_full for case in set_cases
        )
        leaked = sum(
            case.raw_exact
            or (case.normalized_full and len(case.words) >= min_full_words)
            or case.partial_overlap
            for case in set_cases
        )
        summary[set_name] = {
            "total": len(set_cases),
            "raw_exact": raw_exact,
            "normalized_full": normalized_full,
            "short_full": short_full,
            "partial": partial,
            "clean": len(set_cases) - leaked,
        }
    return summary


def format_report(
    *,
    corpus_path: Path,
    scanned_records: int,
    cases: list[LeakageCase],
    ngram_size: int,
    min_full_words: int,
    max_examples: int,
    include_snippets: bool,
) -> str:
    summary = summarize_cases(cases, min_full_words=min_full_words)
    lines = [
        "# Eval Leakage Report",
        "",
        f"Corpus: `{corpus_path}`",
        f"Scanned records: `{scanned_records}`",
        f"Word shingle size: `{ngram_size}` with short-sentence fallback",
        f"Strict normalized-full minimum words: `{min_full_words}`",
        "Normalization: NFC + Turkish-aware lowercase + word-token extraction",
        "",
        "## Summary",
        "",
        "| Eval set | Total | Raw exact | Normalized full | Short full | Partial n-gram | Clean | Policy |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for set_name in sorted(summary):
        row = summary[set_name]
        policy = "strict" if "gold" in set_name else "informational"
        lines.append(
            f"| {set_name} | {row['total']} | {row['raw_exact']} | "
            f"{row['normalized_full']} | {row['short_full']} | "
            f"{row['partial']} | {row['clean']} | {policy} |"
        )

    lines.extend(
        [
            "",
            "## Hit Details",
            "",
            "Gold/frozen hits should be removed from the training corpus, not from the eval set.",
            "Challenge hits are reported for transparency and should not be used as headline claims.",
        ]
    )

    for set_name in sorted({case.set_name for case in cases}):
        set_cases = [case for case in cases if case.set_name == set_name]
        hits = [
            case
            for case in set_cases
            if case.raw_exact or case.normalized_full or case.partial_overlap
        ]
        hits.sort(
            key=lambda case: (
                not (case.raw_exact or case.normalized_full),
                -case.overlap_ratio,
                case.row,
            )
        )
        lines.extend(["", f"### {set_name}", ""])
        if not hits:
            lines.append("No leakage or partial overlap hits.")
            continue
        for case in hits[:max_examples]:
            flags = []
            if case.raw_exact:
                flags.append("raw_exact")
            if case.normalized_full:
                if len(case.words) >= min_full_words:
                    flags.append("normalized_full")
                else:
                    flags.append("short_full")
            if case.partial_overlap and not case.normalized_full:
                flags.append(f"partial_{case.overlap_ratio:.2f}")
            lines.extend(
                [
                    f"- row `{case.row}` category `{case.category}` "
                    f"flags `{', '.join(flags)}`",
                    f"  - eval: `{case.text}`",
                ]
            )
            if include_snippets and case.snippet:
                lines.append(f"  - corpus snippet: `{case.snippet[:240]}`")
            elif case.snippet:
                lines.append("  - corpus snippet: omitted from public report")
        if len(hits) > max_examples:
            lines.append(f"- ... {len(hits) - max_examples} additional hits omitted")

    lines.append("")
    return "\n".join(lines)


def infer_corpus_format(path: Path) -> str:
    if path.suffix.lower() == ".jsonl":
        return "jsonl"
    return "text"


def check_files(train_path: str | Path, eval_path: str | Path) -> list[str]:
    train_lines = Path(train_path).read_text(encoding="utf-8").splitlines()
    eval_texts = [case.text for case in load_cases(eval_path)]
    return find_exact_leakage(train_lines, eval_texts)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Check visible eval leakage in a text or JSONL corpus."
    )
    parser.add_argument("legacy_train_path", nargs="?")
    parser.add_argument("legacy_eval_path", nargs="?")
    parser.add_argument("--corpus")
    parser.add_argument("--gold")
    parser.add_argument("--challenge")
    parser.add_argument("--corpus-format", choices=["text", "jsonl"])
    parser.add_argument("--text-field", default="text")
    parser.add_argument(
        "--parse-jsonl",
        action="store_true",
        help="Parse JSONL and scan only text-field. Default scans raw JSONL lines for speed.",
    )
    parser.add_argument("--text-col", type=int)
    parser.add_argument("--has-header", action="store_true")
    parser.add_argument("--ngram", type=int, default=8)
    parser.add_argument("--min-full-words", type=int, default=3)
    parser.add_argument("--progress", type=int, default=100000)
    parser.add_argument("--max-docs", type=int)
    parser.add_argument("--report-out")
    parser.add_argument("--max-examples", type=int, default=25)
    parser.add_argument(
        "--include-snippets",
        action="store_true",
        help="Include corpus snippets in the report. Keep off for public artifacts.",
    )
    args = parser.parse_args(argv)

    if args.legacy_train_path and args.legacy_eval_path and not args.corpus:
        leaks = check_files(args.legacy_train_path, args.legacy_eval_path)
        if not leaks:
            print("no exact leakage found")
            return 0
        print("exact leakage found")
        for text in leaks:
            print(text)
        return 1

    if not args.corpus:
        parser.error("--corpus is required unless using legacy positional mode")

    cases: list[LeakageCase] = []
    if args.gold:
        cases.extend(
            load_eval_set(
                args.gold,
                set_name="gold",
                ngram_size=args.ngram,
                text_col=args.text_col,
                has_header=args.has_header,
            )
        )
    if args.challenge:
        cases.extend(
            load_eval_set(
                args.challenge,
                set_name="challenge",
                ngram_size=args.ngram,
                text_col=args.text_col,
                has_header=args.has_header,
            )
        )
    if not cases:
        parser.error("at least one of --gold or --challenge must be provided")

    corpus_path = Path(args.corpus)
    corpus_format = args.corpus_format or infer_corpus_format(corpus_path)
    scanned_records = scan_corpus(
        corpus_path,
        cases=cases,
        corpus_format=corpus_format,
        text_field=args.text_field,
        parse_jsonl=args.parse_jsonl,
        progress=args.progress,
        max_docs=args.max_docs,
    )
    report = format_report(
        corpus_path=corpus_path,
        scanned_records=scanned_records,
        cases=cases,
        ngram_size=args.ngram,
        min_full_words=args.min_full_words,
        max_examples=args.max_examples,
        include_snippets=args.include_snippets,
    )
    if args.report_out:
        report_path = Path(args.report_out)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"wrote_report: {report_path}")
    print(report)
    summary = summarize_cases(cases, min_full_words=args.min_full_words)
    gold = summary.get("gold")
    if gold and (gold["raw_exact"] or gold["normalized_full"] or gold["partial"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
