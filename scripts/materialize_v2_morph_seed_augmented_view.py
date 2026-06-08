from __future__ import annotations

from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path


@dataclass(frozen=True)
class PolicyEntry:
    token: str
    surface: str
    total_count: int
    recommendation: str
    action: str
    reason: str


@dataclass(frozen=True)
class AugmentationStats:
    base_lines: int
    base_bytes: int
    selected_entries: int
    augmentation_lines: int
    augmentation_bytes: int
    output_lines: int
    output_bytes: int
    max_repeat_per_entry: int
    total_weighted_repeats: int

    @property
    def output_bytes_per_base_byte(self) -> float:
        return self.output_bytes / self.base_bytes if self.base_bytes else 0.0

    @property
    def augmentation_bytes_per_base_byte(self) -> float:
        return self.augmentation_bytes / self.base_bytes if self.base_bytes else 0.0


def load_policy(path: str | Path) -> list[PolicyEntry]:
    entries: list[PolicyEntry] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        expected = [
            "token",
            "surface",
            "total_count",
            "recommendation",
            "action",
            "reason",
            "soft_share",
            "hard_share",
            "exact_collision_rate",
        ]
        if header != expected:
            raise ValueError(f"unexpected policy header: {header!r}")
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != len(expected):
                continue
            entries.append(
                PolicyEntry(
                    token=parts[0],
                    surface=parts[1],
                    total_count=int(parts[2]),
                    recommendation=parts[3],
                    action=parts[4],
                    reason=parts[5],
                )
            )
    return entries


def selected_policy_entries(
    entries: list[PolicyEntry],
    *,
    include_safe_uds_later: bool,
) -> list[PolicyEntry]:
    allowed = {"seed_bias"}
    if include_safe_uds_later:
        allowed.add("safe_uds_candidate_later")
    return [entry for entry in entries if entry.action in allowed]


def repeats_for_count(count: int, *, divisor: int, max_repeat: int) -> int:
    if count <= 0:
        return 0
    if divisor <= 0:
        raise ValueError("divisor must be positive")
    return min(max_repeat, max(1, math.ceil(count / divisor)))


def augmentation_line(entry: PolicyEntry, repeat: int) -> str:
    # Leading spaces make SentencePiece see these as word-initial pieces without
    # adding synthetic marker characters to normal encode-time text.
    unit = f"{entry.surface} "
    return (unit * repeat).rstrip()


def materialize_augmented_view(
    *,
    base_train: Path,
    policy_path: Path,
    out: Path,
    repeat_divisor: int,
    max_repeat_per_entry: int,
    include_safe_uds_later: bool,
) -> AugmentationStats:
    entries = selected_policy_entries(
        load_policy(policy_path),
        include_safe_uds_later=include_safe_uds_later,
    )
    out.parent.mkdir(parents=True, exist_ok=True)

    base_lines = 0
    base_bytes = 0
    augmentation_lines = 0
    augmentation_bytes = 0
    total_repeats = 0

    with base_train.open("r", encoding="utf-8") as source, out.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as target:
        for raw_line in source:
            target.write(raw_line)
            base_lines += 1
            base_bytes += len(raw_line.rstrip("\n").encode("utf-8"))

        for entry in entries:
            repeats = repeats_for_count(
                entry.total_count,
                divisor=repeat_divisor,
                max_repeat=max_repeat_per_entry,
            )
            if repeats <= 0:
                continue
            line = augmentation_line(entry, repeats)
            target.write(line + "\n")
            augmentation_lines += 1
            augmentation_bytes += len(line.encode("utf-8"))
            total_repeats += repeats

    output_lines = base_lines + augmentation_lines
    output_bytes = base_bytes + augmentation_bytes
    return AugmentationStats(
        base_lines=base_lines,
        base_bytes=base_bytes,
        selected_entries=len(entries),
        augmentation_lines=augmentation_lines,
        augmentation_bytes=augmentation_bytes,
        output_lines=output_lines,
        output_bytes=output_bytes,
        max_repeat_per_entry=max_repeat_per_entry,
        total_weighted_repeats=total_repeats,
    )


def _fmt_float(value: float, digits: int = 6) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    *,
    base_train: Path,
    policy_path: Path,
    out: Path,
    stats: AugmentationStats,
    repeat_divisor: int,
    include_safe_uds_later: bool,
) -> str:
    return "\n".join(
        [
            "# v2.0 Morph Seed Augmented Train View",
            "",
            f"Base train: `{base_train.as_posix()}`",
            f"Policy TSV: `{policy_path.as_posix()}`",
            f"Augmented train view: `{out.as_posix()}`",
            "",
            "This is a train-only SentencePiece view. It appends selected morph",
            "seed surfaces as a small frequency-bias appendix. Normal encode-time",
            "text does not contain these synthetic appendix lines.",
            "",
            "## Parameters",
            "",
            "| Parameter | Value |",
            "| --- | ---: |",
            f"| repeat_divisor | {repeat_divisor} |",
            f"| max_repeat_per_entry | {stats.max_repeat_per_entry} |",
            f"| include_safe_uds_later | {include_safe_uds_later} |",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| base lines | {stats.base_lines} |",
            f"| base bytes | {stats.base_bytes} |",
            f"| selected policy entries | {stats.selected_entries} |",
            f"| augmentation lines | {stats.augmentation_lines} |",
            f"| augmentation bytes | {stats.augmentation_bytes} |",
            f"| augmentation bytes/base byte | {_fmt_float(stats.augmentation_bytes_per_base_byte)} |",
            f"| output lines | {stats.output_lines} |",
            f"| output bytes | {stats.output_bytes} |",
            f"| output bytes/base byte | {_fmt_float(stats.output_bytes_per_base_byte)} |",
            f"| total weighted repeats | {stats.total_weighted_repeats} |",
            "",
            "## Gate",
            "",
            "The augmentation should stay small. If output bytes/base byte grows",
            "substantially above 1.02, reduce repeats before training a tokenizer.",
        ]
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Materialize v2.0 morph seed augmented SP train view.")
    parser.add_argument(
        "--base-train",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt",
    )
    parser.add_argument(
        "--policy",
        default="artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv",
    )
    parser.add_argument(
        "--out",
        default="artifacts/private/v2_0_morph_seed_vocab/morph_seed_bias_augmented_train.txt",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_morph_seed_augmented_view.md",
    )
    parser.add_argument("--repeat-divisor", type=int, default=10000)
    parser.add_argument("--max-repeat-per-entry", type=int, default=8)
    parser.add_argument("--include-safe-uds-later", action="store_true")
    args = parser.parse_args(argv)

    if args.repeat_divisor <= 0:
        raise ValueError("--repeat-divisor must be positive")
    if args.max_repeat_per_entry <= 0:
        raise ValueError("--max-repeat-per-entry must be positive")

    base_train = Path(args.base_train)
    policy_path = Path(args.policy)
    out = Path(args.out)
    stats = materialize_augmented_view(
        base_train=base_train,
        policy_path=policy_path,
        out=out,
        repeat_divisor=args.repeat_divisor,
        max_repeat_per_entry=args.max_repeat_per_entry,
        include_safe_uds_later=args.include_safe_uds_later,
    )
    report = format_report(
        base_train=base_train,
        policy_path=policy_path,
        out=out,
        stats=stats,
        repeat_divisor=args.repeat_divisor,
        include_safe_uds_later=args.include_safe_uds_later,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_view: {out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

