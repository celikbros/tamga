from __future__ import annotations

from array import array
from collections import Counter
from dataclasses import dataclass
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Consumer (LLM-team) environment root; see run_v3_8_final_release_gates.py.
GARDASH_ROOT = os.environ.get("GARDASH_ROOT", "C:/CELIK-GARDASH")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_v2_1_sidecar_operation_simulation import (  # noqa: E402
    Span,
    char_to_byte_offsets,
    protected_spans,
)
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    load_sp_processor,
    selected_piece_strings,
)
from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    TokenizerConfig,
    _processor_eos_id,
    _processor_piece_size,
    _processor_decode_ids,
    load_probe_config,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass
class TokenizeStats:
    lines: int = 0
    raw_bytes: int = 0
    tokens: int = 0
    eos_tokens: int = 0
    fallback_tokens: int = 0
    masked_tokens: int = 0
    protected_spans: int = 0
    protected_bytes: int = 0
    sp_alignment_mismatches: int = 0
    max_token_id: int = 0
    route_counts: Counter[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.route_counts is None:
            self.route_counts = Counter()

    @property
    def tokens_per_byte(self) -> float:
        return self.tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def fallback_rate(self) -> float:
        return self.fallback_tokens / self.tokens if self.tokens else 0.0

    @property
    def masked_token_rate(self) -> float:
        return self.masked_tokens / self.tokens if self.tokens else 0.0


@dataclass(frozen=True)
class EncodedTokenSpan:
    token_id: int
    byte_start: int
    byte_end: int


def find_tokenizer(config_path: Path, name: str) -> TokenizerConfig:
    config = load_probe_config(config_path)
    for tokenizer in config.tokenizers:
        if tokenizer.name == name:
            return tokenizer
    available = ", ".join(tokenizer.name for tokenizer in config.tokenizers)
    raise ValueError(f"tokenizer {name!r} not found. Available: {available}")


def normalize_max_lines(value: int | None) -> int | None:
    if value is not None and value <= 0:
        return None
    return value


def write_uint32(handle: Any, values: list[int]) -> None:
    data = array("I", values)
    if data.itemsize != 4:
        raise RuntimeError("array('I') is not uint32 on this platform")
    if sys.byteorder != "little":
        data.byteswap()
    data.tofile(handle)


def span_to_json(span: Span) -> dict[str, object]:
    return {
        "route": span.route,
        "byte_start": span.byte_start,
        "byte_end": span.byte_end,
        "char_start": span.char_start,
        "char_end": span.char_end,
        "surface": span.surface,
    }


def token_mask_for_line(*, token_spans: list[EncodedTokenSpan], spans: list[Span]) -> bytearray:
    mask = bytearray([1] * len(token_spans))
    for span in spans:
        for index, token in enumerate(token_spans):
            if token.byte_start < span.byte_end and span.byte_start < token.byte_end:
                mask[index] = 0
    return mask


def encode_sp_segment_with_offsets(
    *,
    processor: Any,
    text: str,
    base_byte: int,
    byte_offset: int,
) -> tuple[list[int], list[EncodedTokenSpan], int]:
    if not text:
        return [], [], 0
    proto = processor.EncodeAsImmutableProto(text)
    piece_ids = [int(piece.id) for piece in proto.pieces if int(piece.begin) != int(piece.end)]
    decoded = _processor_decode_ids(processor, piece_ids)
    local_byte_offsets = char_to_byte_offsets(text)
    if decoded == text:
        spans = [
            EncodedTokenSpan(
                token_id=int(piece.id),
                byte_start=base_byte + local_byte_offsets[int(piece.begin)],
                byte_end=base_byte + local_byte_offsets[int(piece.end)],
            )
            for piece in proto.pieces
            if int(piece.begin) != int(piece.end)
        ]
        return piece_ids, spans, 0

    ids: list[int] = []
    spans: list[EncodedTokenSpan] = []
    fallback_tokens = 0
    unknown_id = int(processor.unk_id()) if hasattr(processor, "unk_id") else 0
    for piece in proto.pieces:
        piece_id = int(piece.id)
        begin = int(piece.begin)
        end = int(piece.end)
        if begin == end:
            continue
        begin_byte = local_byte_offsets[begin]
        end_byte = local_byte_offsets[end]
        if piece_id != unknown_id:
            ids.append(piece_id)
            spans.append(
                EncodedTokenSpan(
                    token_id=piece_id,
                    byte_start=base_byte + begin_byte,
                    byte_end=base_byte + end_byte,
                )
            )
            continue
        raw_bytes = text[begin:end].encode("utf-8")
        for offset, raw_byte in enumerate(raw_bytes):
            token_id = byte_offset + raw_byte
            ids.append(token_id)
            spans.append(
                EncodedTokenSpan(
                    token_id=token_id,
                    byte_start=base_byte + begin_byte + offset,
                    byte_end=base_byte + begin_byte + offset + 1,
                )
            )
        fallback_tokens += len(raw_bytes)
    return ids, spans, fallback_tokens


def encode_protected_surface_with_offsets(
    *,
    surface: str,
    base_byte: int,
    selected: list[str],
    piece_to_id: dict[str, int],
    byte_offset: int,
) -> tuple[list[int], list[EncodedTokenSpan], int]:
    ids: list[int] = []
    spans: list[EncodedTokenSpan] = []
    fallback_tokens = 0
    byte_offsets = char_to_byte_offsets(surface)
    position = 0
    while position < len(surface):
        match = ""
        for piece in selected:
            if surface.startswith(piece, position):
                match = piece
                break
        if match:
            token_id = piece_to_id[match]
            next_position = position + len(match)
            ids.append(token_id)
            spans.append(
                EncodedTokenSpan(
                    token_id=token_id,
                    byte_start=base_byte + byte_offsets[position],
                    byte_end=base_byte + byte_offsets[next_position],
                )
            )
            position = next_position
            continue

        raw_bytes = surface[position].encode("utf-8")
        char_byte_start = byte_offsets[position]
        for offset, raw_byte in enumerate(raw_bytes):
            token_id = byte_offset + raw_byte
            ids.append(token_id)
            spans.append(
                EncodedTokenSpan(
                    token_id=token_id,
                    byte_start=base_byte + char_byte_start + offset,
                    byte_end=base_byte + char_byte_start + offset + 1,
                )
            )
        fallback_tokens += len(raw_bytes)
        position += 1
    return ids, spans, fallback_tokens


def encode_line(
    *,
    tokenizer: TokenizerConfig,
    processor: Any,
    selected: list[str],
    piece_size: int,
    eos_id: int,
    text: str,
    append_eos: bool,
) -> tuple[list[int], list[EncodedTokenSpan], int]:
    if (
        tokenizer.kind != "finite_protected_marker_stripped_numeric_sp"
        or tokenizer.isolate_sp_passthrough_routes
        or tokenizer.byte_fallback_crossing_pieces
        or tokenizer.pre_split_sp_passthrough_routes
    ):
        raise ValueError("v3.1 corpus smoke currently supports route-only numeric-SP sidecar config")

    detector = TurkishTokenizer(preserve_whitespace=True)
    passthrough_routes = set(tokenizer.sp_passthrough_routes)
    passthrough_routes.add("numeric_like")
    byte_offset = piece_size + len(selected)
    piece_to_id = {piece: piece_size + index for index, piece in enumerate(selected)}
    ids: list[int] = []
    token_spans: list[EncodedTokenSpan] = []
    fallback_tokens = 0
    segment = ""
    segment_start_byte = 0
    byte_position = 0

    def flush_segment() -> None:
        nonlocal segment, segment_start_byte, fallback_tokens
        if not segment:
            return
        segment_ids, segment_spans, byte_tokens = encode_sp_segment_with_offsets(
            processor=processor,
            text=segment,
            base_byte=segment_start_byte,
            byte_offset=byte_offset,
        )
        ids.extend(segment_ids)
        token_spans.extend(segment_spans)
        fallback_tokens += byte_tokens
        segment = ""

    from scripts.materialize_v2_soft_morph_artifacts import analyze_line

    for piece in analyze_line(text, detector):
        surface = piece.surface
        surface_bytes = len(surface.encode("utf-8"))
        piece_start_byte = byte_position
        piece_end_byte = piece_start_byte + surface_bytes
        if piece.kind.startswith("protected:"):
            route = piece.kind.removeprefix("protected:")
            if route in passthrough_routes:
                if not segment:
                    segment_start_byte = piece_start_byte
                segment += surface
                byte_position = piece_end_byte
                continue
            flush_segment()
            protected_ids, protected_spans_out, byte_tokens = encode_protected_surface_with_offsets(
                surface=surface,
                base_byte=piece_start_byte,
                selected=selected,
                piece_to_id=piece_to_id,
                byte_offset=byte_offset,
            )
            ids.extend(protected_ids)
            token_spans.extend(protected_spans_out)
            fallback_tokens += byte_tokens
            byte_position = piece_end_byte
            continue

        if not segment:
            segment_start_byte = piece_start_byte
        segment += surface
        byte_position = piece_end_byte

    flush_segment()
    if append_eos and eos_id >= 0:
        ids.append(eos_id)
        token_spans.append(
            EncodedTokenSpan(
                token_id=eos_id,
                byte_start=byte_position,
                byte_end=byte_position,
            )
        )
    return ids, token_spans, fallback_tokens


def format_report(
    *,
    input_path: Path,
    out_dir: Path,
    tokenizer_name: str,
    stats: TokenizeStats,
    append_eos: bool,
    token_dtype: str,
) -> str:
    route_lines = [
        "| Route | Spans |",
        "| --- | ---: |",
    ]
    for route, count in stats.route_counts.most_common():
        route_lines.append(f"| `{route}` | {count} |")

    return "\n".join(
        [
            "# v3.1 Corpus Tokenization Smoke",
            "",
            f"Input: `{input_path.as_posix()}`",
            f"Output dir: `{out_dir.as_posix()}`",
            f"Tokenizer: `{tokenizer_name}`",
            f"Append EOS: `{append_eos}`",
            "",
            "This is a reference smoke for the binary LLM handoff format. It is not",
            "an optimized production tokenizer.",
            "",
            "## Outputs",
            "",
            "| File | Meaning |",
            "| --- | --- |",
            "| `tokens.bin` | Flat little-endian uint32 token ids. |",
            "| `loss_mask.bin` | One uint8 per token: 1=train, 0=masked protected overlap. |",
            "| `index.jsonl` | Per-line token offsets into the flat token stream. |",
            "| `sidecar.jsonl` | Protected span byte/char offsets. |",
            "| `manifest.json` | Machine-readable summary and format metadata. |",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| lines | {stats.lines} |",
            f"| raw bytes | {stats.raw_bytes} |",
            f"| tokens | {stats.tokens} |",
            f"| tokens/raw byte | {stats.tokens_per_byte:.6f} |",
            f"| eos tokens | {stats.eos_tokens} |",
            f"| fallback tokens | {stats.fallback_tokens} |",
            f"| fallback rate | {stats.fallback_rate:.6f} |",
            f"| masked tokens | {stats.masked_tokens} |",
            f"| masked token rate | {stats.masked_token_rate:.6f} |",
            f"| protected spans | {stats.protected_spans} |",
            f"| protected bytes | {stats.protected_bytes} |",
            f"| sp alignment mismatches | {stats.sp_alignment_mismatches} |",
            f"| max token id | {stats.max_token_id} |",
            f"| token dtype | {token_dtype} |",
            "",
            "## Routes",
            "",
            *route_lines,
            "",
            "## Gate",
            "",
            "- `sp_alignment_mismatches` should be zero or explained before using",
            "  `loss_mask.bin` as a training artifact.",
            "- This smoke validates the file contract; production throughput is a",
            "  separate Rust/C++ or offline preprocessing task.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Materialize a v3.1 tokenization smoke package.")
    parser.add_argument(
        "--config",
        default=f"{GARDASH_ROOT}/configs/tokenizer_v3_0/v3_0_gardash_sidecar.toml",
    )
    parser.add_argument("--tokenizer", default="sp64_protected_passthrough_sidecar")
    parser.add_argument(
        "--input",
        default=f"{GARDASH_ROOT}/datasets/tokenizer_v3_0/real_mix_60k_sample.txt",
    )
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--report-out", required=True)
    parser.add_argument(
        "--max-lines",
        type=int,
        default=100,
        help="Maximum input lines to tokenize. Use 0 or a negative value for all lines.",
    )
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--append-eos", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args(argv)
    max_lines = normalize_max_lines(args.max_lines)

    config_path = Path(args.config)
    input_path = Path(args.input)
    out_dir = Path(args.out_dir)
    report_out = Path(args.report_out)
    tokenizer = find_tokenizer(config_path, args.tokenizer)
    if tokenizer.path is None:
        raise ValueError(f"tokenizer {args.tokenizer!r} has no SP model path")

    processor = load_sp_processor(tokenizer.path)
    selected = selected_piece_strings(tokenizer.selected_pieces) if tokenizer.selected_pieces else []
    piece_size = _processor_piece_size(processor)
    eos_id = _processor_eos_id(processor)
    detector = TurkishTokenizer(preserve_whitespace=True)
    stats = TokenizeStats()

    out_dir.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    tokens_path = out_dir / "tokens.bin"
    mask_path = out_dir / "loss_mask.bin"
    index_path = out_dir / "index.jsonl"
    sidecar_path = out_dir / "sidecar.jsonl"
    manifest_path = out_dir / "manifest.json"

    token_offset = 0
    with (
        input_path.open("r", encoding="utf-8") as source,
        tokens_path.open("wb") as tokens_file,
        mask_path.open("wb") as mask_file,
        index_path.open("w", encoding="utf-8", newline="\n") as index_file,
        sidecar_path.open("w", encoding="utf-8", newline="\n") as sidecar_file,
    ):
        for line_number, raw_line in enumerate(source, start=1):
            if max_lines is not None and stats.lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            ids, token_spans, fallback_tokens = encode_line(
                tokenizer=tokenizer,
                processor=processor,
                selected=selected,
                piece_size=piece_size,
                eos_id=eos_id,
                text=text,
                append_eos=args.append_eos,
            )
            spans = protected_spans(text, detector)
            mask = token_mask_for_line(token_spans=token_spans, spans=spans)
            mismatch = len(ids) != len(token_spans)

            write_uint32(tokens_file, ids)
            mask_file.write(mask)
            token_end = token_offset + len(ids)
            index_file.write(
                json.dumps(
                    {
                        "line_number": line_number,
                        "raw_bytes": len(text.encode("utf-8")),
                        "token_start": token_offset,
                        "token_end": token_end,
                        "token_count": len(ids),
                        "masked_tokens": mask.count(0),
                        "fallback_source_tokens": fallback_tokens,
                        "sidecar_spans": len(spans),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            sidecar_file.write(
                json.dumps(
                    {
                        "schema_version": "v2.2-sidecar-jsonl-1",
                        "tokenizer": args.tokenizer,
                        "line_number": line_number,
                        "raw_bytes": len(text.encode("utf-8")),
                        "token_start": token_offset,
                        "token_end": token_end,
                        "token_count": len(ids),
                        "fallback_source_tokens": fallback_tokens,
                        "spans": [span_to_json(span) for span in spans],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

            stats.lines += 1
            stats.raw_bytes += len(text.encode("utf-8"))
            stats.tokens += len(ids)
            stats.eos_tokens += 1 if args.append_eos and eos_id >= 0 else 0
            stats.fallback_tokens += fallback_tokens
            stats.masked_tokens += mask.count(0)
            stats.protected_spans += len(spans)
            stats.protected_bytes += sum(span.byte_len for span in spans)
            stats.sp_alignment_mismatches += 1 if mismatch else 0
            stats.max_token_id = max(stats.max_token_id, max(ids, default=0))
            stats.route_counts.update(span.route for span in spans)
            token_offset = token_end

            if args.progress > 0 and stats.lines % args.progress == 0:
                print(
                    f"tokenized {stats.lines:,} lines tokens={stats.tokens:,} "
                    f"masked={stats.masked_tokens:,}",
                    flush=True,
                )

    manifest = {
        "schema_version": "v3.1-tokenized-corpus-smoke-1",
        "tokenizer": args.tokenizer,
        "input": str(input_path),
        "outputs": {
            "tokens": str(tokens_path),
            "loss_mask": str(mask_path),
            "index": str(index_path),
            "sidecar": str(sidecar_path),
        },
        "format": {
            "token_dtype": "uint32_le",
            "loss_mask_dtype": "uint8",
            "loss_mask_values": {"train": 1, "masked": 0},
            "append_eos": args.append_eos and eos_id >= 0,
            "eos_id": eos_id,
        },
        "summary": {
            "lines": stats.lines,
            "raw_bytes": stats.raw_bytes,
            "tokens": stats.tokens,
            "tokens_per_byte": stats.tokens_per_byte,
            "fallback_tokens": stats.fallback_tokens,
            "fallback_rate": stats.fallback_rate,
            "masked_tokens": stats.masked_tokens,
            "masked_token_rate": stats.masked_token_rate,
            "protected_spans": stats.protected_spans,
            "protected_bytes": stats.protected_bytes,
            "sp_alignment_mismatches": stats.sp_alignment_mismatches,
            "max_token_id": stats.max_token_id,
            "route_counts": dict(stats.route_counts),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    report = format_report(
        input_path=input_path,
        out_dir=out_dir,
        tokenizer_name=args.tokenizer,
        stats=stats,
        append_eos=args.append_eos and eos_id >= 0,
        token_dtype="uint32_le",
    )
    report_out.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    print(f"wrote_manifest: {manifest_path}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
