from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.run_tiny_lm_bpb_probe import load_sp_processor  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class Span:
    route: str
    surface: str
    char_start: int
    char_end: int
    byte_start: int
    byte_end: int

    @property
    def byte_len(self) -> int:
        return self.byte_end - self.byte_start


@dataclass(frozen=True)
class TokenPiece:
    piece: str
    char_start: int
    char_end: int
    byte_start: int
    byte_end: int

    @property
    def byte_len(self) -> int:
        return self.byte_end - self.byte_start


@dataclass(frozen=True)
class SpanMask:
    span: Span
    token_count: int
    mask_start: int
    mask_end: int
    left_extra_bytes: int
    right_extra_bytes: int
    crossing_tokens: int
    edge_aligned: bool

    @property
    def mask_bytes(self) -> int:
        return self.mask_end - self.mask_start

    @property
    def extra_bytes(self) -> int:
        return self.left_extra_bytes + self.right_extra_bytes

    @property
    def has_crossing(self) -> bool:
        return self.crossing_tokens > 0


@dataclass
class RouteStats:
    spans: int = 0
    protected_bytes: int = 0
    summed_mask_bytes: int = 0
    summed_extra_bytes: int = 0
    crossing_spans: int = 0
    crossing_tokens: int = 0
    edge_aligned_spans: int = 0
    token_count_sum: int = 0
    max_extra_bytes: int = 0
    surfaces: Counter[str] = field(default_factory=Counter)

    @property
    def extra_per_protected_byte(self) -> float:
        return self.summed_extra_bytes / self.protected_bytes if self.protected_bytes else 0.0

    @property
    def edge_aligned_rate(self) -> float:
        return self.edge_aligned_spans / self.spans if self.spans else 1.0

    @property
    def crossing_span_rate(self) -> float:
        return self.crossing_spans / self.spans if self.spans else 0.0

    @property
    def avg_tokens_per_span(self) -> float:
        return self.token_count_sum / self.spans if self.spans else 0.0


@dataclass
class OperationStats:
    split: str
    lines: int = 0
    raw_bytes: int = 0
    protected_spans: int = 0
    protected_bytes: int = 0
    union_mask_bytes: int = 0
    union_extra_bytes: int = 0
    summed_mask_bytes: int = 0
    summed_extra_bytes: int = 0
    crossing_spans: int = 0
    crossing_tokens: int = 0
    edge_aligned_spans: int = 0
    token_count_sum: int = 0
    max_extra_bytes: int = 0
    routes: dict[str, RouteStats] = field(default_factory=lambda: defaultdict(RouteStats))

    @property
    def protected_bytes_share(self) -> float:
        return self.protected_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def union_mask_bytes_share(self) -> float:
        return self.union_mask_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def union_extra_bytes_share(self) -> float:
        return self.union_extra_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def union_extra_per_protected_byte(self) -> float:
        return self.union_extra_bytes / self.protected_bytes if self.protected_bytes else 0.0

    @property
    def summed_extra_per_protected_byte(self) -> float:
        return self.summed_extra_bytes / self.protected_bytes if self.protected_bytes else 0.0

    @property
    def edge_aligned_rate(self) -> float:
        return self.edge_aligned_spans / self.protected_spans if self.protected_spans else 1.0

    @property
    def crossing_span_rate(self) -> float:
        return self.crossing_spans / self.protected_spans if self.protected_spans else 0.0

    @property
    def avg_tokens_per_span(self) -> float:
        return self.token_count_sum / self.protected_spans if self.protected_spans else 0.0


def char_to_byte_offsets(text: str) -> list[int]:
    offsets = [0]
    total = 0
    for char in text:
        total += len(char.encode("utf-8"))
        offsets.append(total)
    return offsets


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    ordered = sorted(intervals)
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def interval_bytes(intervals: list[tuple[int, int]]) -> int:
    return sum(max(0, end - start) for start, end in intervals)


def protected_spans(text: str, tokenizer: TurkishTokenizer) -> list[Span]:
    byte_offsets = char_to_byte_offsets(text)
    spans: list[Span] = []
    char_offset = 0
    for piece in analyze_line(text, tokenizer):
        start = char_offset
        end = start + len(piece.surface)
        if piece.kind.startswith("protected:"):
            spans.append(
                Span(
                    route=piece.kind.removeprefix("protected:"),
                    surface=piece.surface,
                    char_start=start,
                    char_end=end,
                    byte_start=byte_offsets[start],
                    byte_end=byte_offsets[end],
                )
            )
        char_offset = end
    if char_offset != len(text):
        raise ValueError("analyze_line surfaces did not reconstruct input")
    return spans


def sp_token_pieces(processor: Any, text: str) -> list[TokenPiece]:
    byte_offsets = char_to_byte_offsets(text)
    pieces: list[TokenPiece] = []
    proto = processor.EncodeAsImmutableProto(text)
    for piece in proto.pieces:
        begin = int(piece.begin)
        end = int(piece.end)
        if begin == end:
            continue
        pieces.append(
            TokenPiece(
                piece=str(piece.piece),
                char_start=begin,
                char_end=end,
                byte_start=byte_offsets[begin],
                byte_end=byte_offsets[end],
            )
        )
    return pieces


def span_mask(span: Span, tokens: list[TokenPiece]) -> SpanMask | None:
    overlapping = [
        token
        for token in tokens
        if token.byte_start < span.byte_end and span.byte_start < token.byte_end
    ]
    if not overlapping:
        return None
    mask_start = min(token.byte_start for token in overlapping)
    mask_end = max(token.byte_end for token in overlapping)
    crossing_tokens = sum(
        1
        for token in overlapping
        if (
            token.byte_start < span.byte_start < token.byte_end
            or token.byte_start < span.byte_end < token.byte_end
        )
    )
    token_edges = {edge for token in tokens for edge in (token.byte_start, token.byte_end)}
    return SpanMask(
        span=span,
        token_count=len(overlapping),
        mask_start=mask_start,
        mask_end=mask_end,
        left_extra_bytes=max(0, span.byte_start - mask_start),
        right_extra_bytes=max(0, mask_end - span.byte_end),
        crossing_tokens=crossing_tokens,
        edge_aligned=span.byte_start in token_edges and span.byte_end in token_edges,
    )


def update_route_stats(route_stats: RouteStats, mask: SpanMask) -> None:
    route_stats.spans += 1
    route_stats.protected_bytes += mask.span.byte_len
    route_stats.summed_mask_bytes += mask.mask_bytes
    route_stats.summed_extra_bytes += mask.extra_bytes
    route_stats.crossing_tokens += mask.crossing_tokens
    route_stats.token_count_sum += mask.token_count
    route_stats.max_extra_bytes = max(route_stats.max_extra_bytes, mask.extra_bytes)
    route_stats.surfaces[mask.span.surface] += 1
    if mask.has_crossing:
        route_stats.crossing_spans += 1
    if mask.edge_aligned:
        route_stats.edge_aligned_spans += 1


def audit_line(
    *,
    text: str,
    processor: Any,
    tokenizer: TurkishTokenizer,
) -> tuple[list[SpanMask], int, int]:
    spans = protected_spans(text, tokenizer)
    tokens = sp_token_pieces(processor, text)
    masks = [mask for span in spans if (mask := span_mask(span, tokens)) is not None]
    protected_union = merge_intervals([(span.byte_start, span.byte_end) for span in spans])
    mask_union = merge_intervals([(mask.mask_start, mask.mask_end) for mask in masks])
    protected_union_bytes = interval_bytes(protected_union)
    mask_union_bytes = interval_bytes(mask_union)
    return masks, protected_union_bytes, mask_union_bytes


def add_masks_to_stats(
    stats: OperationStats,
    *,
    masks: list[SpanMask],
    protected_union_bytes: int,
    mask_union_bytes: int,
) -> None:
    stats.protected_spans += len(masks)
    stats.protected_bytes += sum(mask.span.byte_len for mask in masks)
    stats.union_mask_bytes += mask_union_bytes
    stats.union_extra_bytes += max(0, mask_union_bytes - protected_union_bytes)
    for mask in masks:
        stats.summed_mask_bytes += mask.mask_bytes
        stats.summed_extra_bytes += mask.extra_bytes
        stats.crossing_tokens += mask.crossing_tokens
        stats.token_count_sum += mask.token_count
        stats.max_extra_bytes = max(stats.max_extra_bytes, mask.extra_bytes)
        if mask.has_crossing:
            stats.crossing_spans += 1
        if mask.edge_aligned:
            stats.edge_aligned_spans += 1
        update_route_stats(stats.routes[mask.span.route], mask)


def audit_path(
    *,
    path: Path,
    split: str,
    processor: Any,
    max_lines: int | None,
    progress: int,
    sample_limit: int,
) -> tuple[OperationStats, list[dict[str, object]]]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    stats = OperationStats(split=split)
    samples: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            if max_lines is not None and stats.lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            stats.lines += 1
            stats.raw_bytes += len(text.encode("utf-8"))
            masks, protected_union_bytes, mask_union_bytes = audit_line(
                text=text,
                processor=processor,
                tokenizer=tokenizer,
            )
            add_masks_to_stats(
                stats,
                masks=masks,
                protected_union_bytes=protected_union_bytes,
                mask_union_bytes=mask_union_bytes,
            )
            for mask in sorted(masks, key=lambda item: item.extra_bytes, reverse=True):
                if len(samples) >= sample_limit or mask.extra_bytes == 0:
                    break
                samples.append(
                    {
                        "split": split,
                        "line_no": line_no,
                        "route": mask.span.route,
                        "surface": mask.span.surface,
                        "span_byte_start": mask.span.byte_start,
                        "span_byte_end": mask.span.byte_end,
                        "mask_byte_start": mask.mask_start,
                        "mask_byte_end": mask.mask_end,
                        "left_extra_bytes": mask.left_extra_bytes,
                        "right_extra_bytes": mask.right_extra_bytes,
                        "extra_bytes": mask.extra_bytes,
                        "token_count": mask.token_count,
                        "crossing_tokens": mask.crossing_tokens,
                        "edge_aligned": mask.edge_aligned,
                        "text": text,
                    }
                )
            if progress > 0 and stats.lines % progress == 0:
                print(
                    f"audited {split} {stats.lines:,} lines "
                    f"extra_mask_bytes={stats.union_extra_bytes:,}",
                    flush=True,
                )
    return stats, samples


def merge_stats(rows: list[OperationStats]) -> OperationStats:
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


def _fmt(value: float) -> str:
    return f"{value:.6f}"


def _stats_row(stats: OperationStats) -> str:
    return (
        f"| `{stats.split}` | {stats.lines} | {stats.raw_bytes} | "
        f"{stats.protected_spans} | {stats.protected_bytes} | "
        f"{_fmt(stats.protected_bytes_share)} | {stats.union_mask_bytes} | "
        f"{stats.union_extra_bytes} | {_fmt(stats.union_extra_bytes_share)} | "
        f"{_fmt(stats.union_extra_per_protected_byte)} | "
        f"{_fmt(stats.edge_aligned_rate)} | {_fmt(stats.crossing_span_rate)} | "
        f"{_fmt(stats.avg_tokens_per_span)} | {stats.max_extra_bytes} |"
    )


def format_report(
    *,
    input_desc: str,
    sp_model: Path,
    rows: list[OperationStats],
    max_lines: int | None,
    samples_out: Path,
) -> str:
    merged = merge_stats(rows)
    output = [
        "# v2.1 Passthrough Sidecar Operation Simulation",
        "",
        f"Input: `{input_desc}`",
        f"SP model: `{sp_model.as_posix()}`",
        f"Max lines per split/file: `{max_lines if max_lines is not None else 'all'}`",
        f"Private worst-case samples: `{samples_out.as_posix()}`",
        "",
        "This audit simulates a downstream training-mask operation for the",
        "`sp64_protected_passthrough_sidecar` contract. Protected spans are exact",
        "byte ranges in the sidecar, while model tokens may straddle span edges.",
        "The safe token-index policy maps each protected byte span to every",
        "overlapping SP token, conservatively over-masking boundary tokens.",
        "",
        "## Split Summary",
        "",
        "| Split | Lines | Raw bytes | Protected spans | Protected bytes | Protected bytes/raw byte | Conservative mask bytes | Extra mask bytes | Extra mask bytes/raw byte | Extra/protected byte | Edge-aligned span rate | Crossing span rate | Avg tokens/span | Max extra bytes/span |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        output.append(_stats_row(row))
    if len(rows) > 1:
        output.append(_stats_row(merged))

    output.extend(
        [
            "",
            "## Route Summary",
            "",
            "| Route | Spans | Protected bytes | Summed extra bytes | Extra/protected byte | Edge-aligned span rate | Crossing span rate | Avg tokens/span | Max extra bytes/span | Top surfaces |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for route, stats in sorted(
        merged.routes.items(),
        key=lambda item: item[1].summed_extra_bytes,
        reverse=True,
    ):
        top = ", ".join(
            f"`{surface}`:{count}" for surface, count in stats.surfaces.most_common(8)
        )
        output.append(
            f"| `{route}` | {stats.spans} | {stats.protected_bytes} | "
            f"{stats.summed_extra_bytes} | {_fmt(stats.extra_per_protected_byte)} | "
            f"{_fmt(stats.edge_aligned_rate)} | {_fmt(stats.crossing_span_rate)} | "
            f"{_fmt(stats.avg_tokens_per_span)} | {stats.max_extra_bytes} | {top} |"
        )

    output.extend(
        [
            "",
            "## Gate",
            "",
            "Use this audit to decide whether byte-span metadata is operationally",
            "safe enough for training-time masking/redaction workflows.",
            "",
            "- `Extra mask bytes/raw byte` estimates the global data lost by",
            "  conservative token over-masking.",
            "- High route-specific `Extra/protected byte` suggests selective",
            "  pre-splitting for that route class before considering global",
            "  pre-splitting.",
            "- This does not test exact constrained decoding/copy. If that becomes a",
            "  base-model requirement, use a pre-split or route-selective aligned",
            "  variant.",
        ]
    )
    return "\n".join(output) + "\n"


def write_samples(path: Path, samples: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Simulate downstream token masking for v2.1 passthrough sidecar."
    )
    parser.add_argument("--split-dir", help="Directory containing train.txt/valid.txt/test.txt.")
    parser.add_argument("--input", action="append", help="Standalone UTF-8 text file.")
    parser.add_argument("--split", action="append", choices=["train", "valid", "test"])
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument("--sample-limit", type=int, default=100)
    parser.add_argument(
        "--samples-out",
        default="artifacts/private/v2_1_sidecar_operation_simulation.samples.jsonl",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_1_sidecar_operation_simulation.md",
    )
    args = parser.parse_args(argv)

    if not args.split_dir and not args.input:
        raise ValueError("Provide --split-dir or at least one --input file.")
    if args.max_lines is not None and args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")
    if args.sample_limit < 0:
        raise ValueError("--sample-limit must be non-negative")

    processor = load_sp_processor(Path(args.sp_model))
    rows: list[OperationStats] = []
    samples: list[dict[str, object]] = []
    input_parts: list[str] = []

    if args.split_dir:
        split_dir = Path(args.split_dir)
        input_parts.append(split_dir.as_posix())
        for split in args.split or ["valid", "test"]:
            stats, split_samples = audit_path(
                path=split_dir / f"{split}.txt",
                split=split,
                processor=processor,
                max_lines=args.max_lines,
                progress=args.progress,
                sample_limit=max(0, args.sample_limit - len(samples)),
            )
            rows.append(stats)
            samples.extend(split_samples)

    for raw_path in args.input or []:
        path = Path(raw_path)
        input_parts.append(path.as_posix())
        stats, path_samples = audit_path(
            path=path,
            split=path.stem,
            processor=processor,
            max_lines=args.max_lines,
            progress=args.progress,
            sample_limit=max(0, args.sample_limit - len(samples)),
        )
        rows.append(stats)
        samples.extend(path_samples)

    samples_out = Path(args.samples_out)
    write_samples(samples_out, samples[: args.sample_limit])
    report = format_report(
        input_desc=", ".join(input_parts),
        sp_model=Path(args.sp_model),
        rows=rows,
        max_lines=args.max_lines,
        samples_out=samples_out,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    print(f"wrote_samples: {samples_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
