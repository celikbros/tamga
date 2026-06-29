from __future__ import annotations

from dataclasses import dataclass, field
import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    BoundaryBiasedVocab,
    TokenizerConfig,
    _processor_eos_id,
    _processor_piece_size,
    encode_boundary_biased_unigram_line_ids,
    encode_finite_protected_soft_marker_line_ids,
    load_probe_config,
)
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    load_sp_processor,
    selected_piece_strings,
)


@dataclass
class RoundtripFailure:
    line_number: int
    raw_bytes: int
    decoded_bytes: int
    raw_chars: int
    decoded_chars: int
    first_diff: int | None
    reason: str


@dataclass
class RoundtripStats:
    tokenizer: str
    lines: int = 0
    exact: int = 0
    failures: int = 0
    decode_errors: int = 0
    raw_bytes: int = 0
    decoded_bytes: int = 0
    total_tokens: int = 0
    samples: list[RoundtripFailure] = field(default_factory=list)

    @property
    def exact_rate(self) -> float:
        return self.exact / self.lines if self.lines else 0.0

    @property
    def tokens_per_raw_byte(self) -> float:
        return self.total_tokens / self.raw_bytes if self.raw_bytes else 0.0


def first_diff_index(left: str, right: str) -> int | None:
    for index, (left_char, right_char) in enumerate(zip(left, right)):
        if left_char != right_char:
            return index
    if len(left) != len(right):
        return min(len(left), len(right))
    return None


def load_split_lines(split_dir: Path, split: str) -> list[str]:
    path = split_dir / f"{split}.txt"
    if not path.exists():
        raise FileNotFoundError(path)
    return [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines()]


def decode_mixed_ids(
    ids: list[int],
    *,
    processor: Any,
    selected_pieces: list[str],
    protected_piece_offset: int,
) -> str:
    piece_size = _processor_piece_size(processor)
    byte_offset = protected_piece_offset + len(selected_pieces)
    output: list[str] = []
    byte_buffer = bytearray()
    at_start = True

    def flush_bytes() -> None:
        nonlocal at_start
        if byte_buffer:
            decoded = bytes(byte_buffer).decode("utf-8")
            output.append(decoded)
            if decoded:
                at_start = False
            byte_buffer.clear()

    def processor_piece(token_id: int) -> str:
        if hasattr(processor, "IdToPiece"):
            return str(processor.IdToPiece(token_id))
        return str(processor.id_to_piece(token_id))

    def append_sp_piece(token_id: int) -> None:
        nonlocal at_start
        flush_bytes()
        piece = processor_piece(token_id)
        if piece in {"<s>", "</s>"}:
            return
        text = piece.replace("▁", " ")
        # SentencePiece inserts a dummy prefix at the start of normal text. When
        # SP ids are interleaved with byte fallback ids, chunk-level DecodeIds()
        # drops real later spaces, so decode the piece stream directly and strip
        # only the initial dummy prefix.
        if at_start and text.startswith(" "):
            text = text[1:]
        output.append(text)
        if text:
            at_start = False

    for token_id in ids:
        if 0 <= token_id < piece_size:
            if token_id == _processor_eos_id(processor):
                continue
            append_sp_piece(token_id)
            continue

        if protected_piece_offset <= token_id < byte_offset:
            flush_bytes()
            piece = selected_pieces[token_id - protected_piece_offset]
            output.append(piece)
            if piece:
                at_start = False
        elif byte_offset <= token_id < byte_offset + 256:
            byte_buffer.append(token_id - byte_offset)
        else:
            flush_bytes()
            invalid = f"<INVALID:{token_id}>"
            output.append(invalid)
            at_start = False

    flush_bytes()
    return "".join(output)


def encode_line(
    text: str,
    *,
    config: TokenizerConfig,
    processor: Any,
    selected_pieces: list[str],
    boundary_vocab: BoundaryBiasedVocab | None,
) -> list[int]:
    piece_size = _processor_piece_size(processor)
    if config.kind == "boundary_biased_unigram_numeric_sp":
        if boundary_vocab is None:
            raise ValueError("boundary-biased tokenizer requires boundary vocab")
        ids, _byte_tokens = encode_boundary_biased_unigram_line_ids(
            text,
            processor=processor,
            boundary_vocab=boundary_vocab,
            selected_pieces=selected_pieces,
            protected_piece_offset=piece_size,
            boundary_lambda=config.boundary_lambda,
            numeric_sp_passthrough=True,
        )
        return ids

    if config.kind in {
        "finite_protected_marker_stripped",
        "finite_protected_marker_stripped_numeric_sp",
    }:
        ids, _byte_tokens = encode_finite_protected_soft_marker_line_ids(
            text,
            processor=processor,
            selected_pieces=selected_pieces,
            protected_piece_offset=piece_size,
            insert_soft_markers=False,
            numeric_sp_passthrough=(
                config.kind == "finite_protected_marker_stripped_numeric_sp"
            ),
            sp_passthrough_routes=config.sp_passthrough_routes,
            isolate_sp_passthrough_routes=config.isolate_sp_passthrough_routes,
            byte_fallback_crossing_pieces=config.byte_fallback_crossing_pieces,
            pre_split_sp_passthrough_routes=config.pre_split_sp_passthrough_routes,
        )
        return ids

    if config.kind == "sentencepiece":
        if hasattr(processor, "EncodeAsIds"):
            return [int(item) for item in processor.EncodeAsIds(text)]
        return [int(item) for item in processor.encode(text, out_type=int)]

    raise ValueError(f"unsupported tokenizer kind for roundtrip audit: {config.kind}")


def audit_tokenizer(
    *,
    config: TokenizerConfig,
    lines: list[str],
    max_lines: int | None,
    sample_limit: int,
    progress: int,
) -> tuple[RoundtripStats, list[dict[str, Any]]]:
    if config.path is None:
        raise ValueError(f"tokenizer {config.name} requires model path")
    processor = load_sp_processor(config.path)
    selected = (
        selected_piece_strings(config.selected_pieces)
        if config.selected_pieces is not None
        else []
    )
    boundary_vocab = (
        BoundaryBiasedVocab.from_vocab_file(config.vocab_path)
        if config.vocab_path is not None
        else None
    )
    piece_size = _processor_piece_size(processor)
    stats = RoundtripStats(tokenizer=config.name)
    private_samples: list[dict[str, Any]] = []
    limit = len(lines) if max_lines is None else min(max_lines, len(lines))

    for index, raw in enumerate(lines[:limit], start=1):
        ids = encode_line(
            raw,
            config=config,
            processor=processor,
            selected_pieces=selected,
            boundary_vocab=boundary_vocab,
        )
        stats.lines += 1
        stats.raw_bytes += len(raw.encode("utf-8"))
        stats.total_tokens += len(ids)
        try:
            if config.kind == "sentencepiece":
                if hasattr(processor, "DecodeIds"):
                    decoded = str(processor.DecodeIds(ids))
                else:
                    decoded = str(processor.decode(ids))
            else:
                decoded = decode_mixed_ids(
                    ids,
                    processor=processor,
                    selected_pieces=selected,
                    protected_piece_offset=piece_size,
                )
        except Exception as exc:
            decoded = ""
            reason = f"decode_error:{type(exc).__name__}"
            stats.decode_errors += 1
        else:
            reason = "mismatch"

        stats.decoded_bytes += len(decoded.encode("utf-8"))
        if decoded == raw:
            stats.exact += 1
        else:
            stats.failures += 1
            failure = RoundtripFailure(
                line_number=index,
                raw_bytes=len(raw.encode("utf-8")),
                decoded_bytes=len(decoded.encode("utf-8")),
                raw_chars=len(raw),
                decoded_chars=len(decoded),
                first_diff=first_diff_index(raw, decoded),
                reason=reason,
            )
            if len(stats.samples) < sample_limit:
                stats.samples.append(failure)
            if len(private_samples) < sample_limit:
                private_samples.append(
                    {
                        "line_number": index,
                        "raw": raw,
                        "decoded": decoded,
                        "ids_head": ids[:80],
                        "first_diff": failure.first_diff,
                        "reason": failure.reason,
                    }
                )
        if progress > 0 and index % progress == 0:
            print(
                f"{config.name}: checked {index:,} lines exact={stats.exact:,} "
                f"failures={stats.failures:,}",
                flush=True,
            )

    return stats, private_samples


def format_report(
    *,
    config_path: Path,
    split_dir: Path,
    split: str,
    stats_rows: list[RoundtripStats],
    private_out: Path | None,
) -> str:
    lines = [
        "# v2.0 Boundary Encoder Roundtrip Audit",
        "",
        f"Config: `{config_path.as_posix()}`",
        f"Split dir: `{split_dir.as_posix()}`",
        f"Split: `{split}`",
        "",
        "This audit checks whether tokenizer IDs decode back to the exact raw",
        "line text. Public samples omit raw text; private samples, when written,",
        "are stored separately.",
        "",
        "## Summary",
        "",
        "| Tokenizer | Lines | Exact | Failures | Decode errors | Exact rate | Tokens/raw byte | Raw bytes | Decoded bytes |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in stats_rows:
        lines.append(
            f"| {row.tokenizer} | {row.lines} | {row.exact} | {row.failures} | "
            f"{row.decode_errors} | {row.exact_rate:.6f} | "
            f"{row.tokens_per_raw_byte:.6f} | {row.raw_bytes} | {row.decoded_bytes} |"
        )

    lines.extend(["", "## Failure Samples", ""])
    for row in stats_rows:
        lines.extend([f"### {row.tokenizer}", ""])
        if not row.samples:
            lines.append("No failures.")
            lines.append("")
            continue
        for sample in row.samples:
            lines.extend(
                [
                    f"- line `{sample.line_number}` reason `{sample.reason}`",
                    f"  - raw bytes/chars: `{sample.raw_bytes}` / `{sample.raw_chars}`",
                    f"  - decoded bytes/chars: `{sample.decoded_bytes}` / `{sample.decoded_chars}`",
                    f"  - first diff index: `{sample.first_diff}`",
                ]
            )
        lines.append("")

    if private_out is not None:
        lines.extend(
            [
                "## Private Samples",
                "",
                f"Private failure samples: `{private_out.as_posix()}`",
                "",
            ]
        )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Audit exact roundtrip for v2.0 boundary/protected encoders."
    )
    parser.add_argument("config")
    parser.add_argument("--tokenizer", action="append", default=[])
    parser.add_argument("--split", default="valid", choices=("train", "valid", "test"))
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--sample-limit", type=int, default=10)
    parser.add_argument("--progress", type=int, default=0)
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_boundary_encoder_roundtrip_audit.md",
    )
    parser.add_argument(
        "--private-out",
        default="artifacts/private/v2_0_boundary_encoder_roundtrip_audit_failures.jsonl",
    )
    args = parser.parse_args(argv)

    probe = load_probe_config(args.config)
    selected_names = set(args.tokenizer)
    if selected_names:
        tokenizers = [item for item in probe.tokenizers if item.name in selected_names]
        unknown = selected_names - {item.name for item in tokenizers}
        if unknown:
            raise ValueError(f"unknown tokenizer name(s): {', '.join(sorted(unknown))}")
    else:
        tokenizers = [
            item
            for item in probe.tokenizers
            if item.kind
            in {
                "sentencepiece",
                "finite_protected_marker_stripped",
                "finite_protected_marker_stripped_numeric_sp",
                "boundary_biased_unigram_numeric_sp",
            }
        ]

    lines = load_split_lines(probe.split_dir, args.split)
    all_stats: list[RoundtripStats] = []
    all_private: list[dict[str, Any]] = []
    for tokenizer in tokenizers:
        print(f"Auditing tokenizer={tokenizer.name}", flush=True)
        stats, private_samples = audit_tokenizer(
            config=tokenizer,
            lines=lines,
            max_lines=args.max_lines,
            sample_limit=args.sample_limit,
            progress=args.progress,
        )
        all_stats.append(stats)
        all_private.extend(
            {"tokenizer": tokenizer.name, **sample} for sample in private_samples
        )

    report_out = Path(args.report_out)
    private_out = Path(args.private_out) if args.private_out else None
    if private_out is not None:
        private_out.parent.mkdir(parents=True, exist_ok=True)
        with private_out.open("w", encoding="utf-8") as handle:
            for sample in all_private:
                handle.write(json.dumps(sample, ensure_ascii=False) + "\n")

    report = format_report(
        config_path=Path(args.config),
        split_dir=probe.split_dir,
        split=args.split,
        stats_rows=all_stats,
        private_out=private_out,
    )
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    if private_out is not None:
        print(f"wrote_private: {private_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
