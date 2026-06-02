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

from scripts.analyze_v2_seed_vocab import SeedEntry, load_seed_vocab  # noqa: E402
from scripts.materialize_v2_soft_morph_artifacts import protected_kind, source_surface  # noqa: E402
from tr_tokenizer.tokenizer import WORD_START  # noqa: E402


@dataclass(frozen=True)
class SelectedEntry:
    token: str
    count: int
    category: str
    reason: str


@dataclass(frozen=True)
class SelectionStats:
    total_unique: int
    total_count: int
    selected_unique: int
    selected_count: int
    budget: int
    word_start_budget: int
    word_start_min_count: int

    @property
    def coverage(self) -> float:
        return self.selected_count / self.total_count if self.total_count else 0.0

    @property
    def unused_budget(self) -> int:
        return max(0, self.budget - self.selected_unique)


def seed_category(token: str) -> str:
    if token.startswith("+") and len(token) > 1:
        return "suffix"

    surface = source_surface(token)
    kind = protected_kind(surface)
    if kind is not None:
        return f"protected:{kind}"

    if token.startswith(WORD_START):
        return "word_start"

    if len(token) == 1 and not token.isalnum():
        return "punct_or_symbol"

    return "other"


def category_group(category: str) -> str:
    if category.startswith("protected:"):
        return "protected"
    return category


def select_seed_entries(
    entries: list[SeedEntry],
    *,
    budget: int,
    min_word_start_count: int,
    min_protected_count: int,
    include_protected: bool = True,
) -> tuple[list[SelectedEntry], SelectionStats]:
    if budget <= 0:
        raise ValueError("budget must be positive")
    if min_word_start_count <= 0:
        raise ValueError("min_word_start_count must be positive")
    if min_protected_count <= 0:
        raise ValueError("min_protected_count must be positive")

    selected_by_token: dict[str, SelectedEntry] = {}
    word_start_candidates: list[tuple[SeedEntry, str]] = []
    total_count = sum(entry.count for entry in entries)

    def add(entry: SeedEntry, category: str, reason: str) -> None:
        if entry.token in selected_by_token:
            return
        if len(selected_by_token) >= budget:
            return
        selected_by_token[entry.token] = SelectedEntry(
            token=entry.token,
            count=entry.count,
            category=category,
            reason=reason,
        )

    for entry in entries:
        category = seed_category(entry.token)
        group = category_group(category)
        if group == "word_start":
            word_start_candidates.append((entry, category))
        elif group == "suffix":
            add(entry, category, "all_suffix")
        elif group == "punct_or_symbol":
            add(entry, category, "all_punct_or_symbol")
        elif (
            group == "protected"
            and include_protected
            and entry.count >= min_protected_count
        ):
            add(entry, category, f"protected_count_ge_{min_protected_count}")
        elif group == "other":
            add(entry, category, "all_other")

    protected_prefix_unique = len(selected_by_token)
    for entry, category in word_start_candidates:
        if entry.count < min_word_start_count:
            continue
        add(entry, category, "top_word_start")

    selected = sorted(
        selected_by_token.values(),
        key=lambda item: (-item.count, item.category, item.token),
    )
    selected_count = sum(entry.count for entry in selected)
    stats = SelectionStats(
        total_unique=len(entries),
        total_count=total_count,
        selected_unique=len(selected),
        selected_count=selected_count,
        budget=budget,
        word_start_budget=max(0, budget - protected_prefix_unique),
        word_start_min_count=min_word_start_count,
    )
    return selected, stats


def summarize(entries: list[SelectedEntry]) -> dict[str, tuple[int, int]]:
    unique_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    for entry in entries:
        group = category_group(entry.category)
        unique_counts[group] += 1
        token_counts[group] += entry.count
    return {
        group: (unique_counts[group], token_counts[group])
        for group in sorted(unique_counts)
    }


def summarize_reasons(entries: list[SelectedEntry]) -> dict[str, tuple[int, int]]:
    unique_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    for entry in entries:
        unique_counts[entry.reason] += 1
        token_counts[entry.reason] += entry.count
    return {
        reason: (unique_counts[reason], token_counts[reason])
        for reason in sorted(unique_counts)
    }


def write_selected_tsv(path: str | Path, entries: list[SelectedEntry]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("token\tcount\tcategory\treason\n")
        for entry in entries:
            handle.write(f"{entry.token}\t{entry.count}\t{entry.category}\t{entry.reason}\n")


def _fmt_float(value: float, digits: int = 6) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    *,
    seed_path: Path,
    selected_path: Path,
    selected: list[SelectedEntry],
    stats: SelectionStats,
    min_protected_count: int,
    include_protected: bool,
) -> str:
    group_summary = summarize(selected)
    reason_summary = summarize_reasons(selected)
    lines = [
        "# v2.0 Seed Policy Selection",
        "",
        f"Source seed vocab: `{seed_path.as_posix()}`",
        f"Private selected TSV: `{selected_path.as_posix()}`",
        "",
        "This report records the first seed policy for the",
        "`protected_hard_soft_morph_seeded_sp64` prototype without listing raw",
        "private corpus tokens.",
        "",
        "## Policy",
        "",
        "```text",
        "include all suffix tokens",
        "include all punctuation/symbol tokens",
        (
            f"include protected tokens with count >= {min_protected_count}"
            if include_protected
            else "do not force protected surface tokens into the seed set"
        ),
        "include other non-word-start tokens",
        "fill remaining budget with high-frequency word_start tokens",
        "do not seed the word_start long-tail by default",
        "```",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| budget | {stats.budget} |",
        f"| selected unique | {stats.selected_unique} |",
        f"| unused budget | {stats.unused_budget} |",
        f"| total seed unique | {stats.total_unique} |",
        f"| selected token count | {stats.selected_count} |",
        f"| total seed token count | {stats.total_count} |",
        f"| selected coverage | {_fmt_float(stats.coverage)} |",
        f"| word_start available slots after mandatory groups | {stats.word_start_budget} |",
        f"| word_start min count | {stats.word_start_min_count} |",
        f"| protected min count | {min_protected_count if include_protected else 'disabled'} |",
        "",
        "## Selected Coverage By Group",
        "",
        "| Group | Unique selected | Covered token count | Share of all seed tokens |",
        "| --- | ---: | ---: | ---: |",
    ]
    for group, (unique, count) in group_summary.items():
        share = count / stats.total_count if stats.total_count else 0.0
        lines.append(f"| {group} | {unique} | {count} | {_fmt_float(share)} |")

    lines.extend(
        [
            "",
            "## Selected Coverage By Reason",
            "",
            "| Reason | Unique selected | Covered token count | Share of all seed tokens |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for reason, (unique, count) in reason_summary.items():
        share = count / stats.total_count if stats.total_count else 0.0
        lines.append(f"| {reason} | {unique} | {count} | {_fmt_float(share)} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This is a seed-selection policy, not a trained tokenizer. The next",
            "prototype must show whether the unseeded word_start long-tail can be",
            "handled by learned merges without falling back to bytes.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Select v2.0 seed vocab policy entries.")
    parser.add_argument(
        "--seed",
        default="artifacts/private/v2_0_soft_morph/soft_morph_seed_vocab.train.tsv",
    )
    parser.add_argument(
        "--selected-out",
        default="artifacts/private/v2_0_soft_morph/protected_hard_soft_morph_seeded_sp64.selected_seed.tsv",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_seed_policy_selection.md",
    )
    parser.add_argument("--budget", type=int, default=64000)
    parser.add_argument("--min-word-start-count", type=int, default=2)
    parser.add_argument("--min-protected-count", type=int, default=10)
    parser.add_argument(
        "--exclude-protected",
        action="store_true",
        help="Do not force observed protected tokens into the seed set.",
    )
    args = parser.parse_args(argv)

    entries = load_seed_vocab(args.seed)
    selected, stats = select_seed_entries(
        entries,
        budget=args.budget,
        min_word_start_count=args.min_word_start_count,
        min_protected_count=args.min_protected_count,
        include_protected=not args.exclude_protected,
    )
    selected_out = Path(args.selected_out)
    write_selected_tsv(selected_out, selected)
    report = format_report(
        seed_path=Path(args.seed),
        selected_path=selected_out,
        selected=selected,
        stats=stats,
        min_protected_count=args.min_protected_count,
        include_protected=not args.exclude_protected,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_selected: {selected_out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
