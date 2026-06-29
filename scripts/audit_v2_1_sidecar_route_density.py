from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    encode_finite_protected_soft_marker_line_ids,
    load_sp_processor,
    _processor_eos_id,
    _processor_piece_size,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


DEFAULT_PASSTHROUGH_ROUTES = frozenset(
    {
        "file_like",
        "apostrophe_surface",
        "non_turkish_latin_word",
        "greek_word",
        "uzbek_apostrophe_word",
        "cyrillic_word",
        "arabic_word",
        "percent_encoded",
        "azerbaijani_word",
    }
)


@dataclass
class RouteStats:
    occurrences: int = 0
    bytes: int = 0
    lines: set[int] = field(default_factory=set)
    surfaces: Counter[str] = field(default_factory=Counter)

    def add(self, *, surface: str, line_number: int) -> None:
        self.occurrences += 1
        self.bytes += len(surface.encode("utf-8"))
        self.lines.add(line_number)
        self.surfaces[surface] += 1


@dataclass
class DensityStats:
    split: str
    lines: int = 0
    raw_bytes: int = 0
    protected_spans: int = 0
    protected_bytes: int = 0
    protected_lines: set[int] = field(default_factory=set)
    routes: dict[str, RouteStats] = field(default_factory=lambda: defaultdict(RouteStats))
    sp_tokens: int = 0
    passthrough_tokens: int = 0
    presplit_tokens: int = 0
    passthrough_fallback_tokens: int = 0
    presplit_fallback_tokens: int = 0

    @property
    def protected_bytes_share(self) -> float:
        return self.protected_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def protected_line_share(self) -> float:
        return len(self.protected_lines) / self.lines if self.lines else 0.0

    @property
    def sp_tokens_per_byte(self) -> float:
        return self.sp_tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def passthrough_tokens_per_byte(self) -> float:
        return self.passthrough_tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def presplit_tokens_per_byte(self) -> float:
        return self.presplit_tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def presplit_tax_tokens_per_byte(self) -> float:
        return self.presplit_tokens_per_byte - self.passthrough_tokens_per_byte

    @property
    def presplit_tax_relative(self) -> float:
        base = self.passthrough_tokens_per_byte
        return self.presplit_tax_tokens_per_byte / base if base else 0.0


def _read_lines(path: Path, max_lines: int | None) -> list[str]:
    lines: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if max_lines is not None and len(lines) >= max_lines:
                break
            lines.append(raw_line.rstrip("\n"))
    return lines


def audit_split(
    *,
    path: Path,
    split: str,
    processor,
    max_lines: int | None,
    progress: int,
    include_eos: bool,
    passthrough_routes: frozenset[str],
) -> DensityStats:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    piece_size = _processor_piece_size(processor) if processor is not None else 0
    eos_id = _processor_eos_id(processor) if processor is not None else -1
    lines = _read_lines(path, max_lines)
    stats = DensityStats(split=split)

    for line_number, text in enumerate(lines, start=1):
        stats.lines += 1
        stats.raw_bytes += len(text.encode("utf-8"))
        if processor is not None:
            sp_ids = processor.EncodeAsIds(text)
            stats.sp_tokens += len(sp_ids)

            passthrough_ids, passthrough_fallback = (
                encode_finite_protected_soft_marker_line_ids(
                    text,
                    processor=processor,
                    selected_pieces=[],
                    protected_piece_offset=piece_size,
                    insert_soft_markers=False,
                    numeric_sp_passthrough=True,
                    sp_passthrough_routes=passthrough_routes,
                    pre_split_sp_passthrough_routes=False,
                )
            )
            presplit_ids, presplit_fallback = encode_finite_protected_soft_marker_line_ids(
                text,
                processor=processor,
                selected_pieces=[],
                protected_piece_offset=piece_size,
                insert_soft_markers=False,
                numeric_sp_passthrough=True,
                sp_passthrough_routes=passthrough_routes,
                pre_split_sp_passthrough_routes=True,
            )
            stats.passthrough_tokens += len(passthrough_ids)
            stats.presplit_tokens += len(presplit_ids)
            stats.passthrough_fallback_tokens += passthrough_fallback
            stats.presplit_fallback_tokens += presplit_fallback
            if include_eos and eos_id >= 0:
                stats.sp_tokens += 1
                stats.passthrough_tokens += 1
                stats.presplit_tokens += 1

        pieces = analyze_line(text, tokenizer)
        line_has_protected = False
        for piece in pieces:
            if not piece.kind.startswith("protected:"):
                continue
            route = piece.kind.removeprefix("protected:")
            surface_bytes = len(piece.surface.encode("utf-8"))
            stats.protected_spans += 1
            stats.protected_bytes += surface_bytes
            stats.routes[route].add(surface=piece.surface, line_number=line_number)
            line_has_protected = True
        if line_has_protected:
            stats.protected_lines.add(line_number)

        if progress > 0 and stats.lines % progress == 0:
            print(
                f"audited {split} {stats.lines:,} lines "
                f"protected_spans={stats.protected_spans:,}",
                flush=True,
            )

    return stats


def merge_stats(rows: list[DensityStats]) -> DensityStats:
    merged = DensityStats(split="all")
    line_offset = 0
    for row in rows:
        merged.lines += row.lines
        merged.raw_bytes += row.raw_bytes
        merged.protected_spans += row.protected_spans
        merged.protected_bytes += row.protected_bytes
        merged.sp_tokens += row.sp_tokens
        merged.passthrough_tokens += row.passthrough_tokens
        merged.presplit_tokens += row.presplit_tokens
        merged.passthrough_fallback_tokens += row.passthrough_fallback_tokens
        merged.presplit_fallback_tokens += row.presplit_fallback_tokens
        for line_no in row.protected_lines:
            merged.protected_lines.add(line_offset + line_no)
        for route, stats in row.routes.items():
            target = merged.routes[route]
            target.occurrences += stats.occurrences
            target.bytes += stats.bytes
            target.surfaces.update(stats.surfaces)
            for line_no in stats.lines:
                target.lines.add(line_offset + line_no)
        line_offset += row.lines
    return merged


def _fmt(value: float) -> str:
    return f"{value:.6f}"


def _maybe_fmt(value: float, enabled: bool) -> str:
    return _fmt(value) if enabled else "n/a"


def _row(stats: DensityStats, *, token_pressure: bool) -> str:
    return (
        f"| `{stats.split}` | {stats.lines} | {stats.raw_bytes} | "
        f"{stats.protected_spans} | {stats.protected_bytes} | "
        f"{_fmt(stats.protected_bytes_share)} | {_fmt(stats.protected_line_share)} | "
        f"{_maybe_fmt(stats.sp_tokens_per_byte, token_pressure)} | "
        f"{_maybe_fmt(stats.passthrough_tokens_per_byte, token_pressure)} | "
        f"{_maybe_fmt(stats.presplit_tokens_per_byte, token_pressure)} | "
        f"{_maybe_fmt(stats.presplit_tax_tokens_per_byte, token_pressure)} | "
        f"{_maybe_fmt(stats.presplit_tax_relative, token_pressure)} |"
    )


def format_report(
    *,
    input_desc: str,
    sp_model: Path,
    rows: list[DensityStats],
    max_lines: int | None,
    include_eos: bool,
    token_pressure: bool,
) -> str:
    merged = merge_stats(rows)
    output = [
        "# v2.1 Sidecar Protected Route Density Audit",
        "",
        f"Input: `{input_desc}`",
        f"SP model: `{sp_model.as_posix()}`",
        f"Max lines per split/file: `{max_lines if max_lines is not None else 'all'}`",
        f"Include EOS in token pressure: `{include_eos}`",
        f"Token pressure mode: `{token_pressure}`",
        "",
        "This audit estimates whether the selected passthrough sidecar baseline",
        "is exposed to a different protected-span density than the v1.8 pilot.",
        "It also reports the local pre-split token tax on the same text.",
        "",
        "## Split Summary",
        "",
        "| Split | Lines | Raw bytes | Protected spans | Protected bytes | Protected bytes/raw byte | Protected line share | SP tokens/raw byte | Passthrough tokens/raw byte | Pre-split tokens/raw byte | Pre-split tax tokens/raw byte | Pre-split tax relative |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        output.append(_row(row, token_pressure=token_pressure))
    if len(rows) > 1:
        output.append(_row(merged, token_pressure=token_pressure))

    output.extend(
        [
            "",
            "## Route Summary",
            "",
            "| Route | Occurrences | Bytes | Bytes/raw byte | Line share | Unique surfaces | Top surfaces |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for route, route_stats in sorted(
        merged.routes.items(),
        key=lambda item: item[1].bytes,
        reverse=True,
    ):
        top = ", ".join(
            f"`{surface}`:{count}"
            for surface, count in route_stats.surfaces.most_common(8)
        )
        output.append(
            f"| `{route}` | {route_stats.occurrences} | {route_stats.bytes} | "
            f"{_fmt(route_stats.bytes / merged.raw_bytes if merged.raw_bytes else 0.0)} | "
            f"{_fmt(len(route_stats.lines) / merged.lines if merged.lines else 0.0)} | "
            f"{len(route_stats.surfaces)} | {top} |"
        )

    output.extend(
        [
            "",
            "## Gate",
            "",
            "Use this report before any future global pre-split decision.",
            "",
            "- If protected bytes/raw byte is much higher than the v1.8 pilot, the",
            "  global pre-split tax is likely understated by previous results.",
            "- If only a few routes dominate, prefer selective pre-split by route",
            "  class over global pre-split.",
            "- Run with `--with-token-pressure` only for small samples or when",
            "  the extra encoding cost is acceptable.",
            "- `sp64_protected_passthrough_sidecar` remains the default v2.1",
            "  baseline unless token-boundary alignment is a committed requirement.",
        ]
    )
    return "\n".join(output) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Audit v2.1 sidecar protected route density.")
    parser.add_argument(
        "--split-dir",
        help="Directory containing train.txt/valid.txt/test.txt.",
    )
    parser.add_argument(
        "--input",
        action="append",
        help="Standalone UTF-8 text file. Can be passed multiple times.",
    )
    parser.add_argument(
        "--split",
        action="append",
        choices=["train", "valid", "test"],
        help="Split name to scan under --split-dir. Defaults to valid,test.",
    )
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument("--include-eos", action="store_true")
    parser.add_argument(
        "--with-token-pressure",
        action="store_true",
        help="Also encode SP/passthrough/pre-split token streams. Slower.",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_1_sidecar_route_density_audit.md",
    )
    args = parser.parse_args(argv)

    if not args.split_dir and not args.input:
        raise ValueError("Provide --split-dir or at least one --input file.")
    if args.max_lines is not None and args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")

    processor = load_sp_processor(Path(args.sp_model)) if args.with_token_pressure else None
    rows: list[DensityStats] = []
    input_desc_parts: list[str] = []

    if args.split_dir:
        split_dir = Path(args.split_dir)
        splits = args.split or ["valid", "test"]
        input_desc_parts.append(split_dir.as_posix())
        for split in splits:
            rows.append(
                audit_split(
                    path=split_dir / f"{split}.txt",
                    split=split,
                    processor=processor,
                    max_lines=args.max_lines,
                    progress=args.progress,
                    include_eos=args.include_eos,
                    passthrough_routes=DEFAULT_PASSTHROUGH_ROUTES,
                )
            )

    for raw_input in args.input or []:
        path = Path(raw_input)
        input_desc_parts.append(path.as_posix())
        rows.append(
            audit_split(
                path=path,
                split=path.stem,
                processor=processor,
                max_lines=args.max_lines,
                progress=args.progress,
                include_eos=args.include_eos,
                passthrough_routes=DEFAULT_PASSTHROUGH_ROUTES,
            )
        )

    report = format_report(
        input_desc=", ".join(input_desc_parts),
        sp_model=Path(args.sp_model),
        rows=rows,
        max_lines=args.max_lines,
        include_eos=args.include_eos,
        token_pressure=args.with_token_pressure,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
