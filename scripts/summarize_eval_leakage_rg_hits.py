from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.check_eval_leakage import (  # noqa: E402
    load_eval_set,
    normalize_for_leakage,
    word_shingles,
)


@dataclass(frozen=True)
class HitLine:
    line_no: int | None
    text: str


def contains_subtuple(haystack: tuple[str, ...], needle: tuple[str, ...]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    limit = len(haystack) - len(needle) + 1
    return any(haystack[index : index + len(needle)] == needle for index in range(limit))


def parse_rg_line(line: str, *, text_field: str) -> HitLine:
    line_no: int | None = None
    payload = line.rstrip("\n")
    match = re.match(r"^(\d+):(.*)$", payload, flags=re.DOTALL)
    if match:
        line_no = int(match.group(1))
        payload = match.group(2)

    text = payload
    try:
        item = json.loads(payload)
        value = item.get(text_field)
        if isinstance(value, str):
            text = value
    except json.JSONDecodeError:
        pass

    return HitLine(line_no=line_no, text=text)


def load_hit_lines(path: Path, *, text_field: str) -> list[HitLine]:
    hits: list[HitLine] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            if raw_line.strip():
                hits.append(parse_rg_line(raw_line, text_field=text_field))
    return hits


def short_text(text: str, *, max_chars: int = 140) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3] + "..."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize rg candidate hits from full eval leakage scans."
    )
    parser.add_argument("--hits", required=True)
    parser.add_argument("--gold", required=True)
    parser.add_argument("--challenge", required=True)
    parser.add_argument("--ngram", type=int, default=8)
    parser.add_argument("--min-words", type=int, default=3)
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--out")
    args = parser.parse_args(argv)

    cases = []
    cases.extend(
        load_eval_set(
            args.gold,
            set_name="gold",
            ngram_size=args.ngram,
            min_case_words=args.min_words,
        )
    )
    cases.extend(
        load_eval_set(
            args.challenge,
            set_name="challenge",
            ngram_size=args.ngram,
            min_case_words=args.min_words,
        )
    )
    hits = load_hit_lines(Path(args.hits), text_field=args.text_field)

    full_matches: dict[tuple[str, int], set[int | None]] = defaultdict(set)
    partial_matches: dict[tuple[str, int], set[int | None]] = defaultdict(set)
    partial_shingles: dict[tuple[str, int], set[tuple[str, ...]]] = defaultdict(set)

    for hit in hits:
        hit_words = tuple(normalize_for_leakage(hit.text).split())
        if not hit_words:
            continue
        hit_shingles_by_size: dict[int, set[tuple[str, ...]]] = {}
        for case in cases:
            key = (case.set_name, case.row)
            if contains_subtuple(hit_words, case.words):
                full_matches[key].add(hit.line_no)
                continue
            size = case.shingle_size
            if size not in hit_shingles_by_size:
                hit_shingles_by_size[size] = word_shingles(hit_words, ngram_size=size)
            matched = case.shingles.intersection(hit_shingles_by_size[size])
            if matched:
                partial_matches[key].add(hit.line_no)
                partial_shingles[key].update(matched)

    by_key = {(case.set_name, case.row): case for case in cases}
    lines: list[str] = []
    lines.append("# Full Corpus Eval Leakage Candidate Summary")
    lines.append("")
    lines.append(f"Candidate rg hit lines: `{len(hits)}`")
    lines.append(f"Eval cases checked: `{len(cases)}`")
    lines.append(f"Minimum words: `{args.min_words}`")
    lines.append(f"Word shingle size: `{args.ngram}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Eval set | Full-case matches | Partial n-gram cases |")
    lines.append("| --- | ---: | ---: |")
    for set_name in ("gold", "challenge"):
        full_count = sum(1 for key in full_matches if key[0] == set_name)
        partial_count = sum(1 for key in partial_matches if key[0] == set_name)
        lines.append(f"| {set_name} | {full_count} | {partial_count} |")

    def append_section(title: str, matches: dict[tuple[str, int], set[int | None]]) -> None:
        lines.append("")
        lines.append(f"## {title}")
        if not matches:
            lines.append("")
            lines.append("No matches.")
            return
        for key in sorted(matches):
            case = by_key[key]
            line_list = sorted(line for line in matches[key] if line is not None)
            line_preview = ", ".join(str(line) for line in line_list[:8])
            if len(line_list) > 8:
                line_preview += ", ..."
            lines.append("")
            lines.append(
                f"- {case.set_name} row `{case.row}` category `{case.category}` "
                f"corpus_lines `{line_preview or 'unknown'}`"
            )
            lines.append(f"  - eval: `{short_text(case.text)}`")
            if key in partial_shingles:
                shingle_preview = [
                    " ".join(shingle)
                    for shingle in sorted(partial_shingles[key])[:3]
                ]
                lines.append(f"  - matched shingles: `{'; '.join(shingle_preview)}`")

    append_section("Full-Case Matches", full_matches)
    append_section("Partial N-Gram Matches", partial_matches)

    report = "\n".join(lines) + "\n"
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"wrote_summary: {out}")
    try:
        sys.stdout.write(report)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
