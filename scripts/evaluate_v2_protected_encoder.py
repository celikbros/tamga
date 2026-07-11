from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.analyze_v2_protected_route_inventory import (  # noqa: E402
    RouteEntry,
    load_route_inventory,
)


# Moved to the production package (Faz 2); re-exported for compatibility.
from tr_tokenizer.production.config import (  # noqa: E402,F401
    ProtectedPiece,
    load_selected_pieces,
)


@dataclass(frozen=True)
class EncodedSurface:
    piece_tokens: int
    byte_tokens: int
    byte_fallback_bytes: int

    @property
    def total_tokens(self) -> int:
        return self.piece_tokens + self.byte_tokens


@dataclass(frozen=True)
class EncoderStats:
    protected_surfaces: int
    protected_occurrences: int
    source_bytes: int
    piece_tokens: int
    byte_tokens: int
    byte_fallback_bytes: int
    selected_pieces: int
    byte_fallback_reserved: int = 256

    @property
    def total_tokens(self) -> int:
        return self.piece_tokens + self.byte_tokens

    @property
    def tokens_per_source_byte(self) -> float:
        return self.total_tokens / self.source_bytes if self.source_bytes else 0.0

    @property
    def byte_fallback_byte_rate(self) -> float:
        return self.byte_fallback_bytes / self.source_bytes if self.source_bytes else 0.0

    @property
    def byte_token_rate(self) -> float:
        return self.byte_tokens / self.total_tokens if self.total_tokens else 0.0


def protected_entries(entries: list[RouteEntry]) -> list[RouteEntry]:
    return [entry for entry in entries if entry.category == "protected"]


def greedy_encode_surface(surface: str, pieces: list[str]) -> EncodedSurface:
    ordered = sorted((piece for piece in pieces if piece), key=lambda item: (-len(item), item))
    position = 0
    piece_tokens = 0
    byte_tokens = 0
    byte_fallback_bytes = 0

    while position < len(surface):
        matched = ""
        for piece in ordered:
            if surface.startswith(piece, position):
                matched = piece
                break

        if matched:
            piece_tokens += 1
            position += len(matched)
        else:
            char = surface[position]
            encoded = char.encode("utf-8")
            byte_tokens += len(encoded)
            byte_fallback_bytes += len(encoded)
            position += 1

    return EncodedSurface(
        piece_tokens=piece_tokens,
        byte_tokens=byte_tokens,
        byte_fallback_bytes=byte_fallback_bytes,
    )


def evaluate_encoder(
    *,
    inventory_entries: list[RouteEntry],
    selected_pieces: list[ProtectedPiece],
) -> tuple[EncoderStats, dict[str, tuple[int, int, int, int, int]]]:
    piece_strings = [piece.piece for piece in selected_pieces]
    route_unique: Counter[str] = Counter()
    route_occurrences: Counter[str] = Counter()
    route_source_bytes: Counter[str] = Counter()
    route_total_tokens: Counter[str] = Counter()
    route_byte_fallback_bytes: Counter[str] = Counter()

    source_bytes = 0
    protected_occurrences = 0
    piece_tokens = 0
    byte_tokens = 0
    byte_fallback_bytes = 0
    protected = protected_entries(inventory_entries)

    for entry in protected:
        encoded = greedy_encode_surface(entry.surface, piece_strings)
        weighted_source_bytes = entry.count * entry.bytes
        source_bytes += weighted_source_bytes
        protected_occurrences += entry.count
        piece_tokens += entry.count * encoded.piece_tokens
        byte_tokens += entry.count * encoded.byte_tokens
        byte_fallback_bytes += entry.count * encoded.byte_fallback_bytes

        route_unique[entry.route] += 1
        route_occurrences[entry.route] += entry.count
        route_source_bytes[entry.route] += weighted_source_bytes
        route_total_tokens[entry.route] += entry.count * encoded.total_tokens
        route_byte_fallback_bytes[entry.route] += entry.count * encoded.byte_fallback_bytes

    route_summary = {
        route: (
            route_unique[route],
            route_occurrences[route],
            route_source_bytes[route],
            route_total_tokens[route],
            route_byte_fallback_bytes[route],
        )
        for route in sorted(route_unique)
    }
    stats = EncoderStats(
        protected_surfaces=len(protected),
        protected_occurrences=protected_occurrences,
        source_bytes=source_bytes,
        piece_tokens=piece_tokens,
        byte_tokens=byte_tokens,
        byte_fallback_bytes=byte_fallback_bytes,
        selected_pieces=len(selected_pieces),
    )
    return stats, route_summary


def _fmt_float(value: float, digits: int = 6) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    *,
    inventory_path: Path,
    selected_path: Path,
    stats: EncoderStats,
    route_summary: dict[str, tuple[int, int, int, int, int]],
) -> str:
    lines = [
        "# v2.0 Protected Encoder Diagnostic",
        "",
        f"Inventory: `{inventory_path.as_posix()}`",
        f"Selected protected pieces: `{selected_path.as_posix()}`",
        "",
        "This diagnostic evaluates a stateless protected encoder that greedily",
        "uses finite protected pieces and falls back to UTF-8 byte tokens for",
        "all remaining protected text. It does not train a tokenizer.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| protected unique surfaces | {stats.protected_surfaces} |",
        f"| protected occurrences | {stats.protected_occurrences} |",
        f"| source bytes | {stats.source_bytes} |",
        f"| selected protected pieces | {stats.selected_pieces} |",
        f"| mandatory byte fallback pieces | {stats.byte_fallback_reserved} |",
        f"| encoded tokens | {stats.total_tokens} |",
        f"| piece tokens | {stats.piece_tokens} |",
        f"| byte fallback tokens | {stats.byte_tokens} |",
        f"| tokens/source byte | {_fmt_float(stats.tokens_per_source_byte)} |",
        f"| byte fallback byte rate | {_fmt_float(stats.byte_fallback_byte_rate)} |",
        f"| byte token rate | {_fmt_float(stats.byte_token_rate)} |",
        "",
        "## Route Summary",
        "",
        "| Route | Unique surfaces | Occurrences | Source bytes | Tokens/source byte | Byte fallback byte rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for route, (unique, occurrences, source_bytes, total_tokens, fallback_bytes) in route_summary.items():
        tokens_per_byte = total_tokens / source_bytes if source_bytes else 0.0
        fallback_rate = fallback_bytes / source_bytes if source_bytes else 0.0
        lines.append(
            f"| {route} | {unique} | {occurrences} | {source_bytes} | "
            f"{_fmt_float(tokens_per_byte)} | {_fmt_float(fallback_rate)} |"
        )

    lines.extend(
        [
            "",
            "## Decision Hint",
            "",
            "If byte fallback rate is low, the finite protected-piece path is",
            "viable enough for a full tokenizer prototype. If it is high on",
            "file/code/URL routes, protected piece selection needs another pass.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Evaluate finite protected-piece encoder against route inventory.",
    )
    parser.add_argument(
        "--inventory",
        default="artifacts/private/v2_0_protected_aware/protected_route_inventory.train.tsv",
    )
    parser.add_argument(
        "--selected",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--report-out", default="artifacts/v2_0_protected_encoder_diagnostic.md")
    args = parser.parse_args(argv)

    inventory_entries = load_route_inventory(args.inventory)
    selected_pieces = load_selected_pieces(args.selected)
    stats, route_summary = evaluate_encoder(
        inventory_entries=inventory_entries,
        selected_pieces=selected_pieces,
    )
    report = format_report(
        inventory_path=Path(args.inventory),
        selected_path=Path(args.selected),
        stats=stats,
        route_summary=route_summary,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
