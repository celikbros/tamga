from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_THRESHOLDS = (1, 2, 5, 10, 25, 50, 100)


@dataclass(frozen=True)
class RouteEntry:
    category: str
    route: str
    surface: str
    count: int
    bytes: int


@dataclass(frozen=True)
class ThresholdRow:
    threshold: int
    unique_kept: int
    covered_count: int
    total_count: int

    @property
    def coverage(self) -> float:
        return self.covered_count / self.total_count if self.total_count else 0.0


def load_route_inventory(path: str | Path) -> list[RouteEntry]:
    entries: list[RouteEntry] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n")
        expected = "category\troute\tsurface\tcount\tbytes"
        if header != expected:
            raise ValueError(f"unexpected inventory header: {header!r}")
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            category, route, surface, count_raw, bytes_raw = line.split("\t")
            entries.append(
                RouteEntry(
                    category=category,
                    route=route,
                    surface=surface,
                    count=int(count_raw),
                    bytes=int(bytes_raw),
                )
            )
    return entries


def protected_entries(entries: list[RouteEntry]) -> list[RouteEntry]:
    return [entry for entry in entries if entry.category == "protected"]


def suffix_tail_entries(entries: list[RouteEntry]) -> list[RouteEntry]:
    return [entry for entry in entries if entry.category == "suffix_tail"]


def summarize_by_route(entries: list[RouteEntry]) -> dict[str, tuple[int, int, int]]:
    unique_counts: Counter[str] = Counter()
    occurrence_counts: Counter[str] = Counter()
    byte_counts: Counter[str] = Counter()
    for entry in entries:
        unique_counts[entry.route] += 1
        occurrence_counts[entry.route] += entry.count
        byte_counts[entry.route] += entry.count * entry.bytes
    return {
        route: (unique_counts[route], occurrence_counts[route], byte_counts[route])
        for route in sorted(unique_counts)
    }


def threshold_rows(
    entries: list[RouteEntry],
    thresholds: tuple[int, ...],
) -> list[ThresholdRow]:
    total = sum(entry.count for entry in entries)
    rows: list[ThresholdRow] = []
    for threshold in sorted(set(item for item in thresholds if item > 0)):
        kept = [entry for entry in entries if entry.count >= threshold]
        rows.append(
            ThresholdRow(
                threshold=threshold,
                unique_kept=len(kept),
                covered_count=sum(entry.count for entry in kept),
                total_count=total,
            )
        )
    return rows


def _fmt_float(value: float, digits: int = 6) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    *,
    inventory_path: Path,
    entries: list[RouteEntry],
    thresholds: tuple[int, ...],
) -> str:
    protected = protected_entries(entries)
    suffix_tails = suffix_tail_entries(entries)
    protected_total = sum(entry.count for entry in protected)
    suffix_total = sum(entry.count for entry in suffix_tails)
    protected_bytes = sum(entry.count * entry.bytes for entry in protected)

    lines = [
        "# v2.0 Protected Route Inventory Analysis",
        "",
        f"Inventory: `{inventory_path.as_posix()}`",
        "",
        "This public report summarizes the private protected-route inventory",
        "without listing raw protected surfaces. It is used to choose finite",
        "protected pieces and user-defined-symbol thresholds.",
        "",
        "## Inventory Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| protected unique surfaces | {len(protected)} |",
        f"| protected occurrences | {protected_total} |",
        f"| protected surface bytes weighted by count | {protected_bytes} |",
        f"| suffix-tail unique surfaces | {len(suffix_tails)} |",
        f"| suffix-tail occurrences | {suffix_total} |",
        "",
        "## Protected Routes",
        "",
        "| Route | Unique surfaces | Occurrences | Occurrence share | Weighted bytes |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for route, (unique, count, byte_count) in summarize_by_route(protected).items():
        share = count / protected_total if protected_total else 0.0
        lines.append(
            f"| {route} | {unique} | {count} | {_fmt_float(share)} | {byte_count} |"
        )

    lines.extend(
        [
            "",
            "## Protected UDS Threshold Coverage",
            "",
            "| Min count | Unique surfaces kept | Covered occurrences | Coverage |",
            "| ---: | ---: | ---: | ---: |",
        ]
    )
    for row in threshold_rows(protected, thresholds):
        lines.append(
            f"| {row.threshold} | {row.unique_kept} | {row.covered_count} | "
            f"{_fmt_float(row.coverage)} |"
        )

    lines.extend(
        [
            "",
            "## Suffix Tails After Protected Bases",
            "",
            "| Route | Unique surfaces | Occurrences | Occurrence share | Weighted bytes |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for route, (unique, count, byte_count) in summarize_by_route(suffix_tails).items():
        share = count / suffix_total if suffix_total else 0.0
        lines.append(
            f"| {route} | {unique} | {count} | {_fmt_float(share)} | {byte_count} |"
        )

    lines.extend(
        [
            "",
            "## Decision Hint",
            "",
            "Do not promote all protected surfaces. If high thresholds cover little,",
            "the protected encoder should favor subword pieces and byte fallback",
            "over memorizing full protected strings.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Analyze v2.0 protected route inventory without printing private surfaces.",
    )
    parser.add_argument(
        "--inventory",
        default="artifacts/private/v2_0_protected_aware/protected_route_inventory.train.tsv",
    )
    parser.add_argument("--out", default="artifacts/v2_0_protected_route_inventory_analysis.md")
    parser.add_argument(
        "--thresholds",
        default=",".join(str(item) for item in DEFAULT_THRESHOLDS),
        help="Comma-separated min-count thresholds for protected UDS coverage.",
    )
    args = parser.parse_args(argv)

    thresholds = tuple(
        int(item.strip())
        for item in args.thresholds.split(",")
        if item.strip()
    )
    inventory_path = Path(args.inventory)
    entries = load_route_inventory(inventory_path)
    report = format_report(
        inventory_path=inventory_path,
        entries=entries,
        thresholds=thresholds,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
