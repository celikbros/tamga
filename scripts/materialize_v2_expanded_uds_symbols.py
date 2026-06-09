from __future__ import annotations

from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path


@dataclass(frozen=True)
class CandidateRow:
    token: str
    surface: str
    total_count: int
    surface_len: int
    soft_share: float
    hard_share: float
    exact_collision_rate: float
    recommendation: str


@dataclass(frozen=True)
class ExpandedUDSSelection:
    rows: list[CandidateRow]
    input_rows: int

    @property
    def total_count(self) -> int:
        return sum(row.total_count for row in self.rows)

    @property
    def max_hard_share(self) -> float:
        return max((row.hard_share for row in self.rows), default=0.0)

    @property
    def max_collision_rate(self) -> float:
        return max((row.exact_collision_rate for row in self.rows), default=0.0)


def load_candidates(path: str | Path) -> list[CandidateRow]:
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
    rows: list[CandidateRow] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        if header != expected:
            raise ValueError(f"unexpected candidate header: {header!r}")
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != len(expected):
                raise ValueError(f"unexpected candidate row: {line!r}")
            rows.append(
                CandidateRow(
                    token=parts[0],
                    surface=parts[1],
                    total_count=int(parts[2]),
                    surface_len=int(parts[8]),
                    soft_share=float(parts[9]),
                    hard_share=float(parts[10]),
                    exact_collision_rate=float(parts[11]),
                    recommendation=parts[12],
                )
            )
    return rows


def select_rows(
    rows: list[CandidateRow],
    *,
    min_count: int,
    min_surface_len: int,
    max_hard_share: float,
    max_collision_rate: float,
    recommendation: str,
    max_symbols: int,
) -> ExpandedUDSSelection:
    selected = [
        row
        for row in rows
        if row.recommendation == recommendation
        and row.total_count >= min_count
        and row.surface_len >= min_surface_len
        and row.hard_share <= max_hard_share
        and row.exact_collision_rate <= max_collision_rate
    ]
    selected.sort(
        key=lambda row: (
            -row.total_count,
            row.hard_share,
            row.exact_collision_rate,
            row.surface,
        )
    )
    if max_symbols > 0:
        selected = selected[:max_symbols]
    return ExpandedUDSSelection(rows=selected, input_rows=len(rows))


def write_symbols(selection: ExpandedUDSSelection, out: str | Path) -> None:
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
    candidates_path: Path,
    symbols_out: Path,
    selection: ExpandedUDSSelection,
    min_count: int,
    min_surface_len: int,
    max_hard_share: float,
    max_collision_rate: float,
    recommendation: str,
    max_symbols: int,
) -> str:
    lines = [
        "# v2.0 Expanded UDS Symbol Selection",
        "",
        f"Candidate TSV: `{candidates_path.as_posix()}`",
        f"Symbols output: `{symbols_out.as_posix()}`",
        "",
        "This is a controlled expansion of the 7-symbol safe UDS pool. It uses",
        "only train-side morphology candidate statistics and does not inspect",
        "visible challenge rows.",
        "",
        "## Parameters",
        "",
        "| Parameter | Value |",
        "| --- | ---: |",
        f"| recommendation | `{recommendation}` |",
        f"| min_count | {min_count} |",
        f"| min_surface_len | {min_surface_len} |",
        f"| max_hard_share | {_fmt_float(max_hard_share)} |",
        f"| max_collision_rate | {_fmt_float(max_collision_rate)} |",
        f"| max_symbols | {max_symbols} |",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| input candidates | {selection.input_rows} |",
        f"| selected symbols | {len(selection.rows)} |",
        f"| selected occurrences | {selection.total_count} |",
        f"| max selected hard share | {_fmt_float(selection.max_hard_share)} |",
        f"| max selected exact collision rate | {_fmt_float(selection.max_collision_rate)} |",
        "",
        "## Symbols",
        "",
        "| Token | Surface | Count | Surface len | Hard share | Exact collision rate |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in selection.rows:
        lines.append(
            f"| `{row.token}` | `{row.surface}` | {row.total_count} | "
            f"{row.surface_len} | {_fmt_float(row.hard_share)} | "
            f"{_fmt_float(row.exact_collision_rate)} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "This branch should continue only if it improves over the 7-symbol",
            "safe UDS result without materially increasing token pressure.",
            "If it merely shifts token pressure or visible F1 by noise, stop",
            "UDS expansion and move to constrained/MorphBPE design.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Materialize v2.0 expanded UDS symbol list.")
    parser.add_argument(
        "--candidates",
        default="artifacts/private/v2_0_morph_seed_vocab/morph_seed_candidates.train.tsv",
    )
    parser.add_argument(
        "--symbols-out",
        default="artifacts/private/v2_0_morph_seed_vocab/expanded_uds22_symbols.train.txt",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_expanded_uds22_symbols.md",
    )
    parser.add_argument("--min-count", type=int, default=100)
    parser.add_argument("--min-surface-len", type=int, default=3)
    parser.add_argument("--max-hard-share", type=float, default=0.01)
    parser.add_argument("--max-collision-rate", type=float, default=0.001)
    parser.add_argument("--recommendation", default="uds_or_seed_candidate")
    parser.add_argument("--max-symbols", type=int, default=64)
    args = parser.parse_args(argv)

    candidates_path = Path(args.candidates)
    symbols_out = Path(args.symbols_out)
    selection = select_rows(
        load_candidates(candidates_path),
        min_count=args.min_count,
        min_surface_len=args.min_surface_len,
        max_hard_share=args.max_hard_share,
        max_collision_rate=args.max_collision_rate,
        recommendation=args.recommendation,
        max_symbols=args.max_symbols,
    )
    write_symbols(selection, symbols_out)
    report = format_report(
        candidates_path=candidates_path,
        symbols_out=symbols_out,
        selection=selection,
        min_count=args.min_count,
        min_surface_len=args.min_surface_len,
        max_hard_share=args.max_hard_share,
        max_collision_rate=args.max_collision_rate,
        recommendation=args.recommendation,
        max_symbols=args.max_symbols,
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
