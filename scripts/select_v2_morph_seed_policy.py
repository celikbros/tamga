from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path


@dataclass(frozen=True)
class MorphSeedCandidate:
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
class PolicyEntry:
    token: str
    surface: str
    total_count: int
    recommendation: str
    action: str
    reason: str
    soft_share: float
    hard_share: float
    exact_collision_rate: float


@dataclass(frozen=True)
class PolicyStats:
    input_unique: int
    input_count: int
    selected_unique: int
    selected_count: int
    heldout_unique: int
    heldout_count: int

    @property
    def selected_share(self) -> float:
        return self.selected_count / self.input_count if self.input_count else 0.0


def load_candidates(path: str | Path) -> list[MorphSeedCandidate]:
    rows: list[MorphSeedCandidate] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        expected = [
            "token",
            "surface",
            "total_count",
            "soft_count",
            "hard_count",
            "non_suffix_exact_count",
            "word_start_exact_count",
            "other_exact_count",
            "surface_len",
            "soft_share",
            "hard_share",
            "exact_collision_rate",
            "recommendation",
        ]
        if header != expected:
            raise ValueError(f"unexpected header: {header!r}")
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != len(expected):
                continue
            rows.append(
                MorphSeedCandidate(
                    token=parts[0],
                    surface=parts[1],
                    total_count=int(parts[2]),
                    soft_count=int(parts[3]),
                    hard_count=int(parts[4]),
                    non_suffix_exact_count=int(parts[5]),
                    word_start_exact_count=int(parts[6]),
                    other_exact_count=int(parts[7]),
                    surface_len=int(parts[8]),
                    soft_share=float(parts[9]),
                    hard_share=float(parts[10]),
                    exact_collision_rate=float(parts[11]),
                    recommendation=parts[12],
                )
            )
    return rows


def choose_action(
    row: MorphSeedCandidate,
    *,
    min_count: int,
    safe_uds_min_len: int,
    safe_uds_max_collision: float,
    safe_uds_max_hard_share: float,
) -> tuple[str, str]:
    if row.total_count < min_count:
        return "holdout", "below_policy_min_count"

    if row.recommendation == "protected_tail_review":
        return "holdout", "protected_tail_route_review"

    if row.recommendation == "uds_or_seed_candidate":
        if (
            row.surface_len >= safe_uds_min_len
            and row.exact_collision_rate <= safe_uds_max_collision
            and row.hard_share <= safe_uds_max_hard_share
        ):
            return "safe_uds_candidate_later", "long_low_collision_low_hard_share"
        return "seed_bias", "safe_seed_not_forced"

    if row.recommendation == "seed_bias_candidate":
        return "seed_bias", "ambiguous_or_short_seed_only"

    return "holdout", f"recommendation_{row.recommendation}"


def select_policy(
    rows: list[MorphSeedCandidate],
    *,
    min_count: int,
    safe_uds_min_len: int,
    safe_uds_max_collision: float,
    safe_uds_max_hard_share: float,
) -> tuple[list[PolicyEntry], PolicyStats]:
    entries: list[PolicyEntry] = []
    input_count = sum(row.total_count for row in rows)
    for row in rows:
        action, reason = choose_action(
            row,
            min_count=min_count,
            safe_uds_min_len=safe_uds_min_len,
            safe_uds_max_collision=safe_uds_max_collision,
            safe_uds_max_hard_share=safe_uds_max_hard_share,
        )
        entries.append(
            PolicyEntry(
                token=row.token,
                surface=row.surface,
                total_count=row.total_count,
                recommendation=row.recommendation,
                action=action,
                reason=reason,
                soft_share=row.soft_share,
                hard_share=row.hard_share,
                exact_collision_rate=row.exact_collision_rate,
            )
        )
    selected = [entry for entry in entries if entry.action != "holdout"]
    heldout = [entry for entry in entries if entry.action == "holdout"]
    stats = PolicyStats(
        input_unique=len(rows),
        input_count=input_count,
        selected_unique=len(selected),
        selected_count=sum(entry.total_count for entry in selected),
        heldout_unique=len(heldout),
        heldout_count=sum(entry.total_count for entry in heldout),
    )
    entries.sort(key=lambda item: (item.action == "holdout", -item.total_count, item.action, item.token))
    return entries, stats


def write_policy(path: Path, entries: list[PolicyEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "token\tsurface\ttotal_count\trecommendation\taction\treason\t"
            "soft_share\thard_share\texact_collision_rate\n"
        )
        for entry in entries:
            handle.write(
                f"{entry.token}\t{entry.surface}\t{entry.total_count}\t"
                f"{entry.recommendation}\t{entry.action}\t{entry.reason}\t"
                f"{entry.soft_share:.6f}\t{entry.hard_share:.6f}\t"
                f"{entry.exact_collision_rate:.6f}\n"
            )


def summarize(entries: list[PolicyEntry], field: str) -> dict[str, tuple[int, int]]:
    unique_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    for entry in entries:
        key = getattr(entry, field)
        unique_counts[key] += 1
        token_counts[key] += entry.total_count
    return {
        key: (unique_counts[key], token_counts[key])
        for key in sorted(unique_counts)
    }


def _fmt_float(value: float, digits: int = 6) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    *,
    candidate_path: Path,
    policy_path: Path,
    entries: list[PolicyEntry],
    stats: PolicyStats,
    min_count: int,
    safe_uds_min_len: int,
    safe_uds_max_collision: float,
    safe_uds_max_hard_share: float,
) -> str:
    action_summary = summarize(entries, "action")
    reason_summary = summarize(entries, "reason")
    lines = [
        "# v2.0 Morph Seed Policy Selection",
        "",
        f"Source candidate TSV: `{candidate_path.as_posix()}`",
        f"Private policy TSV: `{policy_path.as_posix()}`",
        "",
        "This policy is challenge-blind. It selects morph pieces for a seed/bias",
        "branch without forcing every suffix as a user-defined symbol.",
        "",
        "## Parameters",
        "",
        "| Parameter | Value |",
        "| --- | ---: |",
        f"| min_count | {min_count} |",
        f"| safe_uds_min_len | {safe_uds_min_len} |",
        f"| safe_uds_max_collision | {_fmt_float(safe_uds_max_collision)} |",
        f"| safe_uds_max_hard_share | {_fmt_float(safe_uds_max_hard_share)} |",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| input unique | {stats.input_unique} |",
        f"| input occurrences | {stats.input_count} |",
        f"| selected unique | {stats.selected_unique} |",
        f"| selected occurrences | {stats.selected_count} |",
        f"| selected occurrence share | {_fmt_float(stats.selected_share)} |",
        f"| heldout unique | {stats.heldout_unique} |",
        f"| heldout occurrences | {stats.heldout_count} |",
        "",
        "## Action Summary",
        "",
        "| Action | Unique | Occurrences | Share of input occurrences |",
        "| --- | ---: | ---: | ---: |",
    ]
    for action, (unique, count) in action_summary.items():
        share = count / stats.input_count if stats.input_count else 0.0
        lines.append(f"| {action} | {unique} | {count} | {_fmt_float(share)} |")

    lines.extend(
        [
            "",
            "## Reason Summary",
            "",
            "| Reason | Unique | Occurrences | Share of input occurrences |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for reason, (unique, count) in reason_summary.items():
        share = count / stats.input_count if stats.input_count else 0.0
        lines.append(f"| {reason} | {unique} | {count} | {_fmt_float(share)} |")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "The first prototype should treat `seed_bias` pieces as a learned-vocab",
            "prior, not as hard user-defined symbols.",
            "",
            "`safe_uds_candidate_later` pieces are not automatically promoted in",
            "the first run. They are only a small, auditable pool for a later UDS",
            "experiment if the softer seed/bias branch fails.",
            "",
            "`holdout` pieces stay out of the normal-text morph seed path. In",
            "particular, protected-tail pieces belong with finite protected routing.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Select v2.0 morph seed policy.")
    parser.add_argument(
        "--candidates",
        default="artifacts/private/v2_0_morph_seed_vocab/morph_seed_candidates.train.tsv",
    )
    parser.add_argument(
        "--policy-out",
        default="artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_morph_seed_policy_selection.md",
    )
    parser.add_argument("--min-count", type=int, default=100)
    parser.add_argument("--safe-uds-min-len", type=int, default=4)
    parser.add_argument("--safe-uds-max-collision", type=float, default=0.001)
    parser.add_argument("--safe-uds-max-hard-share", type=float, default=0.01)
    args = parser.parse_args(argv)

    rows = load_candidates(args.candidates)
    entries, stats = select_policy(
        rows,
        min_count=args.min_count,
        safe_uds_min_len=args.safe_uds_min_len,
        safe_uds_max_collision=args.safe_uds_max_collision,
        safe_uds_max_hard_share=args.safe_uds_max_hard_share,
    )
    policy_path = Path(args.policy_out)
    write_policy(policy_path, entries)
    report = format_report(
        candidate_path=Path(args.candidates),
        policy_path=policy_path,
        entries=entries,
        stats=stats,
        min_count=args.min_count,
        safe_uds_min_len=args.safe_uds_min_len,
        safe_uds_max_collision=args.safe_uds_max_collision,
        safe_uds_max_hard_share=args.safe_uds_max_hard_share,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_policy: {policy_path}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

