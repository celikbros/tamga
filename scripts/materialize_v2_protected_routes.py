from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tr_tokenizer import TurkishTokenizer  # noqa: E402

from scripts.materialize_v2_soft_morph_artifacts import (  # noqa: E402
    Piece,
    analyze_line,
)


@dataclass(frozen=True)
class ProtectedRouteStats:
    lines: int
    bytes: int
    protected_pieces: int
    unique_protected_surfaces: int
    suffix_tails_after_protected: int
    unique_suffix_tails_after_protected: int
    max_routes_line: int

    @property
    def protected_pieces_per_byte(self) -> float:
        return self.protected_pieces / self.bytes if self.bytes else 0.0


def is_protected_piece(piece: Piece) -> bool:
    return piece.kind.startswith("protected:")


def protected_route_kind(piece: Piece) -> str:
    if not is_protected_piece(piece):
        raise ValueError(f"not a protected piece: {piece}")
    return piece.kind.removeprefix("protected:")


def suffix_tail_protected_base(pieces: list[Piece], index: int) -> Piece | None:
    if pieces[index].kind != "suffix":
        return None
    if index < 2:
        return None
    if pieces[index - 1].kind != "apostrophe":
        return None
    base = pieces[index - 2]
    if not is_protected_piece(base):
        return None
    return base


def line_routes(pieces: list[Piece]) -> list[dict[str, object]]:
    routes: list[dict[str, object]] = []
    for index, piece in enumerate(pieces):
        if is_protected_piece(piece):
            routes.append(
                {
                    "piece_index": index,
                    "route": protected_route_kind(piece),
                    "surface": piece.surface,
                    "bytes": len(piece.surface.encode("utf-8")),
                    "boundary_before": piece.boundary_before,
                }
            )
            continue

        base = suffix_tail_protected_base(pieces, index)
        if base is not None:
            routes.append(
                {
                    "piece_index": index,
                    "route": f"suffix_tail_after_{protected_route_kind(base)}",
                    "surface": piece.surface,
                    "base_surface": base.surface,
                    "bytes": len(piece.surface.encode("utf-8")),
                    "boundary_before": piece.boundary_before,
                }
            )
    return routes


def materialize_protected_routes(
    *,
    input_path: Path,
    jsonl_out: Path,
    inventory_out: Path,
    max_lines: int | None,
    progress: int,
) -> ProtectedRouteStats:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    protected_counts: Counter[tuple[str, str]] = Counter()
    suffix_tail_counts: Counter[tuple[str, str]] = Counter()
    lines = 0
    total_bytes = 0
    protected_pieces = 0
    suffix_tails_after_protected = 0
    max_routes_line = 0

    jsonl_out.parent.mkdir(parents=True, exist_ok=True)
    inventory_out.parent.mkdir(parents=True, exist_ok=True)

    with (
        input_path.open("r", encoding="utf-8") as source,
        jsonl_out.open("w", encoding="utf-8", newline="\n") as target,
    ):
        for raw_line in source:
            if max_lines is not None and lines >= max_lines:
                break

            text = raw_line.rstrip("\n")
            pieces = analyze_line(text, tokenizer)
            routes = line_routes(pieces)

            target.write(
                json.dumps(
                    {
                        "text": text,
                        "routes": routes,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

            lines += 1
            total_bytes += len(text.encode("utf-8"))
            max_routes_line = max(max_routes_line, len(routes))

            for route in routes:
                route_name = str(route["route"])
                surface = str(route["surface"])
                if route_name.startswith("suffix_tail_after_"):
                    suffix_tail_counts[(route_name, surface)] += 1
                    suffix_tails_after_protected += 1
                else:
                    protected_counts[(route_name, surface)] += 1
                    protected_pieces += 1

            if progress > 0 and lines % progress == 0:
                print(
                    f"materialized {lines:,} lines "
                    f"protected={protected_pieces:,} "
                    f"suffix_tails={suffix_tails_after_protected:,}",
                    flush=True,
                )

    with inventory_out.open("w", encoding="utf-8", newline="\n") as inventory:
        inventory.write("category\troute\tsurface\tcount\tbytes\n")
        for (route, surface), count in protected_counts.most_common():
            inventory.write(
                f"protected\t{route}\t{surface}\t{count}\t"
                f"{len(surface.encode('utf-8'))}\n"
            )
        for (route, surface), count in suffix_tail_counts.most_common():
            inventory.write(
                f"suffix_tail\t{route}\t{surface}\t{count}\t"
                f"{len(surface.encode('utf-8'))}\n"
            )

    return ProtectedRouteStats(
        lines=lines,
        bytes=total_bytes,
        protected_pieces=protected_pieces,
        unique_protected_surfaces=len(protected_counts),
        suffix_tails_after_protected=suffix_tails_after_protected,
        unique_suffix_tails_after_protected=len(suffix_tail_counts),
        max_routes_line=max_routes_line,
    )


def format_report(
    *,
    input_path: Path,
    jsonl_out: Path,
    inventory_out: Path,
    stats: ProtectedRouteStats,
    max_lines: int | None,
) -> str:
    return "\n".join(
        [
            "# v2.0 Protected Route Materialization",
            "",
            f"Input: `{input_path.as_posix()}`",
            f"JSONL output: `{jsonl_out.as_posix()}`",
            f"Inventory output: `{inventory_out.as_posix()}`",
            f"Max lines: `{max_lines if max_lines is not None else 'all'}`",
            "",
            "This is the first finite protected-aware implementation step. It",
            "does not train a tokenizer. It records which current tokenizer",
            "pieces route to protected encoders and which Turkish suffix tails",
            "attach after protected bases.",
            "",
            "## Summary",
            "",
            "| Lines | Bytes | Protected pieces | Protected pieces/byte | Unique protected surfaces | Suffix tails after protected | Unique suffix tails | Max routes/line |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| {stats.lines} | {stats.bytes} | {stats.protected_pieces} | "
                f"{stats.protected_pieces_per_byte:.6f} | "
                f"{stats.unique_protected_surfaces} | "
                f"{stats.suffix_tails_after_protected} | "
                f"{stats.unique_suffix_tails_after_protected} | "
                f"{stats.max_routes_line} |"
            ),
            "",
            "## Next Use",
            "",
            "Use the inventory to select finite protected pieces and UDS candidates.",
            "Do not promote rare full protected surfaces by default.",
        ]
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Materialize v2.0 protected route inventory from a raw split.",
    )
    parser.add_argument(
        "--input",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt",
    )
    parser.add_argument(
        "--jsonl-out",
        default="artifacts/private/v2_0_protected_aware/protected_routes.train.jsonl",
    )
    parser.add_argument(
        "--inventory-out",
        default="artifacts/private/v2_0_protected_aware/protected_route_inventory.train.tsv",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_protected_route_materialization.md",
    )
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--progress", type=int, default=1000)
    args = parser.parse_args(argv)

    if args.max_lines is not None and args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")

    input_path = Path(args.input)
    jsonl_out = Path(args.jsonl_out)
    inventory_out = Path(args.inventory_out)
    report_out = Path(args.report_out)

    stats = materialize_protected_routes(
        input_path=input_path,
        jsonl_out=jsonl_out,
        inventory_out=inventory_out,
        max_lines=args.max_lines,
        progress=args.progress,
    )
    report = format_report(
        input_path=input_path,
        jsonl_out=jsonl_out,
        inventory_out=inventory_out,
        stats=stats,
        max_lines=args.max_lines,
    )
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_jsonl: {jsonl_out}")
    print(f"wrote_inventory: {inventory_out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
