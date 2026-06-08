from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


KIND_GROUPS = (
    "word_start",
    "suffix",
    "protected",
    "punct_or_symbol",
    "apostrophe",
    "whitespace",
    "other",
)


@dataclass
class SuffixStats:
    token: str
    surface: str
    total_count: int = 0
    soft_count: int = 0
    hard_count: int = 0
    prev_word_start_count: int = 0
    prev_suffix_count: int = 0
    prev_protected_count: int = 0
    prev_apostrophe_count: int = 0
    prev_other_count: int = 0

    @property
    def soft_share(self) -> float:
        return self.soft_count / self.total_count if self.total_count else 0.0

    @property
    def hard_share(self) -> float:
        return self.hard_count / self.total_count if self.total_count else 0.0


@dataclass(frozen=True)
class CandidateRow:
    token: str
    surface: str
    total_count: int
    soft_count: int
    hard_count: int
    non_suffix_exact_count: int
    word_start_exact_count: int
    other_exact_count: int
    surface_len: int
    soft_share: float
    hard_share: float
    exact_collision_rate: float
    recommendation: str


@dataclass(frozen=True)
class Summary:
    lines: int
    pieces: int
    suffix_unique: int
    suffix_total: int
    selected_like_unique: int
    selected_like_count: int
    seed_bias_unique: int
    seed_bias_count: int
    protected_tail_review_unique: int
    protected_tail_review_count: int


def kind_group(kind: str) -> str:
    if kind.startswith("protected:"):
        return "protected"
    if kind in KIND_GROUPS:
        return kind
    return "other"


def read_piece(item: dict[str, Any]) -> tuple[str, str, str, str]:
    token = str(item.get("token", ""))
    surface = str(item.get("surface", ""))
    kind = str(item.get("kind", "other"))
    boundary_before = str(item.get("boundary_before", "hard"))
    return token, surface, kind, boundary_before


def recommendation_for(
    stats: SuffixStats,
    *,
    non_suffix_exact_count: int,
    min_count: int,
    min_surface_len: int,
    max_collision_rate: float,
    protected_tail_hard_share: float,
) -> str:
    if stats.total_count < min_count:
        return "low_count"

    collision_rate = non_suffix_exact_count / stats.total_count if stats.total_count else 0.0
    if stats.hard_share >= protected_tail_hard_share:
        return "protected_tail_review"

    if len(stats.surface) < min_surface_len:
        return "seed_bias_candidate"

    if stats.soft_share >= 0.95 and collision_rate <= max_collision_rate:
        return "uds_or_seed_candidate"

    if stats.soft_share >= 0.80 and collision_rate <= max_collision_rate * 2:
        return "seed_bias_candidate"

    return "review"


def analyze_boundary_jsonl(
    path: Path,
    *,
    min_count: int,
    min_surface_len: int,
    max_collision_rate: float,
    protected_tail_hard_share: float,
    progress: int,
) -> tuple[list[CandidateRow], Summary]:
    suffix_stats: dict[str, SuffixStats] = {}
    surface_kind_counts: dict[str, Counter[str]] = defaultdict(Counter)

    lines = 0
    pieces_total = 0
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if not raw_line.strip():
                continue
            item = json.loads(raw_line)
            pieces = item.get("pieces", [])
            if not isinstance(pieces, list):
                continue

            previous_group = "other"
            for raw_piece in pieces:
                if not isinstance(raw_piece, dict):
                    continue
                token, surface, kind, boundary_before = read_piece(raw_piece)
                group = kind_group(kind)
                pieces_total += 1
                surface_kind_counts[surface][group] += 1

                if group == "suffix" and token.startswith("+") and len(token) > 1:
                    stats = suffix_stats.get(token)
                    if stats is None:
                        stats = SuffixStats(token=token, surface=surface)
                        suffix_stats[token] = stats
                    stats.total_count += 1
                    if boundary_before == "soft":
                        stats.soft_count += 1
                    elif boundary_before == "hard":
                        stats.hard_count += 1

                    if previous_group == "word_start":
                        stats.prev_word_start_count += 1
                    elif previous_group == "suffix":
                        stats.prev_suffix_count += 1
                    elif previous_group == "protected":
                        stats.prev_protected_count += 1
                    elif previous_group == "apostrophe":
                        stats.prev_apostrophe_count += 1
                    else:
                        stats.prev_other_count += 1

                previous_group = group

            lines += 1
            if progress > 0 and lines % progress == 0:
                print(
                    f"analyzed {lines:,} lines suffix_unique={len(suffix_stats):,} "
                    f"pieces={pieces_total:,}",
                    flush=True,
                )

    rows: list[CandidateRow] = []
    selected_like_unique = 0
    selected_like_count = 0
    seed_bias_unique = 0
    seed_bias_count = 0
    protected_tail_review_unique = 0
    protected_tail_review_count = 0
    suffix_total = 0

    for stats in suffix_stats.values():
        kind_counts = surface_kind_counts.get(stats.surface, Counter())
        suffix_exact = kind_counts.get("suffix", 0)
        word_start_exact = kind_counts.get("word_start", 0)
        non_suffix_exact = sum(kind_counts.values()) - suffix_exact
        other_exact = non_suffix_exact - word_start_exact
        collision_rate = non_suffix_exact / stats.total_count if stats.total_count else 0.0
        rec = recommendation_for(
            stats,
            non_suffix_exact_count=non_suffix_exact,
            min_count=min_count,
            min_surface_len=min_surface_len,
            max_collision_rate=max_collision_rate,
            protected_tail_hard_share=protected_tail_hard_share,
        )
        suffix_total += stats.total_count
        if rec == "uds_or_seed_candidate":
            selected_like_unique += 1
            selected_like_count += stats.total_count
        elif rec == "seed_bias_candidate":
            seed_bias_unique += 1
            seed_bias_count += stats.total_count
        elif rec == "protected_tail_review":
            protected_tail_review_unique += 1
            protected_tail_review_count += stats.total_count

        rows.append(
            CandidateRow(
                token=stats.token,
                surface=stats.surface,
                total_count=stats.total_count,
                soft_count=stats.soft_count,
                hard_count=stats.hard_count,
                non_suffix_exact_count=non_suffix_exact,
                word_start_exact_count=word_start_exact,
                other_exact_count=other_exact,
                surface_len=len(stats.surface),
                soft_share=stats.soft_share,
                hard_share=stats.hard_share,
                exact_collision_rate=collision_rate,
                recommendation=rec,
            )
        )

    rows.sort(key=lambda row: (-row.total_count, row.recommendation, row.token))
    summary = Summary(
        lines=lines,
        pieces=pieces_total,
        suffix_unique=len(suffix_stats),
        suffix_total=suffix_total,
        selected_like_unique=selected_like_unique,
        selected_like_count=selected_like_count,
        seed_bias_unique=seed_bias_unique,
        seed_bias_count=seed_bias_count,
        protected_tail_review_unique=protected_tail_review_unique,
        protected_tail_review_count=protected_tail_review_count,
    )
    return rows, summary


def write_tsv(path: Path, rows: list[CandidateRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "token\tsurface\ttotal_count\tsoft_count\thard_count\t"
            "non_suffix_exact_count\tword_start_exact_count\tother_exact_count\t"
            "surface_len\tsoft_share\thard_share\texact_collision_rate\trecommendation\n"
        )
        for row in rows:
            handle.write(
                f"{row.token}\t{row.surface}\t{row.total_count}\t"
                f"{row.soft_count}\t{row.hard_count}\t{row.non_suffix_exact_count}\t"
                f"{row.word_start_exact_count}\t{row.other_exact_count}\t"
                f"{row.surface_len}\t{row.soft_share:.6f}\t{row.hard_share:.6f}\t"
                f"{row.exact_collision_rate:.6f}\t{row.recommendation}\n"
            )


def _fmt_float(value: float, digits: int = 6) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def recommendation_counts(rows: list[CandidateRow]) -> dict[str, tuple[int, int]]:
    unique_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    for row in rows:
        unique_counts[row.recommendation] += 1
        token_counts[row.recommendation] += row.total_count
    return {
        key: (unique_counts[key], token_counts[key])
        for key in sorted(unique_counts)
    }


def format_report(
    *,
    boundary_jsonl: Path,
    private_out: Path,
    rows: list[CandidateRow],
    summary: Summary,
    min_count: int,
    min_surface_len: int,
    max_collision_rate: float,
    protected_tail_hard_share: float,
) -> str:
    rec_counts = recommendation_counts(rows)
    lines = [
        "# v2.0 Morph Seed Candidate Analysis",
        "",
        f"Boundary JSONL: `{boundary_jsonl.as_posix()}`",
        f"Private candidate TSV: `{private_out.as_posix()}`",
        "",
        "This analysis uses train-only custom morphology pieces to identify",
        "suffix/morph candidates for the next learned-tokenizer branch. It does",
        "not train a tokenizer and does not tune against visible challenge rows.",
        "",
        "## Parameters",
        "",
        "| Parameter | Value |",
        "| --- | ---: |",
        f"| min_count | {min_count} |",
        f"| min_surface_len | {min_surface_len} |",
        f"| max_collision_rate | {_fmt_float(max_collision_rate)} |",
        f"| protected_tail_hard_share | {_fmt_float(protected_tail_hard_share)} |",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| lines | {summary.lines} |",
        f"| pieces | {summary.pieces} |",
        f"| suffix unique | {summary.suffix_unique} |",
        f"| suffix occurrences | {summary.suffix_total} |",
        f"| uds_or_seed_candidate unique | {summary.selected_like_unique} |",
        f"| uds_or_seed_candidate occurrences | {summary.selected_like_count} |",
        f"| seed_bias_candidate unique | {summary.seed_bias_unique} |",
        f"| seed_bias_candidate occurrences | {summary.seed_bias_count} |",
        f"| protected_tail_review unique | {summary.protected_tail_review_unique} |",
        f"| protected_tail_review occurrences | {summary.protected_tail_review_count} |",
        "",
        "## Recommendation Buckets",
        "",
        "| Recommendation | Unique suffixes | Occurrences | Share of suffix occurrences |",
        "| --- | ---: | ---: | ---: |",
    ]
    for rec, (unique, count) in rec_counts.items():
        share = count / summary.suffix_total if summary.suffix_total else 0.0
        lines.append(f"| {rec} | {unique} | {count} | {_fmt_float(share)} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "`uds_or_seed_candidate` means the suffix is frequent, mostly introduced",
            "by soft morphology boundaries, and has low exact surface collision with",
            "non-suffix pieces in the train split.",
            "",
            "`seed_bias_candidate` means the suffix may still be useful as a learned",
            "prior, but should not be forced broadly as a user-defined symbol without",
            "additional checks.",
            "",
            "`protected_tail_review` means the suffix frequently appears after hard",
            "apostrophe/protected boundaries and should be handled together with the",
            "finite protected routing path, not blindly as a normal-text morph piece.",
            "",
            "## Next Use",
            "",
            "Use the private TSV to build a challenge-blind morph-piece policy. The",
            "next tokenizer candidate should be compared against",
            "`finite_protected_sp64_floor`, not bare SP64.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Analyze v2.0 morph seed candidates.")
    parser.add_argument(
        "--boundary-jsonl",
        default="artifacts/private/v2_0_soft_morph/soft_morph_boundaries.train.jsonl",
    )
    parser.add_argument(
        "--private-out",
        default="artifacts/private/v2_0_morph_seed_vocab/morph_seed_candidates.train.tsv",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_morph_seed_candidate_analysis.md",
    )
    parser.add_argument("--min-count", type=int, default=100)
    parser.add_argument("--min-surface-len", type=int, default=3)
    parser.add_argument("--max-collision-rate", type=float, default=0.05)
    parser.add_argument("--protected-tail-hard-share", type=float, default=0.25)
    parser.add_argument("--progress", type=int, default=1000)
    args = parser.parse_args(argv)

    if args.min_count <= 0:
        raise ValueError("--min-count must be positive")
    if args.min_surface_len <= 0:
        raise ValueError("--min-surface-len must be positive")
    if args.max_collision_rate < 0:
        raise ValueError("--max-collision-rate must be non-negative")
    if args.protected_tail_hard_share < 0 or args.protected_tail_hard_share > 1:
        raise ValueError("--protected-tail-hard-share must be between 0 and 1")

    boundary_jsonl = Path(args.boundary_jsonl)
    private_out = Path(args.private_out)
    rows, summary = analyze_boundary_jsonl(
        boundary_jsonl,
        min_count=args.min_count,
        min_surface_len=args.min_surface_len,
        max_collision_rate=args.max_collision_rate,
        protected_tail_hard_share=args.protected_tail_hard_share,
        progress=args.progress,
    )
    write_tsv(private_out, rows)
    report = format_report(
        boundary_jsonl=boundary_jsonl,
        private_out=private_out,
        rows=rows,
        summary=summary,
        min_count=args.min_count,
        min_surface_len=args.min_surface_len,
        max_collision_rate=args.max_collision_rate,
        protected_tail_hard_share=args.protected_tail_hard_share,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_private: {private_out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

