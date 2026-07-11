from __future__ import annotations

from array import array
from collections import Counter
from dataclasses import dataclass, field
import argparse
import hashlib
import json
from multiprocessing import get_context
import os
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_v2_1_sidecar_operation_simulation import protected_spans  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    load_sp_processor,
    selected_piece_strings,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    TokenizerConfig,
    _processor_decode_ids,
    _processor_eos_id,
    _processor_piece_size,
)
from scripts.tokenize_v3_1_corpus_smoke import (  # noqa: E402
    EncodedTokenSpan,
    find_tokenizer,
    normalize_max_lines,
    span_to_json,
    token_mask_for_line,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass
class CorpusStats:
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
    route_counts: Counter[str] = field(default_factory=Counter)

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
class WorkerState:
    tokenizer_name: str
    tokenizer: TokenizerConfig
    processor: Any
    detector: TurkishTokenizer
    selected: list[str]
    piece_size: int
    eos_id: int
    append_eos: bool
    passthrough_routes: set[str]
    byte_offset: int
    piece_to_id: dict[str, int]


@dataclass(frozen=True)
class EncodedLine:
    line_number: int
    text: str
    ids: list[int]
    mask: bytes
    spans_json: list[dict[str, object]]
    raw_bytes: int
    fallback_tokens: int
    masked_tokens: int
    protected_spans: int
    protected_bytes: int
    sp_alignment_mismatch: bool
    max_token_id: int
    route_counts: dict[str, int]


_STATE: WorkerState | None = None


def write_uint32(handle: Any, values: list[int]) -> None:
    data = array("I", values)
    if data.itemsize != 4:
        raise RuntimeError("array('I') is not uint32 on this platform")
    if sys.byteorder != "little":
        data.byteswap()
    data.tofile(handle)


def char_to_byte_offsets(text: str) -> list[int]:
    offsets = [0]
    total = 0
    for char in text:
        total += len(char.encode("utf-8"))
        offsets.append(total)
    return offsets


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
            ids.append(byte_offset + raw_byte)
            spans.append(
                EncodedTokenSpan(
                    token_id=byte_offset + raw_byte,
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
    state: WorkerState,
) -> tuple[list[int], list[EncodedTokenSpan], int]:
    ids: list[int] = []
    spans: list[EncodedTokenSpan] = []
    fallback_tokens = 0
    byte_offsets = char_to_byte_offsets(surface)
    position = 0
    while position < len(surface):
        match = ""
        for piece in state.selected:
            if surface.startswith(piece, position):
                match = piece
                break
        if match:
            token_id = state.piece_to_id[match]
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
            ids.append(state.byte_offset + raw_byte)
            spans.append(
                EncodedTokenSpan(
                    token_id=state.byte_offset + raw_byte,
                    byte_start=base_byte + char_byte_start + offset,
                    byte_end=base_byte + char_byte_start + offset + 1,
                )
            )
        fallback_tokens += len(raw_bytes)
        position += 1
    return ids, spans, fallback_tokens


def init_worker(config_path: str, tokenizer_name: str, append_eos: bool) -> None:
    global _STATE
    tokenizer = find_tokenizer(Path(config_path), tokenizer_name)
    if tokenizer.path is None:
        raise ValueError(f"tokenizer {tokenizer_name!r} has no SP model path")
    processor = load_sp_processor(tokenizer.path)
    selected = selected_piece_strings(tokenizer.selected_pieces) if tokenizer.selected_pieces else []
    piece_size = _processor_piece_size(processor)
    detector = TurkishTokenizer(preserve_whitespace=True)
    passthrough_routes = set(tokenizer.sp_passthrough_routes)
    passthrough_routes.add("numeric_like")
    _STATE = WorkerState(
        tokenizer_name=tokenizer_name,
        tokenizer=tokenizer,
        processor=processor,
        detector=detector,
        selected=selected,
        piece_size=piece_size,
        eos_id=_processor_eos_id(processor),
        append_eos=append_eos,
        passthrough_routes=passthrough_routes,
        byte_offset=piece_size + len(selected),
        piece_to_id={piece: piece_size + index for index, piece in enumerate(selected)},
    )
    if (
        tokenizer.kind != "finite_protected_marker_stripped_numeric_sp"
        or tokenizer.isolate_sp_passthrough_routes
        or tokenizer.byte_fallback_crossing_pieces
        or tokenizer.pre_split_sp_passthrough_routes
    ):
        raise ValueError("production corpus tokenization currently supports passthrough-sidecar configs")


def require_state() -> WorkerState:
    if _STATE is None:
        raise RuntimeError("worker state is not initialized")
    return _STATE


def encode_line_with_state(text: str, state: WorkerState) -> tuple[list[int], list[EncodedTokenSpan], int]:
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
            processor=state.processor,
            text=segment,
            base_byte=segment_start_byte,
            byte_offset=state.byte_offset,
        )
        ids.extend(segment_ids)
        token_spans.extend(segment_spans)
        fallback_tokens += byte_tokens
        segment = ""

    for piece in analyze_line(text, state.detector):
        surface = piece.surface
        surface_bytes = len(surface.encode("utf-8"))
        piece_start_byte = byte_position
        piece_end_byte = piece_start_byte + surface_bytes
        if piece.kind.startswith("protected:"):
            route = piece.kind.removeprefix("protected:")
            if route in state.passthrough_routes:
                if not segment:
                    segment_start_byte = piece_start_byte
                segment += surface
                byte_position = piece_end_byte
                continue
            flush_segment()
            protected_ids, protected_spans_out, byte_tokens = encode_protected_surface_with_offsets(
                surface=surface,
                base_byte=piece_start_byte,
                state=state,
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
    if state.append_eos and state.eos_id >= 0:
        ids.append(state.eos_id)
        token_spans.append(
            EncodedTokenSpan(
                token_id=state.eos_id,
                byte_start=byte_position,
                byte_end=byte_position,
            )
        )
    return ids, token_spans, fallback_tokens


def encode_task(task: tuple[int, str]) -> EncodedLine:
    state = require_state()
    line_number, text = task
    ids, token_spans, fallback_tokens = encode_line_with_state(text, state)
    spans = protected_spans(text, state.detector)
    mask = token_mask_for_line(token_spans=token_spans, spans=spans)
    route_counts = Counter(span.route for span in spans)
    return EncodedLine(
        line_number=line_number,
        text=text,
        ids=ids,
        mask=bytes(mask),
        spans_json=[span_to_json(span) for span in spans],
        raw_bytes=len(text.encode("utf-8")),
        fallback_tokens=fallback_tokens,
        masked_tokens=mask.count(0),
        protected_spans=len(spans),
        protected_bytes=sum(span.byte_len for span in spans),
        sp_alignment_mismatch=len(ids) != len(token_spans),
        max_token_id=max(ids, default=0),
        route_counts=dict(route_counts),
    )


def encode_chunk(tasks: list[tuple[int, str]]) -> list[EncodedLine]:
    return [encode_task(task) for task in tasks]


def iter_line_chunks(path: Path, max_lines: int | None, chunk_lines: int) -> Iterable[list[tuple[int, str]]]:
    chunk: list[tuple[int, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if max_lines is not None and line_number > max_lines:
                break
            chunk.append((line_number, raw_line.rstrip("\n")))
            if len(chunk) >= chunk_lines:
                yield chunk
                chunk = []
    if chunk:
        yield chunk


def update_stats(stats: CorpusStats, encoded: EncodedLine, append_eos: bool) -> None:
    stats.lines += 1
    stats.raw_bytes += encoded.raw_bytes
    stats.tokens += len(encoded.ids)
    stats.eos_tokens += 1 if append_eos else 0
    stats.fallback_tokens += encoded.fallback_tokens
    stats.masked_tokens += encoded.masked_tokens
    stats.protected_spans += encoded.protected_spans
    stats.protected_bytes += encoded.protected_bytes
    stats.sp_alignment_mismatches += 1 if encoded.sp_alignment_mismatch else 0
    stats.max_token_id = max(stats.max_token_id, encoded.max_token_id)
    stats.route_counts.update(encoded.route_counts)


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(block_size)
            if not block:
                break
            hasher.update(block)
    return hasher.hexdigest()


def write_report(
    *,
    input_path: Path,
    out_dir: Path,
    tokenizer_name: str,
    stats: CorpusStats,
    append_eos: bool,
    workers: int,
    chunk_lines: int,
    checksums: dict[str, str],
) -> str:
    route_lines = ["| Route | Spans |", "| --- | ---: |"]
    for route, count in stats.route_counts.most_common():
        route_lines.append(f"| `{route}` | {count} |")
    checksum_lines = ["| File | SHA-256 |", "| --- | --- |"]
    for name, digest in checksums.items():
        checksum_lines.append(f"| `{name}` | `{digest}` |")
    return "\n".join(
        [
            "# Production Corpus Tokenization Report",
            "",
            f"Input: `{input_path.as_posix()}`",
            f"Output dir: `{out_dir.as_posix()}`",
            f"Tokenizer: `{tokenizer_name}`",
            f"Append EOS: `{append_eos}`",
            f"Workers: `{workers}`",
            f"Chunk lines: `{chunk_lines}`",
            "",
            "## Outputs",
            "",
            "| File | Meaning |",
            "| --- | --- |",
            "| `tokens.bin` | Flat little-endian uint32 token ids. |",
            "| `loss_mask.bin` | One uint8 per token: 1=train, 0=masked protected overlap. |",
            "| `index.jsonl` | Per-line token offsets into the flat token stream. |",
            "| `sidecar.jsonl` | Protected span byte/char offsets. |",
            "| `manifest.json` | Machine-readable summary and output paths. |",
            "| `checksums.json` | SHA-256 checksums for produced files. |",
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
            "",
            "## Routes",
            "",
            *route_lines,
            "",
            "## Checksums",
            "",
            *checksum_lines,
            "",
            "## Gate",
            "",
            "- `sp_alignment_mismatches` must be zero before using `loss_mask.bin`",
            "  as a training artifact.",
            "- `checksums.json` should travel with the binary fixture.",
            "- Production serving can port this behavior later; this script is the",
            "  deterministic offline preprocessing path.",
            "",
        ]
    )


def process_chunks(
    *,
    config_path: Path,
    tokenizer_name: str,
    input_path: Path,
    max_lines: int | None,
    append_eos: bool,
    workers: int,
    chunk_lines: int,
) -> Iterable[list[EncodedLine]]:
    chunks = iter_line_chunks(input_path, max_lines, chunk_lines)
    if workers <= 1:
        init_worker(str(config_path), tokenizer_name, append_eos)
        for chunk in chunks:
            yield encode_chunk(chunk)
        return
    context = get_context("spawn")
    with context.Pool(
        processes=workers,
        initializer=init_worker,
        initargs=(str(config_path), tokenizer_name, append_eos),
    ) as pool:
        for encoded_chunk in pool.imap(encode_chunk, chunks, chunksize=1):
            yield encoded_chunk


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def worker_count(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("workers must be >= 0")
    return parsed


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Tokenize a corpus into the v3.x binary handoff format.")
    # No defaults on purpose: a forgotten flag must fail loudly instead of
    # silently selecting a stale tokenizer generation (former default was v3.5).
    parser.add_argument("--config", required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--report-out", required=True)
    parser.add_argument("--max-lines", type=int, default=0, help="Use 0 or negative for all lines.")
    parser.add_argument("--workers", type=worker_count, default=0, help="0 means auto; 1 disables multiprocessing.")
    parser.add_argument("--chunk-lines", type=positive_int, default=256)
    parser.add_argument("--progress", type=int, default=10000)
    parser.add_argument("--append-eos", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    input_path = Path(args.input)
    out_dir = Path(args.out_dir)
    report_out = Path(args.report_out)
    max_lines = normalize_max_lines(args.max_lines)
    workers = args.workers if args.workers else max(1, min((os.cpu_count() or 2) - 1, 8))

    out_dir.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    tokens_path = out_dir / "tokens.bin"
    mask_path = out_dir / "loss_mask.bin"
    index_path = out_dir / "index.jsonl"
    sidecar_path = out_dir / "sidecar.jsonl"
    manifest_path = out_dir / "manifest.json"
    checksums_path = out_dir / "checksums.json"

    stats = CorpusStats()
    token_offset = 0
    with (
        tokens_path.open("wb") as tokens_file,
        mask_path.open("wb") as mask_file,
        index_path.open("w", encoding="utf-8", newline="\n") as index_file,
        sidecar_path.open("w", encoding="utf-8", newline="\n") as sidecar_file,
    ):
        for encoded_chunk in process_chunks(
            config_path=config_path,
            tokenizer_name=args.tokenizer,
            input_path=input_path,
            max_lines=max_lines,
            append_eos=args.append_eos,
            workers=workers,
            chunk_lines=args.chunk_lines,
        ):
            for encoded in encoded_chunk:
                write_uint32(tokens_file, encoded.ids)
                mask_file.write(encoded.mask)
                token_end = token_offset + len(encoded.ids)
                index_file.write(
                    json.dumps(
                        {
                            "line_number": encoded.line_number,
                            "raw_bytes": encoded.raw_bytes,
                            "token_start": token_offset,
                            "token_end": token_end,
                            "token_count": len(encoded.ids),
                            "masked_tokens": encoded.masked_tokens,
                            "fallback_source_tokens": encoded.fallback_tokens,
                            "sidecar_spans": encoded.protected_spans,
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
                            "line_number": encoded.line_number,
                            "raw_bytes": encoded.raw_bytes,
                            "token_start": token_offset,
                            "token_end": token_end,
                            "token_count": len(encoded.ids),
                            "fallback_source_tokens": encoded.fallback_tokens,
                            "spans": encoded.spans_json,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                update_stats(stats, encoded, args.append_eos)
                token_offset = token_end
                if args.progress > 0 and stats.lines % args.progress == 0:
                    print(
                        f"tokenized {stats.lines:,} lines tokens={stats.tokens:,} "
                        f"masked={stats.masked_tokens:,}",
                        flush=True,
                    )

    data_checksums = {
        "tokens.bin": sha256_file(tokens_path),
        "loss_mask.bin": sha256_file(mask_path),
        "index.jsonl": sha256_file(index_path),
        "sidecar.jsonl": sha256_file(sidecar_path),
    }
    manifest = {
        "schema_version": "v3-production-tokenized-corpus-1",
        "tokenizer": args.tokenizer,
        "input": str(input_path),
        "outputs": {
            "tokens": str(tokens_path),
            "loss_mask": str(mask_path),
            "index": str(index_path),
            "sidecar": str(sidecar_path),
            "checksums": str(checksums_path),
        },
        "format": {
            "token_dtype": "uint32_le",
            "loss_mask_dtype": "uint8",
            "loss_mask_values": {"train": 1, "masked": 0},
            "append_eos": args.append_eos,
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
        "checksums": data_checksums,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    checksums = {
        **data_checksums,
        "manifest.json": sha256_file(manifest_path),
    }
    checksums_path.write_text(
        json.dumps({"algorithm": "sha256", "files": checksums}, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    report = write_report(
        input_path=input_path,
        out_dir=out_dir,
        tokenizer_name=args.tokenizer,
        stats=stats,
        append_eos=args.append_eos,
        workers=workers,
        chunk_lines=args.chunk_lines,
        checksums=checksums,
    )
    report_out.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    print(f"wrote_manifest: {manifest_path}")
    print(f"wrote_checksums: {checksums_path}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
