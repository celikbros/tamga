from __future__ import annotations

from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path


@dataclass(frozen=True)
class PolicyRow:
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
class UDSSelection:
    rows: list[PolicyRow]

    @property
    def total_count(self) -> int:
        return sum(row.total_count for row in self.rows)

    @property
    def max_hard_share(self) -> float:
        return max((row.hard_share for row in self.rows), default=0.0)

    @property
    def max_collision_rate(self) -> float:
        return max((row.exact_collision_rate for row in self.rows), default=0.0)


def load_policy(path: str | Path) -> list[PolicyRow]:
    rows: list[PolicyRow] = []
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
    with Path(path).open("r", encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        if header != expected:
            raise ValueError(f"unexpected policy header: {header!r}")
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != len(expected):
                raise ValueError(f"unexpected policy row: {line!r}")
            rows.append(
                PolicyRow(
                    token=parts[0],
                    surface=parts[1],
                    total_count=int(parts[2]),
                    recommendation=parts[3],
                    action=parts[4],
                    reason=parts[5],
                    soft_share=float(parts[6]),
                    hard_share=float(parts[7]),
                    exact_collision_rate=float(parts[8]),
                )
            )
    return rows


def select_rows(rows: list[PolicyRow], *, action: str) -> UDSSelection:
    selected = [row for row in rows if row.action == action]
    return UDSSelection(rows=selected)


def write_symbols(selection: UDSSelection, out: str | Path) -> None:
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "".join(f"{row.surface}\n" for row in selection.rows),
        encoding="utf-8",
    )


def _fmt_float(value: float, digits: int = 6) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    *,
    policy_path: Path,
    symbols_out: Path,
    action: str,
    selection: UDSSelection,
) -> str:
    lines = [
        "# v2.0 Safe UDS Symbol Selection",
        "",
        f"Policy TSV: `{policy_path.as_posix()}`",
        f"Symbols output: `{symbols_out.as_posix()}`",
        f"Action: `{action}`",
        "",
        "This is a small auditable user-defined-symbol pool. It is derived",
        "only from train-policy statistics and does not use visible challenge",
        "rows.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| selected symbols | {len(selection.rows)} |",
        f"| selected occurrences | {selection.total_count} |",
        f"| max hard share | {_fmt_float(selection.max_hard_share)} |",
        f"| max exact collision rate | {_fmt_float(selection.max_collision_rate)} |",
        "",
        "## Symbols",
        "",
        "| Token | Surface | Count | Hard share | Exact collision rate | Reason |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in selection.rows:
        lines.append(
            f"| `{row.token}` | `{row.surface}` | {row.total_count} | "
            f"{_fmt_float(row.hard_share)} | {_fmt_float(row.exact_collision_rate)} | "
            f"{row.reason} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "This UDS probe should only continue if token pressure stays near the",
            "finite-protected SP64 floor and visible boundary behavior improves.",
            "If it does not improve morphology F1, stop this cheap UDS branch.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Materialize v2.0 safe UDS symbol list.")
    parser.add_argument(
        "--policy",
        default="artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv",
    )
    parser.add_argument("--action", default="safe_uds_candidate_later")
    parser.add_argument(
        "--symbols-out",
        default="artifacts/private/v2_0_morph_seed_vocab/safe_uds_symbols.train.txt",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_safe_uds_symbols.md",
    )
    args = parser.parse_args(argv)

    policy_path = Path(args.policy)
    symbols_out = Path(args.symbols_out)
    selection = select_rows(load_policy(policy_path), action=args.action)
    write_symbols(selection, symbols_out)
    report = format_report(
        policy_path=policy_path,
        symbols_out=symbols_out,
        action=args.action,
        selection=selection,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_symbols: {symbols_out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
