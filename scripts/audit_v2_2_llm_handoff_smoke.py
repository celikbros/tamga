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

from scripts.audit_v2_1_sidecar_operation_simulation import (  # noqa: E402
    OperationStats,
    Span,
    add_masks_to_stats,
    audit_line,
    protected_spans,
)
from scripts.audit_v2_boundary_roundtrip import (  # noqa: E402
    decode_mixed_ids,
    first_diff_index,
)
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    load_sp_processor,
    selected_piece_strings,
)
from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    TokenizerConfig,
    _processor_eos_id,
    _processor_piece_size,
    encode_finite_protected_soft_marker_line_ids,
    load_probe_config,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


DEFAULT_CONFIG = Path("configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml")
DEFAULT_TOKENIZER = "sp64_protected_passthrough_sidecar"
SIDECAR_SCHEMA_VERSION = "v2.2-sidecar-jsonl-1"
REQUIRED_PASSTHROUGH_ROUTES = frozenset({"percent_encoded", "azerbaijani_word"})


@dataclass
class SmokeStats:
    split: str
    lines: int = 0
    exact: int = 0
    failures: int = 0
    decode_errors: int = 0
    invalid_ids: int = 0
    raw_bytes: int = 0
    decoded_bytes: int = 0
    total_tokens: int = 0
    fallback_source_tokens: int = 0
    sidecar_spans: int = 0
    sidecar_surface_failures: int = 0
    sidecar_order_failures: int = 0
    sidecar_offset_failures: int = 0
    lm_tokens_with_eos: int = 0
    operation: OperationStats | None = None

    @property
    def exact_rate(self) -> float:
        return self.exact / self.lines if self.lines else 0.0

    @property
    def tokens_per_byte(self) -> float:
        return self.total_tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def fallback_rate(self) -> float:
        return self.fallback_source_tokens / self.total_tokens if self.total_tokens else 0.0

    @property
    def sidecar_failures(self) -> int:
        return (
            self.sidecar_surface_failures
            + self.sidecar_order_failures
            + self.sidecar_offset_failures
        )


@dataclass
class SmokeResult:
    rows: list[SmokeStats] = field(default_factory=list)
    failure_samples: list[dict[str, object]] = field(default_factory=list)
    sidecar_records: list[dict[str, object]] = field(default_factory=list)

    @property
    def merged(self) -> SmokeStats:
        merged = SmokeStats(split="all")
        operation_rows: list[OperationStats] = []
        for row in self.rows:
            merged.lines += row.lines
            merged.exact += row.exact
            merged.failures += row.failures
            merged.decode_errors += row.decode_errors
            merged.invalid_ids += row.invalid_ids
            merged.raw_bytes += row.raw_bytes
            merged.decoded_bytes += row.decoded_bytes
            merged.total_tokens += row.total_tokens
            merged.fallback_source_tokens += row.fallback_source_tokens
            merged.sidecar_spans += row.sidecar_spans
            merged.sidecar_surface_failures += row.sidecar_surface_failures
            merged.sidecar_order_failures += row.sidecar_order_failures
            merged.sidecar_offset_failures += row.sidecar_offset_failures
            merged.lm_tokens_with_eos += row.lm_tokens_with_eos
            if row.operation is not None:
                operation_rows.append(row.operation)
        if operation_rows:
            merged.operation = merge_operation_stats(operation_rows)
        return merged


def merge_operation_stats(rows: list[OperationStats]) -> OperationStats:
    merged = OperationStats(split="all")
    for row in rows:
        merged.lines += row.lines
        merged.raw_bytes += row.raw_bytes
        merged.protected_spans += row.protected_spans
        merged.protected_bytes += row.protected_bytes
        merged.union_mask_bytes += row.union_mask_bytes
        merged.union_extra_bytes += row.union_extra_bytes
        merged.summed_mask_bytes += row.summed_mask_bytes
        merged.summed_extra_bytes += row.summed_extra_bytes
        merged.crossing_spans += row.crossing_spans
        merged.crossing_tokens += row.crossing_tokens
        merged.edge_aligned_spans += row.edge_aligned_spans
        merged.token_count_sum += row.token_count_sum
        merged.max_extra_bytes = max(merged.max_extra_bytes, row.max_extra_bytes)
        for route, route_stats in row.routes.items():
            target = merged.routes[route]
            target.spans += route_stats.spans
            target.protected_bytes += route_stats.protected_bytes
            target.summed_mask_bytes += route_stats.summed_mask_bytes
            target.summed_extra_bytes += route_stats.summed_extra_bytes
            target.crossing_spans += route_stats.crossing_spans
            target.crossing_tokens += route_stats.crossing_tokens
            target.edge_aligned_spans += route_stats.edge_aligned_spans
            target.token_count_sum += route_stats.token_count_sum
            target.max_extra_bytes = max(target.max_extra_bytes, route_stats.max_extra_bytes)
            target.surfaces.update(route_stats.surfaces)
    return merged


def load_lines(path: Path, max_lines: int | None) -> list[str]:
    lines: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if max_lines is not None and len(lines) >= max_lines:
                break
            lines.append(raw_line.rstrip("\n"))
    return lines


def find_tokenizer(config_path: Path, name: str) -> tuple[TokenizerConfig, Path]:
    probe = load_probe_config(config_path)
    for tokenizer in probe.tokenizers:
        if tokenizer.name == name:
            return tokenizer, probe.split_dir
    raise ValueError(f"tokenizer {name!r} not found in {config_path}")


def validate_sidecar_spans(text: str, spans: list[Span]) -> tuple[int, int, int]:
    raw_bytes = text.encode("utf-8")
    surface_failures = 0
    order_failures = 0
    offset_failures = 0
    previous_end = 0
    for span in spans:
        if (
            span.byte_start < 0
            or span.byte_end < span.byte_start
            or span.byte_end > len(raw_bytes)
            or span.char_start < 0
            or span.char_end < span.char_start
            or span.char_end > len(text)
        ):
            offset_failures += 1
            continue
        if span.byte_start < previous_end:
            order_failures += 1
        previous_end = span.byte_end
        try:
            byte_surface = raw_bytes[span.byte_start : span.byte_end].decode("utf-8")
        except UnicodeDecodeError:
            surface_failures += 1
            continue
        if byte_surface != span.surface or text[span.char_start : span.char_end] != span.surface:
            surface_failures += 1
    return surface_failures, order_failures, offset_failures


def sidecar_record(
    *,
    schema_version: str = SIDECAR_SCHEMA_VERSION,
    tokenizer_name: str = DEFAULT_TOKENIZER,
    split: str,
    line_number: int,
    text: str,
    spans: list[Span],
    token_count: int,
    fallback_source_tokens: int,
) -> dict[str, object]:
    return {
        "schema_version": schema_version,
        "tokenizer": tokenizer_name,
        "split": split,
        "line_number": line_number,
        "raw_bytes": len(text.encode("utf-8")),
        "token_count": token_count,
        "fallback_source_tokens": fallback_source_tokens,
        "spans": [
            {
                "route": span.route,
                "byte_start": span.byte_start,
                "byte_end": span.byte_end,
                "char_start": span.char_start,
                "char_end": span.char_end,
                "surface": span.surface,
            }
            for span in spans
        ],
    }


def encode_ids(
    *,
    text: str,
    config: TokenizerConfig,
    processor: Any,
    selected_pieces: list[str],
    piece_size: int,
) -> tuple[list[int], int]:
    if config.kind != "finite_protected_marker_stripped_numeric_sp":
        raise ValueError(
            "v3 handoff smoke currently expects finite_protected_marker_stripped_numeric_sp"
        )
    return encode_finite_protected_soft_marker_line_ids(
        text,
        processor=processor,
        selected_pieces=selected_pieces,
        protected_piece_offset=piece_size,
        insert_soft_markers=False,
        numeric_sp_passthrough=True,
        sp_passthrough_routes=config.sp_passthrough_routes,
        isolate_sp_passthrough_routes=config.isolate_sp_passthrough_routes,
        byte_fallback_crossing_pieces=config.byte_fallback_crossing_pieces,
        pre_split_sp_passthrough_routes=config.pre_split_sp_passthrough_routes,
    )


def audit_lines(
    *,
    split: str,
    lines: list[str],
    config: TokenizerConfig,
    processor: Any,
    selected_pieces: list[str],
    piece_size: int,
    vocab_size: int,
    batch_size: int,
    seq_len: int,
    progress: int,
    sample_limit: int,
    result: SmokeResult,
) -> SmokeStats:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    eos_id = _processor_eos_id(processor)
    stats = SmokeStats(split=split, operation=OperationStats(split=split))
    assert stats.operation is not None

    for index, text in enumerate(lines, start=1):
        ids, fallback_tokens = encode_ids(
            text=text,
            config=config,
            processor=processor,
            selected_pieces=selected_pieces,
            piece_size=piece_size,
        )
        decoded = ""
        reason = "mismatch"
        try:
            decoded = decode_mixed_ids(
                ids,
                processor=processor,
                selected_pieces=selected_pieces,
                protected_piece_offset=piece_size,
            )
        except Exception as exc:  # pragma: no cover - defensive, reported in smoke output
            reason = f"decode_error:{type(exc).__name__}"
            stats.decode_errors += 1

        raw_bytes = len(text.encode("utf-8"))
        stats.lines += 1
        stats.raw_bytes += raw_bytes
        stats.decoded_bytes += len(decoded.encode("utf-8"))
        stats.total_tokens += len(ids)
        stats.fallback_source_tokens += fallback_tokens
        if eos_id >= 0:
            stats.lm_tokens_with_eos += len(ids) + 1
        else:
            stats.lm_tokens_with_eos += len(ids)
        stats.invalid_ids += sum(1 for token_id in ids if token_id < 0 or token_id >= vocab_size)

        spans = protected_spans(text, tokenizer)
        stats.sidecar_spans += len(spans)
        surface_failures, order_failures, offset_failures = validate_sidecar_spans(text, spans)
        stats.sidecar_surface_failures += surface_failures
        stats.sidecar_order_failures += order_failures
        stats.sidecar_offset_failures += offset_failures
        result.sidecar_records.append(
            sidecar_record(
                split=split,
                tokenizer_name=config.name,
                line_number=index,
                text=text,
                spans=spans,
                token_count=len(ids),
                fallback_source_tokens=fallback_tokens,
            )
        )

        masks, protected_union_bytes, mask_union_bytes = audit_line(
            text=text,
            processor=processor,
            tokenizer=tokenizer,
        )
        add_masks_to_stats(
            stats.operation,
            masks=masks,
            protected_union_bytes=protected_union_bytes,
            mask_union_bytes=mask_union_bytes,
        )
        stats.operation.lines += 1
        stats.operation.raw_bytes += raw_bytes

        if decoded == text:
            stats.exact += 1
        else:
            stats.failures += 1
            if len(result.failure_samples) < sample_limit:
                result.failure_samples.append(
                    {
                        "split": split,
                        "line_number": index,
                        "reason": reason,
                        "first_diff": first_diff_index(text, decoded),
                        "raw_bytes": raw_bytes,
                        "decoded_bytes": len(decoded.encode("utf-8")),
                        "ids_head": ids[:80],
                        "raw": text,
                        "decoded": decoded,
                    }
                )

        if progress > 0 and index % progress == 0:
            windows = stats.lm_tokens_with_eos // (batch_size * seq_len)
            print(
                f"audited {split} {index:,} lines exact={stats.exact:,} "
                f"fallback_rate={stats.fallback_rate:.6f} lm_windows={windows:,}",
                flush=True,
            )

    return stats


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def fmt(value: float) -> str:
    return f"{value:.6f}"


def pass_fail(condition: bool) -> str:
    return "PASS" if condition else "FAIL"


def format_report(
    *,
    config_path: Path,
    tokenizer_name: str,
    input_desc: str,
    result: SmokeResult,
    sidecar_out: Path,
    failures_out: Path,
    vocab_size: int,
    batch_size: int,
    seq_len: int,
    max_fallback_rate: float,
    max_extra_mask_bytes_per_byte: float,
    route_invariant_ok: bool,
    required_routes: frozenset[str] = REQUIRED_PASSTHROUGH_ROUTES,
) -> tuple[str, bool]:
    merged = result.merged
    operation = merged.operation or OperationStats(split="all")
    lm_windows = merged.lm_tokens_with_eos // (batch_size * seq_len)
    gates = [
        ("exact_roundtrip", merged.failures == 0 and merged.decode_errors == 0),
        ("valid_token_ids", merged.invalid_ids == 0),
        ("sidecar_offsets", merged.sidecar_failures == 0),
        ("passthrough_route_invariants", route_invariant_ok),
        ("fallback_rate", merged.fallback_rate <= max_fallback_rate),
        (
            "extra_mask_bytes_per_byte",
            operation.union_extra_bytes_share <= max_extra_mask_bytes_per_byte,
        ),
        ("lm_batch_windows", lm_windows > 0),
    ]
    overall_pass = all(status for _name, status in gates)

    lines = [
        "# v2.2 LLM Handoff Smoke Audit",
        "",
        f"Config: `{config_path.as_posix()}`",
        f"Tokenizer: `{tokenizer_name}`",
        f"Input: `{input_desc}`",
        f"Vocab size: `{vocab_size}`",
        f"Batch smoke shape: `batch_size={batch_size}`, `seq_len={seq_len}`",
        f"Sidecar JSONL: `{sidecar_out.as_posix()}`",
        f"Private failure samples: `{failures_out.as_posix()}`",
        "",
        "This audit is a handoff-hardening smoke test for the future v3.0",
        "experimental tokenizer candidate. It checks exact decode, sidecar byte offsets, token id ranges,",
        "fallback pressure, conservative protected-span masking overhead, and",
        "whether the emitted token stream can form at least one LM batch window.",
        "",
        "## Gate Summary",
        "",
        "| Gate | Status |",
        "| --- | --- |",
    ]
    for name, status in gates:
        lines.append(f"| `{name}` | {pass_fail(status)} |")
    lines.extend(
        [
            f"| `overall` | {pass_fail(overall_pass)} |",
            "",
            "## Split Summary",
            "",
            "| Split | Lines | Raw bytes | Tokens | Tokens/raw byte | Fallback source tokens | Fallback rate | Exact | Failures | Sidecar spans | Sidecar failures | Extra mask bytes/raw byte | LM windows |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in result.rows:
        op = row.operation or OperationStats(split=row.split)
        windows = row.lm_tokens_with_eos // (batch_size * seq_len)
        lines.append(
            f"| `{row.split}` | {row.lines} | {row.raw_bytes} | {row.total_tokens} | "
            f"{fmt(row.tokens_per_byte)} | {row.fallback_source_tokens} | "
            f"{fmt(row.fallback_rate)} | {row.exact} | {row.failures} | "
            f"{row.sidecar_spans} | {row.sidecar_failures} | "
            f"{fmt(op.union_extra_bytes_share)} | {windows} |"
        )
    if len(result.rows) > 1:
        lines.append(
            f"| `all` | {merged.lines} | {merged.raw_bytes} | {merged.total_tokens} | "
            f"{fmt(merged.tokens_per_byte)} | {merged.fallback_source_tokens} | "
            f"{fmt(merged.fallback_rate)} | {merged.exact} | {merged.failures} | "
            f"{merged.sidecar_spans} | {merged.sidecar_failures} | "
            f"{fmt(operation.union_extra_bytes_share)} | {lm_windows} |"
        )

    lines.extend(
        [
            "",
            "## Protected Operation Summary",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| protected spans | {operation.protected_spans} |",
            f"| protected bytes/raw byte | {fmt(operation.protected_bytes_share)} |",
            f"| conservative mask bytes | {operation.union_mask_bytes} |",
            f"| extra mask bytes | {operation.union_extra_bytes} |",
            f"| extra mask bytes/raw byte | {fmt(operation.union_extra_bytes_share)} |",
            f"| extra/protected byte | {fmt(operation.union_extra_per_protected_byte)} |",
            f"| edge-aligned span rate | {fmt(operation.edge_aligned_rate)} |",
            f"| crossing span rate | {fmt(operation.crossing_span_rate)} |",
            f"| max extra bytes/span | {operation.max_extra_bytes} |",
            "",
            "## Sidecar Schema Smoke",
            "",
            "The sidecar JSONL emitted by this smoke contains one record per audited",
            "line. Each record contains:",
            "",
            "```text",
            "schema_version",
            "tokenizer",
            "split",
            "line_number",
            "raw_bytes",
            "token_count",
            "fallback_source_tokens",
            "spans[]: route, byte_start, byte_end, char_start, char_end, surface",
            "```",
            "",
            "For each span, this audit verifies that byte and character offsets slice",
            "back to the recorded surface.",
            "",
            "## Thresholds",
            "",
            "| Threshold | Value |",
            "| --- | ---: |",
            f"| max fallback rate | {fmt(max_fallback_rate)} |",
            f"| max extra mask bytes/raw byte | {fmt(max_extra_mask_bytes_per_byte)} |",
            "",
            "## Interpretation",
            "",
        ]
    )
    if overall_pass:
        lines.extend(
            [
                "The v2.2 handoff smoke passed for this input. This does not make",
                "the tokenizer a v3.0 release yet, but it is strong enough for",
                "LLM-team integration smoke testing preparation.",
            ]
        )
    else:
        lines.extend(
            [
                "The v2.2 handoff smoke failed. Do not hand this tokenizer to the",
                "LLM team until the failing gates are fixed and rerun.",
            ]
        )
    return "\n".join(lines) + "\n", overall_pass


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run v2.2 LLM handoff smoke audit.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--tokenizer", default=DEFAULT_TOKENIZER)
    parser.add_argument("--split-dir")
    parser.add_argument("--split", action="append", choices=["train", "valid", "test"])
    parser.add_argument("--input", action="append")
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--sample-limit", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--seq-len", type=int, default=128)
    parser.add_argument("--max-fallback-rate", type=float, default=0.001)
    parser.add_argument("--max-extra-mask-bytes-per-byte", type=float, default=0.01)
    parser.add_argument(
        "--sidecar-out",
        default="artifacts/private/v2_2_llm_handoff_smoke.sidecar.jsonl",
    )
    parser.add_argument(
        "--failures-out",
        default="artifacts/private/v2_2_llm_handoff_smoke.failures.jsonl",
    )
    parser.add_argument("--report-out", default="artifacts/v2_2_llm_handoff_smoke.md")
    args = parser.parse_args(argv)

    if args.max_lines is not None and args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")
    if args.batch_size <= 0 or args.seq_len <= 0:
        raise ValueError("--batch-size and --seq-len must be positive")
    if args.sample_limit < 0:
        raise ValueError("--sample-limit must be non-negative")

    config_path = Path(args.config)
    tokenizer_config, config_split_dir = find_tokenizer(config_path, args.tokenizer)
    split_dir = Path(args.split_dir) if args.split_dir else config_split_dir
    if tokenizer_config.path is None:
        raise ValueError(f"tokenizer {tokenizer_config.name} requires a model path")
    processor = load_sp_processor(tokenizer_config.path)
    selected = (
        selected_piece_strings(tokenizer_config.selected_pieces)
        if tokenizer_config.selected_pieces is not None
        else []
    )
    piece_size = _processor_piece_size(processor)
    vocab_size = piece_size + len(selected) + 256
    route_invariant_ok = REQUIRED_PASSTHROUGH_ROUTES.issubset(
        tokenizer_config.sp_passthrough_routes
    )

    input_parts: list[str] = []
    split_inputs: list[tuple[str, list[str]]] = []
    if args.split_dir or args.split:
        for split in args.split or ["valid", "test"]:
            path = split_dir / f"{split}.txt"
            input_parts.append(path.as_posix())
            split_inputs.append((split, load_lines(path, args.max_lines)))
    for raw_input in args.input or []:
        path = Path(raw_input)
        input_parts.append(path.as_posix())
        split_inputs.append((path.stem, load_lines(path, args.max_lines)))
    if not split_inputs:
        for split in ["valid", "test"]:
            path = split_dir / f"{split}.txt"
            input_parts.append(path.as_posix())
            split_inputs.append((split, load_lines(path, args.max_lines)))

    result = SmokeResult()
    for split, lines in split_inputs:
        stats = audit_lines(
            split=split,
            lines=lines,
            config=tokenizer_config,
            processor=processor,
            selected_pieces=selected,
            piece_size=piece_size,
            vocab_size=vocab_size,
            batch_size=args.batch_size,
            seq_len=args.seq_len,
            progress=args.progress,
            sample_limit=args.sample_limit,
            result=result,
        )
        result.rows.append(stats)

    sidecar_out = Path(args.sidecar_out)
    failures_out = Path(args.failures_out)
    write_jsonl(sidecar_out, result.sidecar_records)
    write_jsonl(failures_out, result.failure_samples[: args.sample_limit])
    report, ok = format_report(
        config_path=config_path,
        tokenizer_name=args.tokenizer,
        input_desc=", ".join(input_parts),
        result=result,
        sidecar_out=sidecar_out,
        failures_out=failures_out,
        vocab_size=vocab_size,
        batch_size=args.batch_size,
        seq_len=args.seq_len,
        max_fallback_rate=args.max_fallback_rate,
        max_extra_mask_bytes_per_byte=args.max_extra_mask_bytes_per_byte,
        route_invariant_ok=route_invariant_ok,
        required_routes=REQUIRED_PASSTHROUGH_ROUTES,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    print(f"wrote_sidecar: {sidecar_out}")
    print(f"wrote_failures: {failures_out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
