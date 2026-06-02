from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.analyze_v2_protected_route_inventory import (  # noqa: E402
    RouteEntry,
    load_route_inventory,
)


COMMON_LITERALS = (
    "http",
    "https",
    "www",
    "://",
    ">=",
    "<=",
    "==",
    "!=",
    "~=",
    "->",
    "::",
)
EXTENSION_RE = re.compile(r"\.[A-Za-z0-9]{1,12}(?=$|[/?#:&=])")


@dataclass(frozen=True)
class PieceCandidate:
    piece: str
    count: int
    category: str
    reason: str
    routes: tuple[str, ...]

    @property
    def bytes(self) -> int:
        return len(self.piece.encode("utf-8"))


@dataclass(frozen=True)
class SelectionStats:
    candidates_unique: int
    candidates_count: int
    selected_unique: int
    selected_count: int
    budget: int
    byte_fallback_reserved: int = 256

    @property
    def coverage(self) -> float:
        return self.selected_count / self.candidates_count if self.candidates_count else 0.0

    @property
    def unused_budget(self) -> int:
        return max(0, self.budget - self.selected_unique)


def char_category(char: str) -> str:
    if char.isdigit():
        return "char_digit"
    if char.isalpha():
        if char.isascii():
            return "char_ascii_alpha"
        return "char_non_ascii_alpha"
    if char.isspace():
        return "char_space"
    return "char_punct_or_symbol"


def delimiter_runs(surface: str) -> list[str]:
    runs: list[str] = []
    current = ""
    for char in surface:
        if char.isalnum():
            if current:
                runs.append(current)
                current = ""
        else:
            current += char
    if current:
        runs.append(current)
    return runs


def candidate_events(entry: RouteEntry) -> list[tuple[str, str, str]]:
    if entry.category != "protected":
        return []

    surface = entry.surface
    events: list[tuple[str, str, str]] = []

    for char in surface:
        if not char.isspace():
            events.append((char, char_category(char), "protected_char"))

    for run in delimiter_runs(surface):
        if len(run) > 1:
            events.append((run, "delimiter_run", "protected_delimiter"))

    for match in EXTENSION_RE.finditer(surface):
        events.append((match.group(0), "extension", "protected_extension"))

    lowered = surface.lower()
    for literal in COMMON_LITERALS:
        if literal in lowered:
            events.append((literal, "common_literal", "protected_literal"))

    return events


def build_candidates(entries: list[RouteEntry]) -> list[PieceCandidate]:
    counts: Counter[tuple[str, str, str]] = Counter()
    routes_by_key: defaultdict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)

    for entry in entries:
        for piece, category, reason in candidate_events(entry):
            key = (piece, category, reason)
            counts[key] += entry.count
            routes_by_key[key][entry.route] += entry.count

    candidates: list[PieceCandidate] = []
    for (piece, category, reason), count in counts.items():
        routes = tuple(route for route, _ in routes_by_key[(piece, category, reason)].most_common())
        candidates.append(
            PieceCandidate(
                piece=piece,
                count=count,
                category=category,
                reason=reason,
                routes=routes,
            )
        )

    return sorted(candidates, key=lambda item: (-item.count, item.category, item.piece))


def threshold_for_category(
    category: str,
    *,
    min_char_count: int,
    min_delimiter_count: int,
    min_extension_count: int,
    min_literal_count: int,
) -> int:
    if category.startswith("char_"):
        return min_char_count
    if category == "delimiter_run":
        return min_delimiter_count
    if category == "extension":
        return min_extension_count
    if category == "common_literal":
        return min_literal_count
    return min_char_count


def select_candidates(
    candidates: list[PieceCandidate],
    *,
    budget: int,
    min_char_count: int,
    min_delimiter_count: int,
    min_extension_count: int,
    min_literal_count: int,
) -> tuple[list[PieceCandidate], SelectionStats]:
    if budget <= 0:
        raise ValueError("budget must be positive")

    filtered = [
        candidate
        for candidate in candidates
        if candidate.count
        >= threshold_for_category(
            candidate.category,
            min_char_count=min_char_count,
            min_delimiter_count=min_delimiter_count,
            min_extension_count=min_extension_count,
            min_literal_count=min_literal_count,
        )
    ]
    selected = filtered[:budget]
    stats = SelectionStats(
        candidates_unique=len(candidates),
        candidates_count=sum(candidate.count for candidate in candidates),
        selected_unique=len(selected),
        selected_count=sum(candidate.count for candidate in selected),
        budget=budget,
    )
    return selected, stats


def summarize_by_category(candidates: list[PieceCandidate]) -> dict[str, tuple[int, int]]:
    unique_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    for candidate in candidates:
        unique_counts[candidate.category] += 1
        token_counts[candidate.category] += candidate.count
    return {
        category: (unique_counts[category], token_counts[category])
        for category in sorted(unique_counts)
    }


def write_selected_tsv(path: str | Path, selected: list[PieceCandidate]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("piece\tcount\tcategory\treason\tbytes\troutes\n")
        for candidate in selected:
            routes = ",".join(candidate.routes)
            handle.write(
                f"{candidate.piece}\t{candidate.count}\t{candidate.category}\t"
                f"{candidate.reason}\t{candidate.bytes}\t{routes}\n"
            )


def _fmt_float(value: float, digits: int = 6) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    *,
    inventory_path: Path,
    selected_path: Path,
    selected: list[PieceCandidate],
    stats: SelectionStats,
    min_char_count: int,
    min_delimiter_count: int,
    min_extension_count: int,
    min_literal_count: int,
) -> str:
    summary = summarize_by_category(selected)
    lines = [
        "# v2.0 Protected Piece Vocabulary Selection",
        "",
        f"Source inventory: `{inventory_path.as_posix()}`",
        f"Private selected TSV: `{selected_path.as_posix()}`",
        "",
        "This report records a conservative finite protected-piece selection.",
        "It does not list private protected surfaces or selected raw pieces.",
        "",
        "## Policy",
        "",
        "```text",
        "select character pieces from protected surfaces above threshold",
        "select delimiter/operator runs above threshold",
        "select file/URL-like extensions above threshold",
        "select only stable common literals such as http/https/www/operators",
        "do not promote rare full protected surfaces",
        "keep 256 UTF-8 byte fallback pieces mandatory",
        "```",
        "",
        "## Thresholds",
        "",
        "| Threshold | Value |",
        "| --- | ---: |",
        f"| min char count | {min_char_count} |",
        f"| min delimiter count | {min_delimiter_count} |",
        f"| min extension count | {min_extension_count} |",
        f"| min literal count | {min_literal_count} |",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| protected-piece budget | {stats.budget} |",
        f"| selected unique pieces | {stats.selected_unique} |",
        f"| unused budget | {stats.unused_budget} |",
        f"| candidate unique pieces | {stats.candidates_unique} |",
        f"| selected weighted candidate count | {stats.selected_count} |",
        f"| total weighted candidate count | {stats.candidates_count} |",
        f"| selected weighted coverage | {_fmt_float(stats.coverage)} |",
        f"| mandatory byte fallback pieces | {stats.byte_fallback_reserved} |",
        "",
        "## Selected Pieces By Category",
        "",
        "| Category | Unique selected | Weighted count | Share of selected count |",
        "| --- | ---: | ---: | ---: |",
    ]
    for category, (unique, count) in summary.items():
        share = count / stats.selected_count if stats.selected_count else 0.0
        lines.append(f"| {category} | {unique} | {count} | {_fmt_float(share)} |")

    lines.extend(
        [
            "",
            "## Decision Hint",
            "",
            "This is a finite protected-piece vocabulary proposal, not a final",
            "tokenizer. The next gate is a stateless protected encoder that uses",
            "these pieces greedily, then falls back to UTF-8 bytes for all",
            "remaining protected text.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Select conservative finite protected pieces from route inventory.",
    )
    parser.add_argument(
        "--inventory",
        default="artifacts/private/v2_0_protected_aware/protected_route_inventory.train.tsv",
    )
    parser.add_argument(
        "--selected-out",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--report-out", default="artifacts/v2_0_protected_piece_vocab_selection.md")
    parser.add_argument("--budget", type=int, default=4096)
    parser.add_argument("--min-char-count", type=int, default=25)
    parser.add_argument("--min-delimiter-count", type=int, default=5)
    parser.add_argument("--min-extension-count", type=int, default=5)
    parser.add_argument("--min-literal-count", type=int, default=5)
    args = parser.parse_args(argv)

    entries = load_route_inventory(args.inventory)
    candidates = build_candidates(entries)
    selected, stats = select_candidates(
        candidates,
        budget=args.budget,
        min_char_count=args.min_char_count,
        min_delimiter_count=args.min_delimiter_count,
        min_extension_count=args.min_extension_count,
        min_literal_count=args.min_literal_count,
    )

    selected_path = Path(args.selected_out)
    write_selected_tsv(selected_path, selected)
    report = format_report(
        inventory_path=Path(args.inventory),
        selected_path=selected_path,
        selected=selected,
        stats=stats,
        min_char_count=args.min_char_count,
        min_delimiter_count=args.min_delimiter_count,
        min_extension_count=args.min_extension_count,
        min_literal_count=args.min_literal_count,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_selected: {selected_path}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
