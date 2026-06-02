from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tr_tokenizer.tokenizer import WORD_START  # noqa: E402


DEFAULT_CAPS = (1000, 4000, 8000, 16000, 32000, 64000, 128000)


@dataclass(frozen=True)
class SeedEntry:
    token: str
    count: int


@dataclass(frozen=True)
class CoverageRow:
    cap: int
    unique_tokens: int
    covered_count: int
    total_count: int

    @property
    def coverage(self) -> float:
        return self.covered_count / self.total_count if self.total_count else 0.0

    @property
    def uncovered_count(self) -> int:
        return self.total_count - self.covered_count


def load_seed_vocab(path: str | Path) -> list[SeedEntry]:
    entries: list[SeedEntry] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n")
        if header != "token\tcount":
            raise ValueError(f"unexpected seed header: {header!r}")
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            try:
                token, count_raw = line.rsplit("\t", 1)
            except ValueError:
                continue
            entries.append(SeedEntry(token, int(count_raw)))
    return entries


def token_category(token: str) -> str:
    if token.startswith("+") and len(token) > 1:
        return "suffix"
    if token.startswith(WORD_START):
        return "word_start"
    if len(token) == 1 and not token.isalnum():
        return "punct_or_symbol"
    return "other"


def coverage_rows(entries: list[SeedEntry], caps: tuple[int, ...]) -> list[CoverageRow]:
    total = sum(entry.count for entry in entries)
    rows: list[CoverageRow] = []
    running = 0
    index = 0
    sorted_caps = tuple(sorted(set(cap for cap in caps if cap > 0)))
    for cap in sorted_caps:
        while index < min(cap, len(entries)):
            running += entries[index].count
            index += 1
        rows.append(
            CoverageRow(
                cap=cap,
                unique_tokens=min(cap, len(entries)),
                covered_count=running,
                total_count=total,
            )
        )
    return rows


def category_summary(entries: list[SeedEntry]) -> dict[str, tuple[int, int]]:
    unique_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    for entry in entries:
        category = token_category(entry.token)
        unique_counts[category] += 1
        token_counts[category] += entry.count
    return {
        category: (unique_counts[category], token_counts[category])
        for category in sorted(unique_counts)
    }


def category_coverage_at_cap(entries: list[SeedEntry], cap: int) -> dict[str, tuple[int, int]]:
    selected = entries[:cap]
    unique_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    for entry in selected:
        category = token_category(entry.token)
        unique_counts[category] += 1
        token_counts[category] += entry.count
    return {
        category: (unique_counts[category], token_counts[category])
        for category in sorted(unique_counts)
    }


def _fmt_float(value: float, digits: int = 6) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    *,
    seed_path: Path,
    entries: list[SeedEntry],
    caps: tuple[int, ...],
    reference_cap: int,
) -> str:
    total_count = sum(entry.count for entry in entries)
    categories = category_summary(entries)
    reference_categories = category_coverage_at_cap(entries, reference_cap)
    lines = [
        "# v2.0 Soft Morph Seed Vocabulary Analysis",
        "",
        f"Seed vocab: `{seed_path.as_posix()}`",
        "",
        "This report summarizes the private seed vocabulary without listing raw",
        "corpus tokens. It is used to decide how much of the custom morphology",
        "piece inventory should be seeded into a learned tokenizer.",
        "",
        "## Inventory Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| unique seed tokens | {len(entries)} |",
        f"| total seed token count | {total_count} |",
        "",
        "## Coverage By Vocabulary Cap",
        "",
        "| Cap | Unique kept | Covered token count | Uncovered token count | Coverage |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in coverage_rows(entries, caps):
        lines.append(
            f"| {row.cap} | {row.unique_tokens} | {row.covered_count} | "
            f"{row.uncovered_count} | {_fmt_float(row.coverage)} |"
        )

    lines.extend(
        [
            "",
            "## Category Summary",
            "",
            "| Category | Unique tokens | Token count | Share |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for category, (unique, count) in categories.items():
        share = count / total_count if total_count else 0.0
        lines.append(f"| {category} | {unique} | {count} | {_fmt_float(share)} |")

    lines.extend(
        [
            "",
            f"## Category Coverage At Cap {reference_cap}",
            "",
            "| Category | Unique kept | Covered token count | Covered share of all tokens |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for category, (unique, count) in reference_categories.items():
        share = count / total_count if total_count else 0.0
        lines.append(f"| {category} | {unique} | {count} | {_fmt_float(share)} |")

    lines.extend(
        [
            "",
            "## Decision Hint",
            "",
            "If a 64k seed cap already covers most seed-token occurrences, then the",
            "remaining pressure is mostly from rare surface pieces and whitespace",
            "serialization. If coverage is low, the learned-vocab path must either",
            "seed fewer morphology pieces and rely on merges, or increase the vocab",
            "budget before tiny-LM comparison.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Analyze v2.0 soft morph seed vocabulary coverage.")
    parser.add_argument(
        "--seed",
        default="artifacts/private/v2_0_soft_morph/soft_morph_seed_vocab.train.tsv",
    )
    parser.add_argument("--out", default="artifacts/v2_0_soft_morph_seed_vocab_analysis.md")
    parser.add_argument(
        "--caps",
        default=",".join(str(cap) for cap in DEFAULT_CAPS),
        help="Comma-separated vocabulary caps.",
    )
    parser.add_argument("--reference-cap", type=int, default=64000)
    args = parser.parse_args(argv)

    caps = tuple(int(item.strip()) for item in args.caps.split(",") if item.strip())
    entries = load_seed_vocab(args.seed)
    report = format_report(
        seed_path=Path(args.seed),
        entries=entries,
        caps=caps,
        reference_cap=args.reference_cap,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
