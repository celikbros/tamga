from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    _processor_id_to_piece,
    _processor_piece_to_id_safe,
    encode_finite_protected_soft_marker_line_ids,
)
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import load_sp_processor  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass
class SplitStats:
    split: str
    lines: int = 0
    raw_bytes: int = 0
    tokens: int = 0
    fallback_bytes: int = 0
    fallback_reasons: Counter[str] | None = None

    def __post_init__(self) -> None:
        if self.fallback_reasons is None:
            self.fallback_reasons = Counter()

    @property
    def tokens_per_byte(self) -> float:
        return self.tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def fallback_token_rate(self) -> float:
        return self.fallback_bytes / self.tokens if self.tokens else 0.0

    @property
    def fallback_byte_coverage(self) -> float:
        return self.fallback_bytes / self.raw_bytes if self.raw_bytes else 0.0


def load_split_lines(split_dir: Path, split: str) -> list[str]:
    return [
        line.rstrip("\n")
        for line in (split_dir / f"{split}.txt").read_text(encoding="utf-8").splitlines()
    ]


def audit_presplit_fallback_line(
    text: str,
    *,
    processor,
    passthrough_routes: set[str],
) -> Counter[str]:
    pieces = analyze_line(text, TurkishTokenizer(preserve_whitespace=True))
    unknown_id = int(processor.unk_id()) if hasattr(processor, "unk_id") else 0
    counts: Counter[str] = Counter()
    offset = 0
    segment = ""
    segment_start = 0

    def audit_segment(surface: str, *, starts_at_line_start: bool) -> None:
        if not surface:
            return
        proto = processor.EncodeAsImmutableProto(surface)
        for index, piece in enumerate(proto.pieces):
            piece_id = int(piece.id)
            begin = int(piece.begin)
            end = int(piece.end)
            raw_surface = surface[begin:end]
            if not raw_surface:
                continue
            raw_bytes = len(raw_surface.encode("utf-8"))
            if piece_id == unknown_id:
                counts["sp_unk"] += raw_bytes
                continue

            sp_piece = _processor_id_to_piece(processor, piece_id)
            dummy_prefix = (
                index == 0
                and not starts_at_line_start
                and not raw_surface.startswith((" ", "\t", "\r", "\n"))
                and sp_piece.startswith("▁")
            )
            if not dummy_prefix:
                continue

            stripped_piece = sp_piece[1:]
            if not stripped_piece:
                counts["dummy_prefix_drop"] += 0
                continue
            stripped_id = _processor_piece_to_id_safe(processor, stripped_piece)
            if (
                stripped_id >= 0
                and _processor_id_to_piece(processor, stripped_id) == stripped_piece
            ):
                counts["dummy_prefix_rewritten_piece"] += 0
            else:
                counts["dummy_prefix_missing_piece"] += raw_bytes

    def flush_segment() -> None:
        nonlocal segment
        if segment:
            audit_segment(segment, starts_at_line_start=segment_start == 0)
            segment = ""

    for piece in pieces:
        piece_start = offset
        piece_end = piece_start + len(piece.surface)
        if piece.kind.startswith("protected:"):
            route = piece.kind.removeprefix("protected:")
            if route in passthrough_routes:
                flush_segment()
                audit_segment(piece.surface, starts_at_line_start=piece_start == 0)
                offset = piece_end
                segment_start = offset
                continue
            flush_segment()
            offset = piece_end
            segment_start = offset
            continue

        if not segment:
            segment_start = piece_start
        segment += piece.surface
        offset = piece_end

    flush_segment()
    return counts


def audit_split(
    *,
    split: str,
    lines: list[str],
    processor,
    passthrough_routes: set[str],
    progress: int,
) -> SplitStats:
    piece_size = int(processor.GetPieceSize())
    byte_offset = piece_size
    stats = SplitStats(split=split)
    for line_no, text in enumerate(lines, start=1):
        ids, byte_tokens = encode_finite_protected_soft_marker_line_ids(
            text,
            processor=processor,
            selected_pieces=[],
            protected_piece_offset=piece_size,
            insert_soft_markers=False,
            numeric_sp_passthrough=True,
            sp_passthrough_routes=passthrough_routes,
            pre_split_sp_passthrough_routes=True,
        )
        reasons = audit_presplit_fallback_line(
            text,
            processor=processor,
            passthrough_routes=set(passthrough_routes) | {"numeric_like"},
        )
        stats.lines += 1
        stats.raw_bytes += len(text.encode("utf-8"))
        stats.tokens += len(ids)
        stats.fallback_bytes += byte_tokens
        stats.fallback_reasons.update(reasons)
        if sum(reasons.values()) != byte_tokens:
            stats.fallback_reasons["unclassified"] += byte_tokens - sum(reasons.values())
        if progress > 0 and line_no % progress == 0:
            print(
                f"audited {split} {line_no:,} lines fallback_bytes={stats.fallback_bytes:,}",
                flush=True,
            )
    return stats


def format_report(*, split_dir: Path, model: Path, rows: list[SplitStats]) -> str:
    lines = [
        "# v2.1 Presplit Sidecar Fallback Decomposition",
        "",
        f"Split dir: `{split_dir.as_posix()}`",
        f"SP model: `{model.as_posix()}`",
        "",
        "This report decomposes UTF-8 byte fallback in the pre-split sidecar",
        "encoder. Fallback bytes equal fallback tokens because every fallback",
        "token represents one source byte.",
        "",
        "## Summary",
        "",
        "| Split | Lines | Raw bytes | Tokens | Tokens/raw byte | Fallback bytes | Fallback token rate | Fallback byte coverage |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.split} | {row.lines} | {row.raw_bytes} | {row.tokens} | "
            f"{row.tokens_per_byte:.6f} | {row.fallback_bytes} | "
            f"{row.fallback_token_rate:.6f} | {row.fallback_byte_coverage:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Reason Breakdown",
            "",
            "| Split | Reason | Fallback bytes | Share of raw bytes |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for row in rows:
        assert row.fallback_reasons is not None
        for reason, count in sorted(row.fallback_reasons.items()):
            lines.append(
                f"| {row.split} | `{reason}` | {count} | "
                f"{(count / row.raw_bytes if row.raw_bytes else 0.0):.6f} |"
            )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Decompose fallback bytes for v2.1 pre-split sidecar."
    )
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
    )
    parser.add_argument(
        "--model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument("--split", action="append", default=[])
    parser.add_argument("--progress", type=int, default=0)
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_1_presplit_sidecar_fallback_decomposition.md",
    )
    args = parser.parse_args(argv)

    split_dir = Path(args.split_dir)
    model = Path(args.model)
    processor = load_sp_processor(model)
    passthrough_routes = {
        "file_like",
        "apostrophe_surface",
        "non_turkish_latin_word",
        "greek_word",
        "uzbek_apostrophe_word",
        "cyrillic_word",
        "arabic_word",
    }
    selected_splits = args.split or ["train", "valid", "test"]
    rows = [
        audit_split(
            split=split,
            lines=load_split_lines(split_dir, split),
            processor=processor,
            passthrough_routes=passthrough_routes,
            progress=args.progress,
        )
        for split in selected_splits
    ]
    report = format_report(split_dir=split_dir, model=model, rows=rows)
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
